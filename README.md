# MP4toPDF

Extract subtitle from MP4 and convert PDF

# Platform

 - macOS / Linux

# Need

Please install tools to $PATH.

 - ffmpeg
 - python3
 - Python packages: `pypdf`, `reportlab`

# Install with pip

```
pip3 install -r requirements.txt
cd src
chmod +x mp4topdf.py
```

# Install and run with uv

Install `uv` and `ffmpeg`, then run the script from the repository root:

```
uv run --with-requirements requirements.txt src/mp4topdf.py example.mp4
```

To create a virtual environment and install the dependencies first:

```
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python src/mp4topdf.py example.mp4
```

On macOS, you can also run the included shell script from the repository root:

```
chmod +x mp4topdf.sh
./mp4topdf.sh example.mp4
```

# How to use

```
python3 src/mp4topdf.py example.mp4
```

# macOS

```
brew install ffmpeg
```

PDF is generated directly by Python. ReportLab lays out the transcript and
pypdf writes the final PDF; no HTML-to-PDF executable is required.
