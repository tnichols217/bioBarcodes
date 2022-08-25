# Barcode generator from csv file for the biology inventory system

- Generates Barcodes for every item in the biology lab

Run by placing the inventory.csv and history.csv files in this directory then run generate.sh

Uses Nix to standardize the inputs and python version, requirements are listed in flake.nix and locked in flake.lock

the inv folder contains the last completed transaction number inside the trsx file
the uuids.json file contains a map of each uuid to its corresponding ID

the export folder contains folders for each run, containing a pdf file containing the stickers