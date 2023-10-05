import os
import argparse
from path import Path
from typing import Optional, Tuple
from argparse import Namespace
from convert_audio import check_audio
from segment_audio import split_file
from transcribe_audio import transcribe



def arge_parser() -> Namespace:
    parser = argparse.ArgumentParser(description="Whisper audio transcriber")
    parser.add_argument("-f", "--file", help="input file path")
    parser.add_argument("-m", "--model", help="model path")
    parser.add_argument("-otxt", "--output", help="output file path")
    return parser.parse_args()


def main(args):
    
    in_file=args.file or "whisper/in/input.wav",
    out_file=args.output or "whisper/out/output.txt",
    temp_fold=args.temp or "whisper/temp/temp.wav",
    model_file_path=args.model or "whisper/models/ggml-base.en.bin"

    wav_file_path = check_audio(audio_path)
    segmented_audio = split_file(wav_file_path, chunk_length)
    transcription_paths = []
    for audio_segment in segmented_audio:
        transcript = transcribe(
            input_path=audio_segment,
            output_path=output_file,
            model_path=model_file_path,
            output_dir=out_dir,
        )
        transcription_paths.append(transcript)
