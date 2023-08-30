import os
import argparse
from typing import Optional, Tuple
from argparse import Namespace
from convert_audio import check_audio
from segment_audio import split_file
from transcribe_audio import transcribe


def manage_variables(
    input_file: str,
    out_directory: Optional[str],
    model_path: Optional[str],
    chunk_length: int,
) -> Tuple[str, str, str, str, str, int]:
    if not model_path:
        model_path = "./whisper.cpp/models/ggml-model-whisper-large-q5_0.bin"
    model_file_path = model_path
    chunk_length = 10 * 40 * 512
    temp_fold = "./temp/"
    if not out_directory:
        out_directory = "./output/"
    out_dir = out_directory
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    in_file = input_file
    filename = os.path.basename(input_file)
    output_file = f"{os.path.join(out_directory, filename)}.txt"
    return (
        in_file,
        output_file,
        out_dir,
        temp_fold,
        model_file_path,
        chunk_length,
    )


def arge_parser() -> Namespace:
    parser = argparse.ArgumentParser(description="Whisper audio transcriber")
    parser.add_argument("-f", "--file", help="input file path")
    parser.add_argument("-o", "--out", help="output directory")
    parser.add_argument("-m", "--model", help="model path")
    parser.add_argument("-otxt", "--output", help="output file path")
    parser.add_argument("-c", "--chunk_size", help="chunk size in ms")
    return parser.parse_args()


def main(args):
    (
        in_file,
        output_file,
        out_dir,
        temp_fold,
        model_file_path,
        chunk_length,
    ) = manage_variables(
        input_file=args.file,
        out_directory=args.out,
        model_path=args.model,
        chunk_length=args.chunk_sizze,
    )

    wav_file_path = check_audio(audio_path=in_file)
    segmented_audio = split_file(wav_file_path, chunk_length)
    transcription_paths = []
    for audio_segment in segmented_audio:
        transcript = transcribe(
            input_path=audio_segment,
            output_path=output_file,
            model_path=model_file_path,
            temporary_dir=temp_fold,
            output_dir=out_dir,
        )
        transcription_paths.append(transcript)
