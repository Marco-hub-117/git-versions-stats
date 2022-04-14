from pathlib import Path
import os
import csv


def make_dir(dirName):
    try:
        os.makedirs(dirName)
    except FileExistsError:
        print(f'la cartella {dirName} è già presente')


def init_csv_file(destDirectory, fileName, field, overwrite = False):
    """
        Init a .csv file with the first row containing field passed.
        field must be a list.
        return the destination file path
        Always overwite the csv if overwite == True
    """
    make_dir(destDirectory)
    if not Path(fileName).suffix == ".csv":
        fileName += '.csv'

    destFile = os.path.join(destDirectory,fileName)

    if os.path.isfile(destFile) and not overwrite:
        overwrite = input(f'Do you want to overwrite the file {destFile}? \n(ok, y, yes) to confirm\n')
        if overwrite in ['ok', 'y', 'yes']:
            with open(destFile, 'w', newline = '') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(field)
            print(f'File {destFile} overwritten')
    else:
        print(f'init a new csv file: {destFile}')
        with open(destFile, 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(field)

    return destFile


def add_rows_to_csv(csvFileName, rows):
    """
        append all rows passed into csvFileName
    """
    with open(csvFileName, 'a', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            writer.writerow(row)

def list_all_rows_from_csv(csvFileName):
    """
        return a list with all rows contained into csvFileName
    """
    with open(csvFileName, 'r', newline = '') as csvfile:
        reader = csv.reader(csvfile)
        field = next(reader)
        retrievedRowsList = []
        for row in reader:
            rowList = []
            for elem in row:
                rowList.append(elem)
            retrievedRowsList.append(rowList)

        return field, retrievedRowsList

def main():
    pass

if __name__ == '__main__':
    main()
