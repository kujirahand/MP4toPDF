#!/usr/bin/env python3

"""Extract subtitles from a video and save them as timestamped plain text."""

import os
import re
import subprocess
import sys


FFMPEG = "ffmpeg"


def change_ext(filename, extension):
    output = re.sub(r"\.[a-zA-Z0-9_%]+$", extension, filename)
    if output == filename:
        output += extension
    return output


def srt_to_text(srt):
    blocks = re.split(r"\r?\n\s*\r?\n", srt.strip())
    output = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        time_match = re.match(r"(\d{2}:\d{2}:\d{2})", lines[1])
        if not time_match:
            continue
        subtitle_lines = [
            re.sub(r"\{.+?\}", "", re.sub(r"<.+?>", "", line)).strip()
            for line in lines[2:]
        ]
        subtitle_lines = [line for line in subtitle_lines if line]
        if subtitle_lines:
            output.append(f"{time_match.group(1)}> {' '.join(subtitle_lines)}")
    return "\n".join(output) + ("\n" if output else "")


def main(args):
    if not args:
        print("Usage: mp4totxt.py video.mp4 [output.txt]", file=sys.stderr)
        return 2

    infile = args[0]
    if re.match(r"^https?://", infile):
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(data_dir, exist_ok=True)
        mp4file = os.path.join(data_dir, change_ext(os.path.basename(infile), ".mp4"))
        subprocess.check_call(["wget", "-O", mp4file, infile])
        infile = mp4file

    textfile = args[1] if len(args) >= 2 else change_ext(infile, ".txt")
    srtfile = change_ext(infile, ".srt")
    print("in:", infile)
    print("out:", textfile)

    try:
        subprocess.check_call([FFMPEG, "-y", "-i", infile, srtfile])
    except (OSError, subprocess.CalledProcessError) as error:
        print("[ERROR] failed to extract subtitle", file=sys.stderr)
        print("[REASON]", error, file=sys.stderr)
        return 1

    with open(srtfile, "rt", encoding="utf-8") as source:
        text = srt_to_text(source.read())
    with open(textfile, "wt", encoding="utf-8") as output:
        output.write(text)
    print("ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
