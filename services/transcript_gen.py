import os
import time
import tempfile
import subprocess
import yt_dlp
import whisper
import logging
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger(__name__)

class TranscriptGen:
    def __init__(self, model_size: str = "tiny"):
        self.model = whisper.load_model(model_size)

    def generate_transcript(self, youtube_url: str) -> str:
        start_time = time.time()

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Download audio with proper output suppression
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(tmpdir, 'audio.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'postprocessors': [],
                    # Additional options to suppress output
                    'noprogress': True,
                    'no_color': True,
                }

                # Capture all stdout/stderr to prevent contamination
                captured_output = StringIO()
                captured_errors = StringIO()
                
                with redirect_stdout(captured_output), redirect_stderr(captured_errors):
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(youtube_url, download=True)
                        audio_file = ydl.prepare_filename(info_dict)

                # Crop first 3 minutes, convert to mono, 16kHz
                cropped_audio_file = os.path.join(tmpdir, "audio_3min.wav")
                
                # Run ffmpeg with output suppression
                with open(os.devnull, 'w') as devnull:
                    subprocess.run([
                        "ffmpeg", "-y", "-i", audio_file,
                        "-t", "90", "-ac", "1", "-ar", "16000", cropped_audio_file
                    ], check=True, stdout=devnull, stderr=devnull)

                # Transcribe (Whisper might also output to stdout)
                with redirect_stdout(captured_output), redirect_stderr(captured_errors):
                    result = self.model.transcribe(cropped_audio_file)
                    transcript = result.get('text', '')

        except Exception as e:
            logger.error(f"Failed to generate transcript: {e}")
            transcript = ""

        end_time = time.time()
        logger.info(f"Transcript generated in {end_time - start_time:.2f} seconds")
        return transcript