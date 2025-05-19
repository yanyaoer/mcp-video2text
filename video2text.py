#! /usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp", "pywhispercpp", "mlx-whisper", "pydantic_ai"]
# ///

# dependencies = ["yt-dlp", "mlx-whisper", "sherpa-onnx"]

# from pathlib import Path

import mlx_whisper
import yt_dlp
from mcp.server.fastmcp import FastMCP

server = FastMCP("PydanticAI Server")


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
    return info["id"] + ".wav"


def asr_mlx(wav_file):
  result = mlx_whisper.transcribe(
    wav_file,
    path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
  )

  return [s["text"] for s in result["segments"]]


"""
from pywhispercpp.model import Model as whisper_cpp

def asr_cpp(wav_file):
  model = whisper_cpp(
    "large-v3-turbo",
    models_dir="$HOME/Projects/agi/whisper.cpp/models/",  # for dev
  )
  segments = model.transcribe(
    wav_file, language="zh", initial_prompt="以下是普通话的句子。"
  )
  for segment in segments:
    print(segment.text)
"""


@server.tool()
async def video2text(url: str) -> str:
  """tools for download video and extract audio,
  then transcribe to text"""

  w = download(url)
  r = asr_mlx(w)
  return "\n".join(r)


if __name__ == "__main__":
  server.run()
