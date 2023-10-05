import os
import loguru
import subprocess
from datetime import datetime

logger = loguru.logger

date_time = datetime.now().strftime("%Y%m%d_%H%M%S")

def transcribe(
    input_path: Optional[str]="whisper/temp/temp.wav",,
    output_path: Optional[str]=f"whisper/out/{date_time_}output.txt",
    model_path: Optional[str]="whisper/models/ggml-base.en.bin",
    whisper_path: Optional[str]="./whisper/main",
) -> str:
    logger.info("Transcribing Audio")
    subprocess.run(
        [
            "",
            "-f",
            input_path,
            "-m",
            model_path,
            "-otxt",
            output_path,
            "-oved",
            "TPU",
            "-p",
            "8",
            "-pc",
            "-nt"            
        ],
        check=True,
    )
    subprocess.run(["rm", input_path], check=True)
    return output_path


def stream():
    subprocess.run(["./stream", "-m", "./models/ggml-base.en.bin", "-t", "6", "--step", "0", "--length", "30000", "-vth", "0.6"], check=True)
    
    # build using Emscripten (v3.1.2)
mkdir build-em && cd build-em
emcmake cmake ..
make -j

# copy the produced page to your HTTP path
cp bin/stream.wasm/*       localhost:8888
cp bin/libstream.worker.js localhost:8888