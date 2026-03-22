import cv2, time, threading
from flask import Flask, Response, jsonify
from flask_cors import CORS
from streaming.frame_buffer import buffer
from utils.logger import logger

app = Flask(__name__)
CORS(app) #allows Next.js to call this

def generate_frames(camera_id: str):
    """Generator function - yields JPEG frames forever.
    
    This is the heart of MJPEG streaming.
    Flask keeps the HTTP connection open and calls next() on this generator continuously - each yield sends one frame
    to the browser.
    """
    
    logger.info(f"[Stream] Client connected to {camera_id}")
    
    while True:
        frame_bytes = buffer.get(camera_id)
        
        if frame_bytes is None:
            # Camera not active yet - send a blank frame so the browser doesn't show broken image
            time.sleep(0.1)
            continue
        
        # MJPEG frame format - browser expects exactly this structure
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes +
            b"\r\n"
        )
        
        # -30fps cap - don't burn CPU sending faster than camera produce
        time.sleep(1 / 30)
        
@app.route("/video_feed/<camera_id>")
def video_feed(camera_id: str):
    """
    Browser hits this URL with a plain <img> tag.
    Returns a never-ending HTTP response containing JPEG frames.
    """
    return Response(
        generate_frames(camera_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
    
@app.route("/cameras")
def active_cameras():
    """Returns list of all camera currently streaming - dashboard uses this"""
    return jsonify({"cameras": buffer.get_all_ids()})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

def start_stream_server(host="0.0.0.0", port=5000):
    """Run Flask in its own daemon thread so it doesn't block main.py"""
    thread = threading.Thread(
        target=lambda: app.run(
            host=host,
            port=port,
            debug=False,        # must be False — debug mode conflicts with threading
            threaded=True,      # handle multiple camera streams simultaneously
            use_reloader=False  # must be False — reloader conflicts with our threads
        ),
        daemon=True
    )
    
    thread.start()
    logger.info(f"[Stream] Server started on http://{host}:{port}")