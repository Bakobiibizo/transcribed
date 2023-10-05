from dotenv import dotenv_values, set_key
import os
from getpass import getpass

# Load existing .env if it exists
env_file_path = ".env"
env_data = dotenv_values(dotenv_path=env_file_path)

def get_input_for_key(key):
    return getpass(f"Enter your {key}: ")

# Collect new values
keys = ["HUGGINGFACE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DOCKER_BUILDKIT"]
for key in keys:
    if key == "DOCKER_BUILDKIT":
        "DOCKER_BUILDKIT"="1"
        set_key(env_file_path, key, "")
    new_value = get_input_for_key(key)
    set_key(env_file_path, key, new_value)

build_sh = """
# build.sh
#!/bin/bash

# Export variables from .env to the shell
export $(grep -v '^#' .env | xargs)

# Build Docker image
docker build --build-arg $HUGGINGFACE_API_KEY --build-arg $OPENAI_API_KEY --build-arg $ANTHROPIC_API_KEY -t .

print("Configuration saved to .env")
"""
build_path = "build.sh"

run_sh="""
#! /bin/bash
sudo docker run --rm -it -v $(pwd):/app/server -p 8888:8888 python:3.8-slim bash
"""
run_path = "run.sh"

docker_file = """
FROM gcr.io/tpu-pytorch/xla:nightly
WORKDIR /root

# Installs Tensorflow to resolve the TPU name to IP Address
RUN pip install tensorflow

# Installs google cloud sdk, this is mostly for using gsutil to    
# export the model.
RUN wget -nv \\
    https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz && \\
    mkdir /root/tools && \\
    tar xvzf google-cloud-sdk.tar.gz -C /root/tools && \\
    rm google-cloud-sdk.tar.gz && \\
    /root/tools/google-cloud-sdk/install.sh --usage-reporting=false \\
    --path-update=false --bash-completion=false \\
    --disable-installation-options && \\
    rm -rf /root/.config/* && \\
    ln -s /root/.config /config && \\
    # Remove the backup directory that gcloud creates
    rm -rf /root/tools/google-cloud-sdk/.install/.backup

# Path configuration
ENV PATH $PATH:/root/tools/google-cloud-sdk/bin

# Make sure gsutil will use the default service account
RUN echo '[GoogleCompute]\\nservice_account = default' > /etc/boto.cfg

# Set work directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Use ARG for build-time variables
ARG HUGGINGFACE_API_KEY
ARG OPENAI_API_KEY
ARG ANTHROPIC_API_KEY

# Use ENV for runtime variables
ENV HUGGINGFACE_API_KEY=$HUGGINGFACE_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# Install packages
RUN python install.py

# Change the below to your exec. Make sure you chmod +x the script first
ENTRYPOINT ["sh", "run.sh"]
"""
docker_path = "Dockerfile"

install_sh = """#!/bin/bash

# Install CMake, gcc, g++ and other build essentials

sudo apt update
sudo apt upgrade -y

sudo apt dist-upgrade -y

sudo apt install python3-dev

sudo apt python-is-python3 -y

sudo apt install build-essential -y

echo installed build essentials

# Install git
if command -v git &> /dev/null
    then sudo apt install git -y
    echo installed git
fi

git lfs install
pip install --upgrade huggingface_hub

huggingface-cli lfs-enable-largefiles .

# Check virtual environment
if file ~/.pyenv/bin/ &> /dev/null]; then
    curl https://pyenv.run | bash

    pyenv install 3.10.13
    pyenv global 3.10.13
    echo installed pyenv
fi
pyenv local 3.10.13
echo activated local pyenv

if file ~/.local/bin/poetry &> /dev/null]; then
    curl -sSL https://install.python-poetry.org | python3 -
    echo installed poetry
fi
poetry shell
echo activate poetry

# upgrade pip
python -m pip install --upgrade pip
echo updated pip

# install notebook resources
pip install testresources
pip install wheel setuptools
pip install jupyter lab
echo installed jupyter resources

# install requirements.txt
poetry install
echo installed requirements

# Install ffmpeg
sudo apt install ffmpeg -y
echo installed ffmpeg

# Install zlib
sudo apt-get install zlib1g -y
echo installed zlib

# Create a symbolic link for CUDA
sudo ln -sf /sbin/ldconfig.real /usr/lib/wsl/lib/libcuda.so.1
echo created symbolic link

# Delete the 7fa2af80 key
sudo apt-key del 7fa2af80
echo deleted 7fa2af80 key

# Download and Install CUDA
# This is setup for CUDA 12.2 on ubuntu 20.04. Do not install this on a different operating system. Go to this site to get the correct cuda version: https://developer.nvidia.com/cuda-downloads

# download pin for keyring
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
echo downloaded and moved pin


# Check if the local installer is already downloaded if not download it
if command -v nvcc &> /dev/null
    then
        wget https://developer.download.nvidia.com/compute/cuda/12.2.2/local_installers/cuda-repo-ubuntu2004-12-2-local_12.2.2-535.104.05-1_amd64.deb
fi

# Install CUDA
if file cuda-repo-ubuntu2004-12-2-local_12.2.2-535.104.05-1_amd64.deb &> /dev/null]; then
    sudo dpkg -i cuda-repo-ubuntu2004-12-2-local_12.2.2-535.104.05-1_amd64.deb
    sudo cp /var/cuda-repo-ubuntu2004-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/
    sudo apt-get update
    sudo apt-get -y install cuda
    echo installed cuda
fi

# install libsdl2
sudo apt-get install libsdl2-dev
echo installed libsdl2

# Install CLBlast
curl https://github.com/CNugteren/CLBlast/releases/download/1.6.1/CLBlast-1.6.1-windows-x64.zip -o CLBlast-1.6.1-windows-x64.zip
echo installed CLBlast

# Install PyTorch.
if command python -c "import torch; print(torch.cuda.is_available())" ; then
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    echo installed PyTorch
fi

# Check if CUDA is available
if python -c "import torch; print(torch.cuda.is_available())" ; then
    nvidia-smi
    echo "CUDA is available"
else
    echo "CUDA is not available. Instillation failed"
fi

if file ./whisper/ &> /dev/null; then
    git clone git@github.com:ggerganov/whisper.cpp.git
    mv whisper.cpp whipser
    cd whisper

    CMake:
    cd whisper.cpp
    cmake -B build -DWHISPER_CLBLAST=ON
    cmake --build build -j --config Release
    cd ..
    
    make samples
    make tiny.en
    make tiny
    make base.en
    make base
    make small.en
    make small
    make medium.en
    make medium
    make large-v1
    make large
    bash livestream.sh
    
    make stream
    
fi


if command -v nvm &> /dev/nulll; then
    wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
    echo installed nvm
fi

if command -v npm &> /dev/nulll; then
    nvm install 18
    nvm use 18
    echo installed npm
fi

if command -v pm2 &> /dev/nulll; then
    pm2 install pm2-logrotate
    echo installed pm2
fi

if command -v ngrok &> /dev/nulll; then
    ngrok authtoken $NGROK_TOKEN
    echo installed ngrok
fi

# Update repositories
sudo apt update -y
echo updated repositories

# clean up apt
sudo apt auto remove -y
echo cleaned up apt

# Start ngrok
node pm2 start "npm run ngrok http 8888"
echo started pm2 with ngrok on port 8888

# start server
uvicorn app.main:app --host localhost --port 8888
echo started server on port 8888

echo instilation complete

EOF
"""
livestream_sh = """
#!/bin/bash
#
# Transcribe audio livestream by feeding ffmpeg output to whisper.cpp at regular intervals
# Idea by @semiformal-net
# ref: https://github.com/ggerganov/whisper.cpp/issues/185
#

set -eo pipefail

url="http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_world_service.m3u8"
fmt=aac # the audio format extension of the stream (TODO: auto detect)
step_s=30
model="base.en"

check_requirements()
{
    if ! command -v ./main &>/dev/null; then
        echo "whisper.cpp main executable is required (make)"
        exit 1
    fi

    if ! command -v ffmpeg &>/dev/null; then
        echo "ffmpeg is required (https://ffmpeg.org)"
        exit 1
    fi
}

check_requirements


if [ -z "$1" ]; then
    echo "Usage: $0 stream_url [step_s] [model]"
    echo ""
    echo "  Example:"
    echo "    $0 $url $step_s $model"
    echo ""
    echo "No url specified, using default: $url"
else
    url="$1"
fi

if [ -n "$2" ]; then
    step_s="$2"
fi

if [ -n "$3" ]; then
    model="$3"
fi

# Whisper models
models=( "tiny.en" "tiny" "base.en" "base" "small.en" "small" "medium.en" "medium" "large-v1" "large" )

# list available models
function list_models {
    printf "\\n"
    printf "  Available models:"
    for model in "${models[@]}"; do
        printf " $model"
    done
    printf "\\n\\n"
}

if [[ ! " ${models[@]} " =~ " ${model} " ]]; then
    printf "Invalid model: $model\\n"
    list_models

    exit 1
fi

running=1

trap "running=0" SIGINT SIGTERM

printf "[+] Transcribing stream with model '$model', step_s $step_s (press Ctrl+C to stop):\\n\\n"

# continuous stream in native fmt (this file will grow forever!)
ffmpeg -loglevel quiet -y -re -probesize 32 -i $url -c copy /tmp/whisper-live0.${fmt} &
if [ $? -ne 0 ]; then
    printf "Error: ffmpeg failed to capture audio stream\\n"
    exit 1
fi

printf "Buffering audio. Please wait...\\n\\n"
sleep $(($step_s))

# do not stop script on error
set +e

i=0
SECONDS=0
while [ $running -eq 1 ]; do
    # extract the next piece from the main file above and transcode to wav. -ss sets start time and nudges it by -0.5s to catch missing words (??)
    err=1
    while [ $err -ne 0 ]; do
        if [ $i -gt 0 ]; then
            ffmpeg -loglevel quiet -v error -noaccurate_seek -i /tmp/whisper-live0.${fmt} -y -ar 16000 -ac 1 -c:a pcm_s16le -ss $(($i*$step_s-1)).5 -t $step_s /tmp/whisper-live.wav 2> /tmp/whisper-live.err
        else
            ffmpeg -loglevel quiet -v error -noaccurate_seek -i /tmp/whisper-live0.${fmt} -y -ar 16000 -ac 1 -c:a pcm_s16le -ss $(($i*$step_s)) -t $step_s /tmp/whisper-live.wav 2> /tmp/whisper-live.err
        fi
        err=$(cat /tmp/whisper-live.err | wc -l)
    done

    ./main -t 8 -m ./models/ggml-${model}.bin -f /tmp/whisper-live.wav --no-timestamps -otxt 2> /tmp/whispererr | tail -n 1

    while [ $SECONDS -lt $((($i+1)*$step_s)) ]; do
        sleep 1
    done
    ((i=i+1))
done

killall -v ffmpeg
killall -v main"""
install_path = "bash_install.sh"
livestream_path = "livestream.sh"
def write_scripts(script, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script)

    if file_path.is_file() or file_path.is_dir():
        file_path.chmod(0o777)

print("Building build and run script")

write_scripts(docker_file, docker_path)
write_scripts(build_sh, build_path)
write_script(livestream_sh, livestream_path)
write_script(install_sh, install_path)
write_scripts(run_sh, run_path)

print("Build Docker image")
    
subprocess.run(["sudo", "bash ./build.sh"])
