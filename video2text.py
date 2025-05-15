#! /usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp", "soundfile", "pywhispercpp", "mlx-whisper"]
# ///

# dependencies = ["yt-dlp", "mlx-whisper", "sherpa-onnx"]

from pathlib import Path

import mlx_whisper
import yt_dlp
from pywhispercpp.model import Model as whisper_cpp


def download(url):
  ydl_opts = {
    "format": "m4a/bestaudio/best",
    "postprocessors": [
      {
        "key": "FFmpegExtractAudio",
        "preferredcodec": "wav",
      }
    ],
    "outtmpl": "%(id)s.%(ext)s",
    "postprocessor_args": [
      "-ar",
      "16000",
      "-ac",
      "1",
    ],
  }

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download([url])
    if error_code != 0:
      raise Exception("Download failed")

    info = ydl.extract_info(url, download=False)
    # print(info["id"])
    return info["id"] + ".wav"


def asr_mlx(wav_file):
  result = mlx_whisper.transcribe(
    wav_file,
    path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
  )

  for seg in result["segments"]:
    print(seg["text"])


def asr_cpp(wav_file):
  model = whisper_cpp(
    "large-v3-turbo",
    models_dir="/Users/yanyao/Projects/agi/whisper.cpp/models/",  # for dev
  )
  segments = model.transcribe(
    wav_file, language="zh", initial_prompt="以下是普通话的句子。"
  )
  for segment in segments:
    print(segment.text)


if __name__ == "__main__":
  import sys

  u = (
    sys.argv[1] if len(sys.argv) > 1 else "https://www.bilibili.com/video/BV1ZMNrejEnH/"
  )
  # w = download(u)
  # w = "/tmp/BV1ZMNrejEnH.wav"
  # w = "/tmp/1746897004.wav"
  w = "BV1VqEvzSEcs.wav"
  asr_cpp(w)
  asr_mlx(w)
  # print(r)
