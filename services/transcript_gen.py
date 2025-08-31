import os
import time
import tempfile
import subprocess
import yt_dlp
import whisper
import logging

logger = logging.getLogger(__name__)

class TranscriptGen:
    def __init__(self, model_size: str = "tiny"):
        self.model = whisper.load_model(model_size)

    def generate_transcript(self, youtube_url: str) -> str:
        start_time = time.time()

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Download audio
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(tmpdir, 'audio.%(ext)s'),
                    'quiet': True,
                    'postprocessors': [],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(youtube_url, download=True)
                    audio_file = ydl.prepare_filename(info_dict)

                # Crop first 3 minutes, convert to mono, 16kHz
                cropped_audio_file = os.path.join(tmpdir, "audio_3min.wav")
                subprocess.run([
                    "ffmpeg", "-y", "-i", audio_file,
                    "-t", "180", "-ac", "1", "-ar", "16000", cropped_audio_file
                ], check=True)

                # Transcribe
                result = self.model.transcribe(cropped_audio_file)
                transcript = result.get('text', '')

        except Exception as e:
            logger.error(f"Failed to generate transcript: {e}")
            transcript = ""

        end_time = time.time()
        logger.info(f"Transcript generated in {end_time - start_time:.2f} seconds")
        return transcript
