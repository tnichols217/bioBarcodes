import xml, PyPDF2, barcode, qrcode, qrcode.image.svg, svgwrite, random, json, pathlib, uuid

PXPMM = 3.7795275590551185
FACTORY = qrcode.image.svg.SvgPathImage
QR = ".qr"
BAR = ".bar"
SVG = ".svg"
FIN = ".fin"
COLUMNS = ["ID", "Name", "Category", "Variation"]


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

    merger = PyPDF2.PdfFileMerger()

    for pdf in pdfs:
        merger.append(str(pdf))

    merger.write(out)
    merger.close()

    # delete pdf parts 

    [pathlib.Path(i).unlink() for i in pdfs]

# barcode generator

def gen_full(item, inventory, inventoryKey, UUIDS, TAGWIDTH, TAGHEIGHT, EXPORT):

    FOLDER = inventory.split('.')[0]

    # parse csv row into oo object dictionary
    itemTrim = {}
    for j in COLUMNS:
        itemTrim[j] = item[inventoryKey[j]]
    
    # generate uuid, with first three digits being base 10 for the barcode

    randThree = ("00" + str(random.randrange(0, 999)))[-3:]
    itemTrim["UUID"] = (randThree + "".join([j if j != "-" else "" for j in str(uuid.uuid4())]))[:33]
    itemTrim["Barcode"] = ("0" + str(int("".join([j if j != "-" else "" for j in itemTrim["ID"]]), 16)) + randThree)[-12:]

    UUIDS[itemTrim["UUID"]] = itemTrim["ID"]
    name = itemTrim["ID"] + "-" + itemTrim["UUID"]

    # generate qr

    img = qrcode.make(json.dumps(itemTrim), image_factory=FACTORY)
    img.save(EXPORT + name + QR + SVG)

    parseSVGtoGtag(EXPORT + name + QR + SVG, 53, 0, 0.4)

    # generate bar

    bar = barcode.EAN13(itemTrim["Barcode"])
    bar.save(EXPORT + name + BAR)

    parseSVGtoGtag(EXPORT + name + BAR + SVG, 41, 31.5, 0.9, removeText=True)

    # generate full image

    dwg = svgwrite.Drawing(EXPORT + name + FIN + SVG, size=(str(TAGWIDTH) + "mm", str(TAGHEIGHT) + "mm"), profile='full')
    dwg.add(dwg.g())
    addText(dwg, itemTrim["Name"], 5, 7.5, 15)
    addText(dwg, itemTrim["Variation"], 5, 22.5, 15)
    addText(dwg, itemTrim["ID"], 5, 32.5, 11)
    addText(dwg, itemTrim["UUID"], 5, 37.5, 11)
    dwg.save()

    outputFile = EXPORT + name + FIN + SVG

    with open(outputFile, 'r') as fr:
        l = fr.read()
        with open(outputFile, 'w') as fw:
            with open(EXPORT + name + BAR + SVG) as fb:
                with open(EXPORT + name + QR + SVG) as fq:
                    fw.write(l.replace("<g />", fb.read() + fq.read()))


    pathlib.Path(EXPORT + name + QR + SVG).unlink()
    pathlib.Path(EXPORT + name + BAR + SVG).unlink()
    return UUIDS, outputFile
