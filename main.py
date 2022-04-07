import csv
import svgwrite
import sys
import qrcode
import qrcode.image.svg
from barcode import EAN13
import json
import uuid
import os
from pathlib import Path
from wand.image import Image
import svgutils
import xml.dom.minidom
import xml.etree.ElementTree
import cairosvg
from PyPDF2 import PdfFileMerger
import time

PXPMM = 3.7795275590551185

MAKE_PNG = False

UUIDS = {}

# filename
filename = sys.argv[1]
folder = filename.split('.')[0]

# parse csv

c = []
k = {}

with open(filename) as f:
    c = [i for i in csv.reader(f)]
    k = {}
    for i in range(len(c[0])):
        k[c[0][i]] = i
        k[i] = c[0][i]

    c = c[1:]

# sort csv items

factory = qrcode.image.svg.SvgPathImage
wid = 80
hei = 50
e = str(Path("./export/" + folder + "/").resolve()) + "/"
if not os.path.exists(e):
    os.makedirs(e)
q = ".qr"
b = ".bar"
s = ".svg"
fin = ".fin"

def gen_full(i):
    oo = {}
    u = ["ID", "Name", "Category", "Variation"]
    for j in u:
        oo[j] = i[k[j]]
    t = ("000" + str(int("".join([j if j != "-" else "" for j in str(uuid.uuid4())]), 16)))[-39:]
    t = str(t[:3]) + ("00" + str(hex(int(t[3:])).split("x")[-1]))[-30:]
    oo["UUID"] = t

    UUIDS[t] = oo["ID"]


    name = oo["ID"] + "-" + oo["UUID"]


    # generate qr


    img = qrcode.make(json.dumps(oo), image_factory=factory)
    img.save(e + name + q + s)

    tree = xml.dom.minidom.parse(e + name + q + s).toprettyxml()
    with open(e + name + q + s, "w") as f:
        f.write(tree)

    with open(e + name + q + s, 'r') as fr:
        l = fr.readlines()
        with open(e + name + q + s, 'w') as fw:
            fw.write("<g transform=\"translate(" + str(53 * PXPMM) + ",0) scale(0.4)\">")
            [fw.write(i) if "<!" not in i and "<?" not in i and i.strip().startswith("<") else "" for i in l]
            fw.write("</g>")



    # generate bar

    oo["Barcode"] = ("0" + str(int("".join([j if j != "-" else "" for j in oo["ID"]]), 16))[-10:] + str(oo["UUID"]))[:12]
    bar = EAN13(oo["Barcode"])
    bar.save(e + name + b)


    tree = xml.dom.minidom.parse(e + name + b + s).toprettyxml()
    with open(e + name + b + s, "w") as f:
        f.write(tree)

    with open(e + name + b + s, 'r') as fr:
        l = fr.readlines()
        with open(e + name + b + s, 'w') as fw:
            fw.write("<g transform=\"translate(" + str(41 * PXPMM) + "," + str(30 * PXPMM) + ") scale(0.9)\">")
            [fw.write(i) if "<text" not in i and "<!" not in i and "<?" not in i and i.strip().startswith("<") else "" for i in l]
            fw.write("</g>")

    

    # generate full image

    dwg = svgwrite.Drawing(e + name + fin + s, size=(str(wid) + "mm", str(hei) + "mm"), profile='full')
    dwg.add(dwg.g())

    size = 20

    [dwg.add(dwg.text(oo["Name"][i:i+15], ("5mm", str(7.5 + 0.4 * i) + "mm"), font_size=size, font_family="Fira Code")) for i in range(0, len(oo["Name"]), 15)]
    [dwg.add(dwg.text(oo["Variation"][i:i+15], ("5mm", str(22.5 + 0.4 * i) + "mm"), font_size=size, font_family="Fira Code")) for i in range(0, len(oo["Variation"]), 15)]
    [dwg.add(dwg.text(oo["ID"][i:i+11], ("5mm", str(32.5 + 0.4 * i) + "mm"), font_size=size, font_family="Fira Code")) for i in range(0, len(oo["UUID"]), 11)]
    [dwg.add(dwg.text(oo["UUID"][i:i+11], ("5mm", str(37.5 + 0.4 * i) + "mm"), font_size=size, font_family="Fira Code")) for i in range(0, len(oo["UUID"]), 11)]
    dwg.save()


    with open(e + name + fin + s, 'r') as fr:
        l = fr.read()
        with open(e + name + fin + s, 'w') as fw:
            with open(e + name + b + s) as fb:
                with open(e + name + q + s) as fq:
                    fw.write(l.replace("<g />", fb.read() + fq.read()))


    tree = xml.dom.minidom.parse(e + name + fin + s).toprettyxml()
    with open(e + name + fin + s, "w") as f:
        f.write(tree)

    # convert to png
    if MAKE_PNG:
        with Image(filename=e + name + fin + s, width=wid, height=hei) as img:
            with img.convert('png') as output_img:
                output_img.save(filename=e + name + fin + ".png")

    # format svg to be ready to be included in pdf
    with open(e + name + fin + s, 'r') as fr:
        l = fr.readlines()
        with open(e + name + fin + s, 'w') as fw:
            [fw.write(i) if "<!" not in i and "<?" not in i and i.strip().startswith("<") else "" for i in l]

    Path(e + name + q + s).unlink()
    Path(e + name + b + s).unlink()


for i in c:
    for _ in range(int(i[k["Quantity"]])):
        gen_full(i)




ff = [str(i) for i in Path(e).glob("*.svg")]

a4wid = 210
a4hei = 297
widd = 2
heii = 5
widdd = 80
heiii = 50

offsetx = (a4wid - widd * widdd) / 2
offsety = (a4hei - heii * heiii) / 2

ff = [[ff[j:j+heii] for j in range(i, i + widd * heii, heii)] for i in range(0, len(ff), widd * heii)]


for i in range(len(ff)):
    dwg2 = svgwrite.Drawing(e + str(i) + s, size=(str(a4wid) + "mm", str(a4hei) + "mm"), profile="full")
    dwg2.add(dwg2.g())
    dwg2.save()
    
    ss = ""

    for j in range(len(ff[i])):
        for k in range(len(ff[i][j])):
            ss += "<g transform=\"translate(" + str((offsetx + j * widdd) * PXPMM) + "," + str((offsety + k * heiii) * PXPMM) + ")\">"
            with open(str(ff[i][j][k])) as f:
                ss += f.read()
            ss += "</g>"


    with open(e + str(i) + s, 'r') as fr:
        l = fr.read()
        with open(e + str(i) + s, 'w') as fw:
            fw.write(l.replace("<g />", ss))

    tree = xml.dom.minidom.parse(e + str(i) + s).toprettyxml()
    with open(e + str(i) + s, "w") as f:
        f.write(tree)


    cairosvg.svg2pdf(url=e + str(i) + s, write_to=e + str(i) + ".pdf")


[i.unlink() for i in Path(e).glob("*.svg")]


pdfs = [i for i in Path(e).glob("*.pdf")]
merger = PdfFileMerger()

for pdf in pdfs:
    merger.append(str(pdf))

merger.write(e + "final.pdf")
merger.close()

[i.unlink() for i in pdfs]


e = str(Path("./inv").resolve()) + "/"
if not os.path.exists(e):
    os.makedirs(e)

with open(e + str(time.time()) + ".json", "w") as f:
    f.write(json.dumps(UUIDS))