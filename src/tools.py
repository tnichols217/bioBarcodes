import os, svgwrite, pathlib, cairosvg, json
import barcodeGen

SVG = ".svg"

# generate svg according to csv
def generateStickers(UUIDFILE, inventoryCsv, inventoryKey, inventory, TAGWIDTH, TAGHEIGHT, EXPORT):
    uuids = {}
    generatedBarcodes = []
    if os.path.exists(UUIDFILE):
        with open(UUIDFILE, "r") as f:
            uuids = json.loads(f.read())
    for item in inventoryCsv:
        for _ in range(int(item[inventoryKey["Quantity"]])):
            # writes to EXPORT + name + .fin.svg
            outUUIDS, newBarcode = barcodeGen.gen_full(item, inventory, inventoryKey, uuids, TAGWIDTH, TAGHEIGHT, EXPORT)
            uuids = outUUIDS
            generatedBarcodes.append(newBarcode)
    return uuids, generatedBarcodes

# start making each svg into pdf by page
def svg2pdf(generatedBarcodes, inventoryKey, EXPORT, A4WIDTH, A4HEIGHT, offsetX, offsetY, TAGWIDTH, TAGHEIGHT):
    outputFiles = []
    for page in range(len(generatedBarcodes)):
        pageSVG = EXPORT + str(page) + SVG
        dwg2 = svgwrite.Drawing(pageSVG, size=(str(A4WIDTH) + "mm", str(A4HEIGHT) + "mm"), profile="full")
        dwg2.add(dwg2.g())
        dwg2.save()
        
        ss = ""

        for column in range(len(generatedBarcodes[page])):
            for inventoryKey in range(len(generatedBarcodes[page][column])):
                barcodeGen.parseSVGtoGtag(str(generatedBarcodes[page][column][inventoryKey]), offsetX + column * TAGWIDTH, offsetY + inventoryKey * TAGHEIGHT, 1)
                svgFileLocation = str(generatedBarcodes[page][column][inventoryKey])
                with open(svgFileLocation) as f:
                    ss += f.read()
                pathlib.Path(svgFileLocation).unlink()

        with open(pageSVG, 'r') as fr:
            l = fr.read()
            with open(pageSVG, 'w') as fw:
                fw.write(l.replace("<g />", ss))

        barcodeGen.cleanSVG(pageSVG, clearMeta=False)

        outPdf = EXPORT + str(page) + ".pdf"

        cairosvg.svg2pdf(url=pageSVG, write_to=outPdf)
        outputFiles.append(outPdf)
        # delete svg once its converted to pdf
        pathlib.Path(pageSVG).unlink()
    return outputFiles