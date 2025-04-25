from flask import Flask, render_template, request, send_from_directory, jsonify, Response
import os
import threading
import time
import ffmpeg

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'clips'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

progress = {"percentage": 0}  # Global progress variable

def process_video(video_path):
    """Process video and update progress dynamically."""
    global progress
    total_clips = 0
    clip_duration = 40  # Each short clip is 40 seconds

    # Get video duration using FFmpeg
    probe = ffmpeg.probe(video_path)
    video_duration = float(probe['format']['duration'])
    total_clips = int(video_duration // clip_duration)

    for i in range(total_clips):
        start_time = i * clip_duration
        output_clip = os.path.join(OUTPUT_FOLDER, f'clip_{i+1}.mp4')

        # FFmpeg command to extract 40-second clips
        (
            ffmpeg
            .input(video_path, ss=start_time, t=clip_duration)
            .output(output_clip, codec="copy")
            .run(overwrite_output=True, quiet=True)
        )

        # Update progress
        progress["percentage"] = int(((i + 1) / total_clips) * 100)
        time.sleep(1)  # Simulate delay for visualization

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start processing in a separate thread."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Start video processing in a separate thread
    threading.Thread(target=process_video, args=(file_path,)).start()

    return jsonify({"message": "Processing started!"})

@app.route('/progress')
def get_progress():
    """Send real-time progress updates to frontend."""
    def progress_stream():
        while progress["percentage"] < 100:
            yield f"data: {progress['percentage']}\n\n"
            time.sleep(1)
        yield "data: 100\n\n"

    return Response(progress_stream(), mimetype='text/event-stream')

@app.route('/clips/<filename>')
def download_clip(filename):
    """Serve the generated clips."""
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/get_clips')
def get_clips():
    """Return the list of generated clips."""
    clips = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.mp4')]
    return jsonify({"clips": clips})

if __name__ == '__main__':
    app.run(debug=True)