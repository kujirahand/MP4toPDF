#!/usr/bin/env python3

import sys, re, os
import subprocess

ffmpeg = 'ffmpeg'
topdf = 'wkhtmltopdf'

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
    try:
        chk = subprocess.check_call([topdf, '--version'])
    except:
        print('please install wkhtmltopdf')
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
htmlfile = change_ext(infile, '.html')
textfile = change_ext(infile, '.txt')
tplfile = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'template.html')
if len(sys.argv) >= 3:
    outfile = sys.argv[2]

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

# scr to text
with open(srtfile, "rt", encoding="utf-8") as fp:
    scr = fp.read()
scr = re.sub(r'\<.+?\>', '', scr) # remove tag
scr = re.sub(r'\{.+?\}', '', scr) # remove {...}
scr_a = scr.split("\n\n")
txt2 = ""
txt = ""
for s in scr_a:
    s = s.strip()
    sa = s.split("\n")
    del sa[0]
    if len(sa) == 0: continue
    m = re.match('\d+:\d+:\d+', sa[0])
    if not m: continue
    time_str = m.group(0)
    del sa[0]
    line = ""
    for i, ss in enumerate(sa):
        if i == 0:
            line += "<span class='time'>" + time_str + ":</span> "
            txt2 += time_str + "> "
        else:
            line += "&nbsp;" * 10
            txt2 += " " * 10
        line += ss + "<br>\n"
        txt2 += ss + "\n"
    txt += line

# savet to textfile
with open(textfile, 'wt', encoding='utf-8') as fp:
    fp.write(txt2)

# convert to html
tpl = open(tplfile, 'rt', encoding='utf-8').read()
tpl = tpl.replace('__TEXT__', txt)
with open(htmlfile, 'wt', encoding='utf-8') as fp:
    fp.write(tpl)

# convert to pdf
import pdfkit
options = {
    'page-size': 'A4',
    'margin-top': '0.1in',
    'margin-right': '0.1in',
    'margin-bottom': '0.1in',
    'margin-left': '0.1in',
    'encoding': "UTF-8",
    #'no-outline': None
}
pdfkit.from_file(htmlfile, pdffile, options=options)
print("ok.")














