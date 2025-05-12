import re
import os
import time
from pydub import AudioSegment
from mutagen.id3 import (
    ID3, APIC, TIT2, TPE1, TPE2, TALB, TDRC, TRCK,
    ID3NoHeaderError
)
from custom_logger import logger

TIMESTAMP_PATTERN = re.compile(r"(?:(?P<h>\d+):)?(?P<m>\d+):(?P<s>\d+)")

def sanitize_filename(text: str) -> str:
    safe = re.sub(r'[\\/*?:"<>|]', "", text).strip()
    safe = re.sub(r'^[\s\|\-]+', "", safe)
    return safe

def parse_tracklist(text: str):
    start = time.time()
    logger.debug("parse_tracklist() start")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    tracks = []
    for idx, line in enumerate(lines, start=1):
        m = TIMESTAMP_PATTERN.search(line)
        if not m:
            logger.warning(f"Line {idx} skipped (no timestamp): {line!r}")
            continue
        h = int(m.group("h") or 0)
        m_ = int(m.group("m"))
        s = int(m.group("s"))
        start_ms = ((h*60 + m_) * 60 + s) * 1000
        title = TIMESTAMP_PATTERN.sub("", line).strip(" -")
        title = re.sub(r'^[\s\|\-]+', "", title)
        tracks.append({"title": title or f"Track {len(tracks)+1}", "start_ms": start_ms})
        logger.debug(f"Track {len(tracks)}: title={title!r}, start_ms={start_ms}")

    for i in range(len(tracks)-1):
        tracks[i]["end_ms"] = tracks[i+1]["start_ms"]
    if tracks:
        tracks[-1]["end_ms"] = None

    logger.debug(f"parse_tracklist() end, {len(tracks)} total, took "
                 f"{(time.time()-start)*1000:.1f}ms")
    return tracks

def split_and_tag(
    input_path, output_dir, tracks,
    artist=None, album=None, albumartist=None,
    cover_path=None, year=None,
    bitrate="192k"
):
    total_start = time.time()
    logger.info(f"split_and_tag() loading audio from {input_path!r}")
    audio = AudioSegment.from_file(input_path)
    logger.info(f"Audio duration: {len(audio)/1000:.1f}s")

    output_files = []
    for idx, t in enumerate(tracks, start=1):
        track_start = time.time()
        start_ms  = t["start_ms"]
        end_ms    = t.get("end_ms") or len(audio)
        duration  = (end_ms - start_ms) / 1000
        logger.info(f"Track {idx}: slicing {duration:.1f}s "
                    f"[{start_ms}-{end_ms}]")

        segment = audio[start_ms:end_ms]
        title_raw   = t["title"]
        title_clean = re.sub(r'^[\s\|\-]+', "", title_raw).strip()
        safe_title  = sanitize_filename(title_clean)
        filename    = f"{idx:02d} - {safe_title}.mp3"
        out_path    = os.path.join(output_dir, filename)

        export_start = time.time()
        segment.export(out_path, format="mp3", bitrate=bitrate)
        logger.debug(f"Exported {filename!r} in "
                     f"{(time.time()-export_start)*1000:.1f}ms")

        # ID3 tagging
        tag_start = time.time()
        try:
            try:
                id3 = ID3(out_path)
            except ID3NoHeaderError:
                id3 = ID3()

            if artist:
                id3.add(TPE1(encoding=3, text=artist))
            if albumartist:
                id3.add(TPE2(encoding=3, text=albumartist))
            if album:
                id3.add(TALB(encoding=3, text=album))
            id3.add(TIT2(encoding=3, text=title_clean))
            id3.add(TRCK(encoding=3, text=str(idx)))
            if year:
                id3.add(TDRC(encoding=3, text=str(year)))
            if cover_path and os.path.exists(cover_path):
                ext = os.path.splitext(cover_path)[1].lower().lstrip('.')
                mime = 'image/jpeg' if ext in ('jpg','jpeg') else f'image/{ext}'
                with open(cover_path, 'rb') as img:
                    id3.add(APIC(
                        encoding=3, mime=mime,
                        type=3, desc='Cover',
                        data=img.read()
                    ))
            id3.save(out_path)
            logger.debug(f"Tagged {filename!r} in {(time.time()-tag_start)*1000:.1f}ms")
        except Exception:
            logger.exception(f"Failed to tag {filename!r}")

        output_files.append(filename)

    logger.info(f"split_and_tag() completed {len(output_files)} tracks in "
                f"{(time.time()-total_start)/1:.1f}s")
    return output_files
