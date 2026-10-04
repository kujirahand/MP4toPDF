#!/usr/bin/env python3

import sys, re, os
import subprocess
from html import escape
from io import BytesIO

ffmpeg = 'ffmpeg'

def change_ext(fname, ext):
    out = re.sub(r'\.[a-zA-Z0-9\_\%]+$', ext, fname)
    if ext != '.mp4':
        if out == fname: out += ext
    return out

# check args
if len(sys.argv) < 2:
    # check ffmpeg
    try:
        chk = subprocess.check_call([ffmpeg, '-version'])
    except Exception as e:
        print(e)
        print('please install ffmpeg')
        quit()
    # show usage
    print("------------")
    print("[usage] mp4topdf.py video.mp4 (output.pdf)")
    quit()


# get in/out file
infile = sys.argv[1]

# Is infile url?
if re.match(r'^https?://', infile):
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    mp4file = os.path.join(data_dir, change_ext(os.path.basename(infile), '.mp4'))
    subprocess.check_call(['wget', '-O', mp4file, infile])
    infile = mp4file

pdffile = change_ext(infile, '.pdf')
srtfile = change_ext(infile, '.srt')
textfile = change_ext(infile, '.txt')
if len(sys.argv) >= 3:
    pdffile = sys.argv[2]

print("in:", infile)
print("out:", pdffile)
# print("srt:", srtfile)

# mp4 to scr
cmd = [ffmpeg, "-y", "-i", infile, srtfile]
try:
    chk = subprocess.check_call(cmd)
except Exception as e:
    with open(textfile, 'wt', encoding='utf-8') as fp:
        fp.write("sorry failed to extract subtitle\n")
        fp.write("REASON: " + str(e) + "\n")
    print("[ERROR] sorry failed to extract subtitle")
    print("[REASON]", e)
    quit(-1)

# srt to text
with open(srtfile, "rt", encoding="utf-8") as fp:
    scr = fp.read()
scr = re.sub(r'\<.+?\>', '', scr) # remove tag
scr = re.sub(r'\{.+?\}', '', scr) # remove {...}
scr_a = scr.split("\n\n")
txt2 = ""
for s in scr_a:
    s = s.strip()
    sa = s.split("\n")
    del sa[0]
    if len(sa) == 0: continue
    m = re.match(r'\d+:\d+:\d+', sa[0])
    if not m: continue
    time_str = m.group(0)
    del sa[0]
    for i, ss in enumerate(sa):
        if i == 0:
            txt2 += time_str + "> "
        else:
            txt2 += " " * 10
        txt2 += ss + "\n"

# savet to textfile
with open(textfile, 'wt', encoding='utf-8') as fp:
    fp.write(txt2)

# Draw the transcript directly into a PDF. ReportLab provides text layout and
# Japanese CID fonts; pypdf writes the final document without an external renderer.
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from pypdf import PdfReader, PdfWriter

pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
line_style = ParagraphStyle(
    'TranscriptLine', fontName='HeiseiKakuGo-W5', fontSize=10.5,
    leading=16, wordWrap='CJK', textColor=colors.black,
)
story = []
for block in scr_a:
    lines = block.strip().splitlines()
    if len(lines) < 3:
        continue
    time_match = re.match(r'(\d{2}:\d{2}:\d{2})', lines[1])
    if not time_match:
        continue
    subtitle_lines = [re.sub(r'\{.+?\}', '', re.sub(r'<.+?>', '', line)).strip()
                      for line in lines[2:]]
    subtitle_lines = [line for line in subtitle_lines if line]
    if not subtitle_lines:
        continue
    for index, line in enumerate(subtitle_lines):
        prefix = f"{time_match.group(1)} - " if index == 0 else "　　　　- "
        story.append(Paragraph(escape(prefix + line), line_style))
    story.append(Spacer(1, 2 * mm))

rendered_pdf = BytesIO()
document = SimpleDocTemplate(
    rendered_pdf, pagesize=A4,
    rightMargin=18 * mm, leftMargin=18 * mm,
    topMargin=16 * mm, bottomMargin=16 * mm,
    title=os.path.basename(pdffile),
)
document.build(story)
reader = PdfReader(rendered_pdf)
writer = PdfWriter()
writer.append_pages_from_reader(reader)
writer.add_metadata({'/Title': os.path.basename(pdffile), '/Creator': 'MP4toPDF'})
with open(pdffile, 'wb') as output:
    writer.write(output)
print("ok.")









