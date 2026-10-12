"""Transcribe all MP3 files in podcasts/ using OpenAI Whisper."""
import sys
from pathlib import Path

import whisper

PODCASTS_DIR = Path(__file__).parent / "podcasts"


def main():
    model_name = sys.argv[1] if len(sys.argv) > 1 else "base"
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    mp3s = sorted(PODCASTS_DIR.glob("*.mp3"))
    if not mp3s:
        print("No MP3 files found in podcasts/")
        return

    for mp3 in mp3s:
        out_file = mp3.with_suffix(".txt")
        if out_file.exists():
            print(f"Skipping {mp3.name} (transcript already exists)")
            continue

        print(f"Transcribing {mp3.name}...")
        result = model.transcribe(str(mp3), language="en")
        text = result["text"].strip()
        out_file.write_text(text)
        print(f"  -> {out_file.name} ({len(text)} chars)")

    print("Done.")


if __name__ == "__main__":
    main()
