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
wid = 800
hei = 500
e = str(Path("./export/" + folder + "/").resolve()) + "/"
if not os.path.exists(e):
    os.makedirs(e)
q = ".qr"
b = ".bar"
s = ".svg"
fin = ".fin"
scl = "<svg transform=\"scale(5)\""

def gen_full(i):
    oo = {}
    u = ["ID", "Name", "Category", "Variation"]
    for j in u:
        oo[j] = i[k[j]]
    t = ("000" + str(int("".join([j if j != "-" else "" for j in str(uuid.uuid4())]), 16)))[-39:]
    t = str(t[:3]) + ("00" + str(hex(int(t[3:])).split("x")[-1]))[-30:]
    oo["UUID"] = t


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
            fw.write("<g transform=\"translate(530, 0) scale(1.1)\">")
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
            fw.write("<g transform=\"translate(360, 270) scale(2.75)\">")
            [fw.write(i) if "<text" not in i and "<!" not in i and "<?" not in i and i.strip().startswith("<") else "" for i in l]
            fw.write("</g>")

    

    # generate full image

    dwg = svgwrite.Drawing(e + name + fin + s, size=(wid, hei), profile='full')
    dwg.add(dwg.g())

    size = 50
    width = 500

    [dwg.add(dwg.text(oo["Name"][i:i+15], (50, 75 + 4 * i), font_size=size, font_family="Fira Code")) for i in range(0, len(oo["Name"]), 15)]
    [dwg.add(dwg.text(oo["Variation"][i:i+15], (50, 225 + 4 * i), font_size=size, font_family="Fira Code")) for i in range(0, len(oo["Variation"]), 15)]
    [dwg.add(dwg.text(oo["ID"][i:i+11], (50, 325 + 4 * i), font_size=size, font_family="Fira Code")) for i in range(0, len(oo["UUID"]), 11)]
    [dwg.add(dwg.text(oo["UUID"][i:i+11], (50, 375 + 4 * i), font_size=size, font_family="Fira Code")) for i in range(0, len(oo["UUID"]), 11)]
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


    with Image(filename=e + name + fin + s, width=wid, height=hei) as img:
        with img.convert('png') as output_img:
            output_img.save(filename=e + name + fin + ".png")


for i in c:
    for _ in range(int(i[k["Quantity"]])):
        gen_full(i)


for p in Path(e).glob("*" + s):
    p.unlink()