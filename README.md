# Audio Splitter

A simple web-based tool to split a single MP3 file into individual tracks based on a pasted tracklist. It tags each split segment with ID3 metadata (artist, album, track title, track number, cover art and release year), and provides download links to single tracks or choosable a set of tracks. All Tracks can be previewed with the integrated Waveform-Player.

---

## 🚀 Features

- **Free-form tracklist parsing**
  Accepts timestamps in formats like `0:00 – Intro`, `00:45 KALT`, `INTRO 0:00`, etc.
- **FastAPI backend**
  - Splits audio using pydub
  - Tags output files with ID3 metadata (Mutagen)
  - Optional cover art embedding
  - CORS enabled for local development
- **Vue.js frontend**
  - Upload form for audio file, tracklist, artist, album, cover image, year
  - Interactive table & modal with waveform previews (WaveSurfer), per-track play/pause
  - Single-track or multi-track ZIP download (JSZip + File-Saver)
  - SCSS-based modern styling, components scoped per Vue file
  - Loading overlay & toast notifications

---

## 📦 Prerequisites

- **Backend**
  - Python 3.10+
  - FFmpeg (in PATH)
- **Frontend**
  - Node.js 14+
  - npm or yarn

---

## 🔧 Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/SoBo7a/audio-splitter.git
   cd audio-splitter
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate      # or .venv\\Scripts\\activate on Windows
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Frontend setup**
   ```bash
   cd ../frontend
   npm install       # or yarn install
   ```

---

## ▶️ Usage

### 1. Run the backend

From `/backend`:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Run the frontend

From `/frontend`:
```bash
npm run serve   # starts at http://localhost:8080 by default
```

> **Tip:** set the `backend` URL in `frontend/.env` if your API runs on a different host/port.

---

## 🛠️ Configuration

- **`backend/requirements.txt`** lists Python dependencies.
- **`frontend/vue.config.js`** (optional) adjust dev server proxy.

---

## 🔌 API Reference

All endpoints under `/api`.

| Method | Path                       | Description                                      |
| ------ | -------------------------- | ------------------------------------------------ |
| POST   | `/api/split`               | Upload files & split → JSON with session/tracks. |
| GET    | `/api/download/{session}/{file}` | Download a single track or cover.             |
| GET    | `/api/download_zip/{session}`   | ZIP of all tracks (and cover).               |

---

## 📂 Project Structure

```
.
├── backend/
│   ├── main.py
│   ├── track_splitter.py
│   ├── logger.py
│   ├── requirements.txt
│   └── temp/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── styles/
│   │   └── main.js
│   ├── package.json
│   └── vue.config.js
└── README.md
```

---

## 🤝 Contributing

1. Fork & create a feature branch:  
   `git checkout -b feat/your-feature`  
2. Commit & push:  
   `git commit -am 'Add feature' && git push origin feat/your-feature`  
3. Open a PR describing your changes.

---

## 📜 License

This project is licensed under the MIT License.
