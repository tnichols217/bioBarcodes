import csv, os, pathlib

TRSX = "trsx"


def parseCSVFile(filename):
    csvLines = []
    csvKey = {}
    with open(filename) as csvfile:
        csvLines = [i for i in csv.reader(csvfile)]
        csvKey = {}
        for line in range(len(csvLines[0])):
            csvKey[csvLines[0][line]] = line
            csvKey[line] = csvLines[0][line]
            # create csvKey object

        csvLines = csvLines[1:]
        # remove key from csvLines
    
    return csvLines, csvKey


def parseCSV(inventory, history, INV, EXPORT):
    # parse inventory and history

    inventoryCsv, inventoryKey = parseCSVFile(inventory)
    historyCsv, historyKey = parseCSVFile(history)

    # get trsx file and contents
    if not os.path.exists(INV):
        pathlib.Path(INV).mkdir()

    if not os.path.exists(INV + TRSX):
        with open(INV + TRSX, "w") as f:
            f.write("FF")

    lastTrsx = ""
    outTrsx = ""

    with open(INV + TRSX, "r") as f:
        outTrsx = f.read()
        lastTrsx = int(outTrsx, 16)

    newTransactions = []

    for line in historyCsv:
        if int(line[historyKey["Trsx ID"]], 16) > lastTrsx:
            outTrsx = line[historyKey["Trsx ID"]]
            newTransactions.append(line)

    with open(INV + TRSX, "w") as f:
        # write the latest transaction
        f.write(outTrsx)

    transactionLog = {}

    for transaction in newTransactions:
        if transaction[historyKey["ID"]] not in transactionLog:
            transactionLog[transaction[historyKey["ID"]]] = 0

        quantity = int(transaction[historyKey["Change in quantity"]])
        
        transactionLog[transaction[historyKey["ID"]]] += quantity if quantity > 0 else 0

    # sort csv items

    if not os.path.exists(EXPORT):
        os.makedirs(EXPORT)

    if not os.path.exists(INV):
        os.makedirs(INV)

    for line in inventoryCsv:
        if line[inventoryKey["ID"]] in transactionLog:
            line[inventoryKey["Quantity"]] = transactionLog[line[inventoryKey["ID"]]]
        else:
            line[inventoryKey["Quantity"]] = 0

    return inventoryCsv, inventoryKey
