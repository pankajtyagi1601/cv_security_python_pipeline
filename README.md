# CV Security — Python Pipeline

> Real-time AI-powered access control system. Detects and identifies faces from live camera feeds, classifies them as authorized or intruder, streams annotated video to a web dashboard, and logs every security event — all without restarting the pipeline.

![Python](https://img.shields.io/badge/Python-3.10-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green) ![Redis](https://img.shields.io/badge/Redis-Upstash-red) ![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)

---

## Repository Structure

```
cv_security_python_pipeline/
├── backend/              # Production Python pipeline
├── dashboard/            # Next.js dashboard (git submodule)
└── prototype_code_work/  # Early experiments and learning scripts
```

The `dashboard/` folder is a git submodule pointing to
**[pankajtyagi1601/cv_security_dashboard](https://github.com/pankajtyagi1601/cv_security_dashboard)**.

The `prototype_code_work/` folder contains scripts written while learning OpenCV,
face_recognition, and threading concepts before the production system was built.
Not required to run the system.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Next.js Dashboard                       │
│   Auth · Events · Live Feed · Enroll · Cameras · Admins  │
└───────────────┬─────────────────────────┬────────────────┘
                │ MongoDB Atlas            │ Upstash Redis
                │ (shared database)        │ (message broker)
┌───────────────▼─────────────────────────▼────────────────┐
│                   Python Pipeline                          │
│                                                            │
│  Redis Subscribers                                         │
│  ├── enrollment_subscriber  → enrollment + reload signals  │
│  └── camera_subscriber      → add/remove camera signals   │
│                                                            │
│  Camera Threads (one per camera, spawned dynamically)      │
│  └── cap.read() → resize → HOG detect → encode → compare  │
│       └── event_queue.put()                                │
│                                                            │
│  Event Worker                                              │
│  └── Cloudinary upload → MongoDB log                       │
│                                                            │
│  Flask MJPEG Stream (port 5000)                            │
│  └── FrameBuffer → annotated JPEG → browser <img> tag     │
└────────────────────────────────────────────────────────────┘
```

---

## How It Works

### Camera Pipeline
Each camera runs in its own Python thread. Frames are read continuously,
resized to 60% for performance, and passed through the HOG face detector
every 2nd frame. Detected faces are encoded into 128-dimensional vectors
and compared against known encodings loaded from MongoDB. Matches below a
distance of 0.5 are AUTHORIZED — everything else is UNKNOWN.

### Producer-Consumer Event Queue
Camera threads are fast producers running at ~30fps. Cloudinary uploads
are slow consumers taking 1-3 seconds. A thread-safe `Queue` decouples
them — camera threads drop events into the queue and immediately return
to reading frames. The event worker processes one event at a time with
exponential backoff retry on upload failure.

### Redis Pub/Sub — Zero Polling
Instead of Python polling MongoDB for changes, the dashboard publishes
messages to Redis channels when admin actions happen. Python subscribers
wake up in microseconds.

```
enrollment_channel → new person enrolled OR person deleted
camera_channel     → camera added OR removed
```

### Live MJPEG Stream
A Flask server runs inside the same Python process on port 5000. Camera
threads write annotated JPEG frames to a shared `FrameBuffer` after each
recognition cycle. Flask reads from the buffer and streams frames as a
multipart HTTP response — a plain `<img>` tag in the dashboard displays
the live feed natively with no video libraries needed.

### Hot Reload Without Restart
When a person is enrolled or deleted, the dashboard publishes to Redis.
Python receives the signal, reloads encodings from MongoDB, and clears
stale annotation cache — all within one frame cycle. No restart needed.

When no cameras are running at the time of deletion, a `system_flags`
document in MongoDB marks encodings as dirty. The next camera thread to
start checks this flag and reloads before processing its first frame.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Face Detection | `face_recognition` + dlib HOG | CPU-friendly, no GPU required |
| Video Capture | OpenCV | Supports webcam, RTSP, HTTP streams |
| Live Streaming | Flask MJPEG | Single `<img>` tag, no JS video library |
| Thread Safety | `threading.Lock` | dlib is not thread-safe on Windows |
| Message Broker | Redis (Upstash) | Zero-polling pub/sub, no extra server |
| Image Storage | Cloudinary | Permanent URLs, accessible from both services |
| Database | MongoDB Atlas | Shared between Python and Next.js |
| Logging | Python `logging` | Daily rotating log files |

---

## Backend Structure

```
backend/
├── main.py                           # Entry point
├── config.py                         # Constants + env validation
├── requirements.txt
│
├── camera/
│   ├── camera_manager.py             # Spawn/stop threads, track active cameras
│   ├── camera_stream.py              # Frame loop, HOG, annotation, buffer write
│   └── camera_subscriber.py         # Redis → add/remove camera live
│
├── enrollment/
│   ├── enrollment_processor.py       # Download → encode → save to DB
│   ├── enrollment_subscriber.py      # Redis → enrollment + reload signals
│   └── enrollment_pending_recover.py # Process jobs interrupted by crash
│
├── events/
│   ├── event_queue.py                # Shared thread-safe Queue
│   └── event_worker.py              # Cloudinary upload + MongoDB log
│
├── recognition/
│   └── face_recognizer.py            # HOG detect, encode, compare, dlib lock
│
├── streaming/
│   ├── frame_buffer.py               # Thread-safe in-memory frame store
│   └── stream_server.py             # Flask MJPEG server on port 5000
│
├── messaging/
│   └── redis_client.py              # Shared Redis connection
│
├── storage/
│   ├── database.py                   # All MongoDB operations
│   └── cloudinary_upload.py         # Upload with retry
│
└── utils/
    └── logger.py                     # Daily rotating log files → logs/
```

---

## Setup

### Prerequisites

- Python 3.9+
- MongoDB Atlas account (free tier works)
- Upstash Redis account (free tier works)
- Cloudinary account (free tier works)

---

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/pankajtyagi1601/cv_security_python_pipeline.git
cd cv_security_python_pipeline/backend
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Windows note:** `face_recognition` requires `dlib`. If pip fails, install
> the prebuilt wheel first matching your Python version:
> ```bash
> # Python 3.10
> pip install https://github.com/jloh02/dlib/releases/download/v19.22/dlib-19.22.0-cp310-cp310-win_amd64.whl
> pip install face-recognition
> ```
> Check your version with `python --version`.

---

### 3. Environment variables

Create `backend/.env`:

```env
# MongoDB Atlas
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/cv_security

# Upstash Redis — must use rediss:// (with SSL)
REDIS_URL=rediss://default:password@your-instance.upstash.io:6379

# Cloudinary
CLOUD_NAME=your_cloud_name
API_KEY=your_api_key
API_SECRET=your_api_secret
```

---

### 4. Run

```bash
python main.py
```

Expected startup output:
```
========================================
  CV Security — Starting up
========================================
Event worker started
[Enrollment] Subscriber thread started
[Camera] Subscriber thread started.
[Stream] Server started on http://0.0.0.0:5000
========================================
  All systems running
========================================
```

---

### 5. Add cameras from the dashboard

Cameras are not hardcoded — add them from the Next.js dashboard Cameras tab.
The pipeline spawns a new thread instantly via Redis signal.

| Source type | Example |
|---|---|
| Local webcam | `0` or `1` |
| IP camera RTSP | `rtsp://192.168.1.100:554/stream` |
| Phone — DroidCam | `http://192.168.1.x:4747/video` |
| Phone — IP Webcam | `http://192.168.1.x:8080/video` |

---

### 6. Enroll an authorized person

From the dashboard → **Enroll Person** → upload a clear solo face photo.
The pipeline encodes the face and cameras recognize the person within
seconds — no restart required.

---

## MongoDB Indexes

Run once in MongoDB Atlas shell for optimal query performance:

```javascript
db.events.createIndex({ timestamp: -1 })
db.events.createIndex({ event_type: 1, timestamp: -1 })
db.authorized_people.createIndex({ name: 1 }, { unique: true })
db.cameras.createIndex({ camera_id: 1 }, { unique: true })
db.enrollment_jobs.createIndex({ status: 1 })
```

---

## Key Design Decisions

**Why Redis instead of FastAPI?**
The original design used FastAPI as a bridge between Next.js and Python.
Replaced with Redis Pub/Sub — Next.js publishes directly, Python subscribes.
No second server, no extra port, no deployment complexity.

**Why HOG instead of CNN?**
HOG runs on CPU without a GPU. Practical for edge deployment on Jetson Nano
or Raspberry Pi. CNN is more accurate but requires CUDA.

**Why a threading.Lock for dlib?**
On Windows, dlib is not thread-safe. Two threads calling face_recognition
simultaneously causes a C-level segfault — not a Python exception, a hard
process crash. A single Lock shared across all camera threads and the
enrollment processor serializes all dlib calls with ~50ms max wait.

**Why MJPEG instead of WebRTC?**
MJPEG streams over plain HTTP and the browser handles it natively with
a single `<img>` tag. WebRTC requires STUN/TURN servers and peer
negotiation — unnecessary complexity for a one-way stream.

**Why producer-consumer Queue?**
Camera threads run at ~30fps. Cloudinary uploads take 1-3 seconds.
Without a Queue, the camera thread would freeze waiting for each upload.
The Queue decouples speed — cameras never wait, the worker processes
at its own pace without dropping frames.

---

## Environment Variables Reference

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB Atlas connection string |
| `REDIS_URL` | Upstash Redis URL — must start with `rediss://` |
| `CLOUD_NAME` | Cloudinary cloud name |
| `API_KEY` | Cloudinary API key |
| `API_SECRET` | Cloudinary API secret |

---

## Dashboard Repo

**[pankajtyagi1601/cv_security_dashboard](https://github.com/pankajtyagi1601/cv_security_dashboard)**

---

## License

MIT