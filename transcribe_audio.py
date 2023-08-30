import os
import loguru
import subprocess

logger = loguru.logger


def transcribe(
    input_path: str,
    output_path: str,
    temporary_dir: str,
    output_dir: str,
    model_path: str,
) -> str:
    logger.info("Transcribing Audio")
    subprocess.run(
        [
            "./whisper.cpp/main",
            "-f",
            input_path,
            "-m",
            model_path,
            "-otxt",
            output_path,
        ],
        check=True,
    )
    subprocess.run(["rm", "-rf", temporary_dir], check=True)
    subprocess.run(["mv", output_path, output_dir], check=True)
    return output_path
