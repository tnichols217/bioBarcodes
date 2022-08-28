import sys, json, pathlib, time, os
import csvParse, barcodeGen, tools

# filenames

inventory = sys.argv[1]
history = sys.argv[2]
folder = inventory.split('.')[0]

# constants

PXPMM = 3.7795275590551185
EXPORT = str(pathlib.Path("./export/" + folder + "/").resolve()) + "_" + str(time.time()) + "/"
INVENTORY = str(pathlib.Path("./inv").resolve()) + "/"
if not os.path.exists(INVENTORY):
    pathlib.Path(INVENTORY).mkdir()

UUIDFILE = INVENTORY + "uuids.json"
A4WIDTH = 210
A4HEIGHT = 297
HORIZONTALAMOUNT = 4
VERTICALAMOUNT = 10
TAGWIDTH = 80
TAGHEIGHT = 50
TAGSCALE = 0.5

offsetX = (A4WIDTH - (HORIZONTALAMOUNT * TAGWIDTH * TAGSCALE)) / 2
offsetY = (A4HEIGHT - (VERTICALAMOUNT * TAGHEIGHT * TAGSCALE)) / 2


inventoryCsv, inventoryKey = csvParse.parseCSV(inventory, history, INVENTORY, EXPORT)

generatedBarcodes = []

uuids, generatedBarcodes = tools.generateStickers(UUIDFILE, inventoryCsv, inventoryKey, inventory, TAGWIDTH, TAGHEIGHT, EXPORT)

# split list of svgs into chunks by page then column

generatedBarcodes = [[generatedBarcodes[j:j+VERTICALAMOUNT] for j in range(i, i + HORIZONTALAMOUNT * VERTICALAMOUNT, VERTICALAMOUNT)] for i in range(0, len(generatedBarcodes), HORIZONTALAMOUNT * VERTICALAMOUNT)]

generatedPdfPages = tools.svg2pdf(generatedBarcodes, inventoryKey, EXPORT, A4WIDTH, A4HEIGHT, offsetX, offsetY, TAGWIDTH, TAGHEIGHT, TAGSCALE)

# merge pdfs

barcodeGen.combinePdfs(generatedPdfPages, EXPORT + "final.pdf")

# write out UUID -> ID table

pathlib.Path(UUIDFILE).touch()
with open(UUIDFILE, "w") as f:
    f.write(json.dumps(uuids, indent=4))