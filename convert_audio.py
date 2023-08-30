from moviepy.editor import AudioFileClip
from pydub import AudioSegment
import loguru


logger = loguru.logger


def convert_audio(file_path: str) -> str:
    if not file_path:
        raise FileNotFoundError(f"File {file_path} not found.")
    logger.info(f"Checking and converting to audio: {file_path}")
    audio_file_path = ""
    try:
        while not audio_file_path.endswith(".mp3"):
            if file_path.endswith(".wav"):
                file = AudioFileClip(file_path)
                audio_file_path = file_path.split(".")[0] + ".mp3"
                file.write_audiofile(audio_file_path)
                file.close()
                return audio_file_path
            if file_path.endswith(".mp4" or ".mkv"):
                audio = AudioSegment.from_wav(file_path)
                audio_file_path = file_path.split(".")[0] + ".mp3"
                audio.export(audio_file_path, format="mp3")
                audio.close()
                return audio_file_path
            if file_path.endswith(".mp3"):
                return audio_file_path
    except (FileNotFoundError, SystemError, IndexError, ValueError) as error:
        logger.exception(f"Failed to convert file: {error}")
    return "Error could not convert audio"


def check_audio(
    audio_path: str,
) -> str:
    logger.info("Checking Audio Files")
    folder_path = audio_path or "./out/"
    audio_file_path = convert_audio(
        folder_path,
    )
    logger.info("Check complete")
    return audio_file_path
