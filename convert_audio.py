from moviepy.editor import AudioFileClip
from pydub import AudioSegment
from typing import Optional
import loguru


logger = loguru.logger


def convert_audio(file_path: str, temp_path: str) -> str:
    try:
        subprocess.run([
            "ffmpeg", 
            "-i", 
            f"{file_path}", 
            "-ar", 
            "16000", 
            "-ac", 
            "1", 
            "-c:a", 
            "pcm_s16le", 
            f"{temp_path}"
            ])
        return temp_path

    except (FileNotFoundError, SystemError, IndexError, ValueError) as error:
        logger.exception(f"Failed to convert file: {error}")
    return "Error could not convert audio"


def check_audio(
    audio_path: str,
    temp_path: Optional[str]="whipser/temp/temp.wav"
) -> str:
    logger.info("Checking Audio Files")
    
    audio_file_path = convert_audio(
        file_path, temp_path
    )
    logger.info("Check complete")
    return audio_file_path
