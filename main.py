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

# filename

filename = sys.argv[1]
ledger = sys.argv[2]
folder = filename.split('.')[0]

# constants

PXPMM = 3.7795275590551185

UUIDS = {}

factory = qrcode.image.svg.SvgPathImage
wid = 80
hei = 50
e = str(Path("./export/" + folder + "/").resolve()) + "_" + str(time.time()) + "/"
inv = str(Path("./inv").resolve()) + "/"
trsx = "trsx"
q = ".qr"
b = ".bar"
s = ".svg"
fin = ".fin"
u = ["ID", "Name", "Category", "Variation"]

a4wid = 210
a4hei = 297
widd = 2
heii = 5
widdd = 80
heiii = 50

offsetx = (a4wid - widd * widdd) / 2
offsety = (a4hei - heii * heiii) / 2

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

# parse current inventory

c2 = []
k2 = {}

with open(ledger) as f:
    c2 = [i for i in csv.reader(f)]
    k2 = {}
    for i in range(len(c2[0])):
        k2[c2[0][i]] = i
        k2[i] = c2[0][i]

    c2 = c2[1:]

if not os.path.exists(inv + trsx):
    with open(inv + trsx, "w") as f:
        f.write("FF")

lastTrsx = ""
outTrsx = ""

with open(inv + trsx, "r") as f:
    outTrsx = f.read()
    lastTrsx = int(outTrsx, 16)

cc2 = []

for i in c2:
    if int(i[k2["Trsx ID"]], 16) > lastTrsx:
        outTrsx = i[k2["Trsx ID"]]
        print(i)
        cc2.append(i)

with open(inv + trsx, "w") as f:
    f.write(outTrsx)

val2 = {}

for i in cc2:
    if i[k2["ID"]] not in val2:
        val2[i[k2["ID"]]] = 0
    
    val2[i[k2["ID"]]] += int(i[k2["Change in quantity"]])

# sort csv items

if not os.path.exists(e):
    os.makedirs(e)

if not os.path.exists(inv):
    os.makedirs(inv)

for i in c:
    if i[k["ID"]] in val2:
        i[k["Quantity"]] = val2[i[k["ID"]]]
    else:
        i[k["Quantity"]] = 0

# clean svg

def cleanSVG(svgFile, removeText=False, clearMeta=True):
    tree = xml.dom.minidom.parse(svgFile).toprettyxml()
    with open(svgFile, "w") as f:
        f.write(tree)

    with open(svgFile, 'r') as fr:
        l = fr.readlines()
        with open(svgFile, 'w') as fw:
            [fw.write(i) if ("<text" not in i or not removeText) and ("<!" not in i or not clearMeta) and ("<?" not in i or not clearMeta) and i.strip().startswith("<") else "" for i in l]

def parseSVGtoGtag(svgFile, x, y, s, removeText=False):
    cleanSVG(svgFile, removeText=removeText)
    with open(svgFile, 'r') as fr:
        l = fr.read()
        with open(svgFile, 'w') as fw:
            fw.write("<g transform=\"translate(" + str(x * PXPMM) + "," + str(y * PXPMM) + ") scale(" + str(s) + ")\">" + l + "</g>")



def addText(dwg, text, x, y, wraplength):
    [dwg.add(dwg.text(text[i:i+wraplength], (str(x) + "mm", str(y + 0.4 * i) + "mm"), font_size=20, font_family="Fira Code")) for i in range(0, len(text), wraplength)]

def combinePdfs(pdfs, out):
    # find and merge pdfs

    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(str(pdf))

    merger.write(out)
    merger.close()

    # delete pdf parts 

    [i.unlink() for i in pdfs]    

# barcode generator

def gen_full(i):
    # parse csv row into oo object dictionary
    oo = {}
    for j in u:
        oo[j] = i[k[j]]
    
    # generate uuid, with first three digits being base 10 for the barcode

    t = ("000" + str(int("".join([j if j != "-" else "" for j in str(uuid.uuid4())]), 16)))[-39:]
    t = str(t[:3]) + ("00" + str(hex(int(t[3:])).split("x")[-1]))[-30:]
    oo["UUID"] = t

    UUIDS[t] = oo["ID"]

    name = oo["ID"] + "-" + oo["UUID"]

    # generate qr

    img = qrcode.make(json.dumps(oo), image_factory=factory)
    img.save(e + name + q + s)

    parseSVGtoGtag(e + name + q + s, 53, 0, 0.4)

    # generate bar

    oo["Barcode"] = ("0" + str(int("".join([j if j != "-" else "" for j in oo["ID"]]), 16))[-10:] + str(oo["UUID"]))[:12]
    bar = EAN13(oo["Barcode"])
    bar.save(e + name + b)

    parseSVGtoGtag(e + name + b + s, 41, 31.5, 0.9, removeText=True)

    # generate full image

    dwg = svgwrite.Drawing(e + name + fin + s, size=(str(wid) + "mm", str(hei) + "mm"), profile='full')
    dwg.add(dwg.g())
    addText(dwg, oo["Name"], 5, 7.5, 15)
    addText(dwg, oo["Variation"], 5, 22.5, 15)
    addText(dwg, oo["ID"], 5, 32.5, 11)
    addText(dwg, oo["UUID"], 5, 37.5, 11)
    dwg.save()


    with open(e + name + fin + s, 'r') as fr:
        l = fr.read()
        with open(e + name + fin + s, 'w') as fw:
            with open(e + name + b + s) as fb:
                with open(e + name + q + s) as fq:
                    fw.write(l.replace("<g />", fb.read() + fq.read()))


    Path(e + name + q + s).unlink()
    Path(e + name + b + s).unlink()


# generate svg according to csv

for i in c:
    for _ in range(int(i[k["Quantity"]])):
        gen_full(i)

ff = [str(i) for i in Path(e).glob("*.svg")]

# split list of svgs into chunks by page then column

ff = [[ff[j:j+heii] for j in range(i, i + widd * heii, heii)] for i in range(0, len(ff), widd * heii)]

# start making each svg into pdf by page

for i in range(len(ff)):
    dwg2 = svgwrite.Drawing(e + str(i) + s, size=(str(a4wid) + "mm", str(a4hei) + "mm"), profile="full")
    dwg2.add(dwg2.g())
    dwg2.save()
    
    ss = ""

    for j in range(len(ff[i])):
        for k in range(len(ff[i][j])):
            parseSVGtoGtag(str(ff[i][j][k]), offsetx + j * widdd, offsety + k * heiii, 1)
            with open(str(ff[i][j][k])) as f:
                ss += f.read()

    with open(e + str(i) + s, 'r') as fr:
        l = fr.read()
        with open(e + str(i) + s, 'w') as fw:
            fw.write(l.replace("<g />", ss))

    cleanSVG(e + str(i) + s, clearMeta=False)

    cairosvg.svg2pdf(url=e + str(i) + s, write_to=e + str(i) + ".pdf")

# delete svgs

[i.unlink() for i in Path(e).glob("*.svg")]

# merge pdfs

combinePdfs([i for i in Path(e).glob("*.pdf")], e + "final.pdf")

# write out UUID -> ID table

with open(inv + str(time.time()) + ".json", "w") as f:
    f.write(json.dumps(UUIDS))