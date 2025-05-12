import os
import shutil
import uuid
import time
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from track_splitter import parse_tracklist, split_and_tag
from custom_logger import logger

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

BASE_DIR = os.path.dirname(__file__)
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)


@app.on_event("startup")
async def on_startup():
    logger.info("Application startup complete")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(f"-> {request.method} {request.url.path}")
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(f"<- {request.method} {request.url.path} completed in {duration:.1f}ms "
                f"status={response.status_code}")
    return response


def cleanup_temp():
    """
    Remove any subfolder of TEMP_DIR older than 6 hours.
    """
    cutoff = time.time() - 6 * 3600
    for name in os.listdir(TEMP_DIR):
        path = os.path.join(TEMP_DIR, name)
        if os.path.isdir(path):
            try:
                mtime = os.path.getmtime(path)
                if mtime < cutoff:
                    shutil.rmtree(path)
                    logger.info(f"Removed old temp folder: {name}")
            except Exception:
                logger.exception(f"Failed to remove temp folder: {name}")


@app.post("/api/split")
async def split(
    file: UploadFile = File(...),
    cover: Optional[UploadFile] = File(None),
    tracklist: str = Form(...),
    artist: Optional[str] = Form(None),
    album: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
):
    logger.info("=== Begin split request ===")
    start_all = time.time()

    cleanup_temp()

    logger.info(f"Parameters: artist={artist!r}, album={album!r}, year={year!r}, "
                f"filename={file.filename!r}")

    # 1) create session directory
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    logger.debug(f"Created session directory: {session_dir}")

    # 2) save uploaded audio
    audio_start = time.time()
    input_path = os.path.join(session_dir, file.filename)
    with open(input_path, "wb") as out:
        shutil.copyfileobj(file.file, out)
    size = os.path.getsize(input_path)
    logger.info(f"Saved audio to {input_path!r} ({size//1024} KB) in "
                f"{(time.time()-audio_start)*1000:.1f}ms")

    # 3) save cover image if provided
    cover_path = None
    if cover:
        cover_start = time.time()
        ext = os.path.splitext(cover.filename)[1]
        cover_filename = f"cover{ext}"
        cover_path = os.path.join(session_dir, cover_filename)
        with open(cover_path, "wb") as out:
            shutil.copyfileobj(cover.file, out)
        logger.info(f"Saved cover to {cover_path!r} in "
                    f"{(time.time()-cover_start)*1000:.1f}ms")

    # 4) parse tracklist
    parse_start = time.time()
    tracks = parse_tracklist(tracklist)
    logger.info(f"parse_tracklist returned {len(tracks)} tracks in "
                f"{(time.time()-parse_start)*1000:.1f}ms")

    # 5) split & tag
    split_start = time.time()
    output_files = split_and_tag(
        input_path,
        session_dir,
        tracks,
        artist=artist,
        album=album,
        albumartist=artist,
        cover_path=cover_path,
        year=year
    )
    logger.info(f"split_and_tag created {len(output_files)} files in "
                f"{(time.time()-split_start)*1000:.1f}ms")

    # 6) build response
    prefix = f"/api/download/{session_id}/"
    track_objs = []
    for fn in output_files:
        display = fn.split(" - ", 1)[1] if " - " in fn else fn
        track_objs.append({
            "title": display.replace(".mp3", ""),
            "path": prefix + fn
        })

    response = {"session": session_id, "tracks": track_objs}
    if album:
        response["album"] = album
    if cover and cover_path:
        response["cover"] = prefix + os.path.basename(cover_path)
    if year:
        response["year"] = year

    logger.info(f"Returning response for session {session_id} in "
                f"{(time.time()-start_all)*1000:.1f}ms")
    logger.info("=== End split request ===")
    return JSONResponse(response)


@app.get("/api/download/{session}/{filename}")
def download_track(session: str, filename: str):
    path = os.path.join(TEMP_DIR, session, filename)
    logger.info(f"Download track request: {path!r}")
    return FileResponse(path, media_type="audio/mpeg", filename=filename)


@app.get("/api/download_zip/{session}")
def download_zip(session: str):
    zip_path = os.path.join(TEMP_DIR, f"{session}.zip")
    session_dir = os.path.join(TEMP_DIR, session)
    logger.info(f"Creating zip for session {session!r}")
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', session_dir)
    logger.info(f"Serving zip: {zip_path!r}")
    return FileResponse(zip_path, media_type="application/zip", filename=f"{session}.zip")


if __name__ == "__main__":
    import uvicorn
    logger.info("Launching via __main__ (uvicorn.run)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
