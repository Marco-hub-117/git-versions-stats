import mosspy
import glob
import os
import argparse
from pathlib import Path
import pandas as pd
import csv
import re

userid = 719337169

def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--firstdir', '-f', metavar='firstdir', default = './first',
                        help='First directory containing .c file to compare. Default = "%(default)s"')
    parser.add_argument('--seconddir', '-s', metavar='seconddir', default = './second',
                        help='second directory containing .c file to compare. Default = "%(default)s"')
    parser.add_argument('--outdir', '-o', metavar='outdir', default = './script_moss_compare',
                            help='Output directory containing the csv file with compare results. Default = "%(default)s"')
    return parser

def make_dir(dirName):
    try:
        os.makedirs(dirName)
    except FileExistsError:
        print(f'la cartella {dirName} è già presente')

def init_csv_file(destDirectory, fileName, field):
    """
        Init a .csv file with the first row containing field passed.
        field must be a list.
        return the destination file path
    """
    make_dir(destDirectory)
    if not Path(fileName).suffix == ".csv":
        fileName += '.csv'

    destFile = os.path.join(destDirectory,fileName)

    with open(destFile, 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field)

    return destFile

def init_moss_and_send(firstFile, secondFile, lang = 'c'):
    """
        Init a mosspy.Moss object and send the comparison between
        firstfile and secondfile.
        return the result url
    """
    m = mosspy.Moss(userid, lang)
    m.addFile(firstFile)
    m.addFile(secondFile)
    return m.send(lambda file_path, display_name: print('*', end='', flush=True))

def add_row_to_csv(csvFileName, row):
    """
        append the row passed into csvFileName
    """
    with open(csvFileName, 'a', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row)

def get_perc_from_value(value):
    """
        Extract PERC from value
        value must respect the following format:
        file_name.c (PERC%)
    """

    valueList = value.split(' ')
    percString = valueList[-1]
    percNumber = re.findall(r'-?\d+\.?\d*', percString)
    return float(percNumber[0])


def get_date_from_file_name(fileName):
    """
        This function return a string representing the date contained in .c
        fileName passed. fileName should respect the following format:
        parentDir/YYYY-MM-DD_HH-MM-SS_COMMITHEX.c
    """
    fileName = os.path.basename(fileName)
    fileNameParts = fileName.split('_')
    return fileNameParts[0] + '_' + fileNameParts[1]

def compare_with_moss_all_file(firstDir, secondDir, resultDir = './script_moss_compare'):
    """
        create a csv file into resultDir containing information retrieved
        from moss web page. It will contain information between the comparison
        of all .c file contained into firstDir and secondDir.
        The csv fil has the following field:
        ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
            'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', 'LINES_MATCHES']
    """
    # init all variable needed
    firstFileList = glob.glob(os.path.join(firstDir,'**/*.c'), recursive = True)
    secondFileList = glob.glob(os.path.join(secondDir,'**/*.c'), recursive = True)
    firstFileList.sort(reverse = True)
    secondFileList.sort(reverse = True)
    # init result dir and csv file
    make_dir(resultDir)
    field = ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
        'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', 'LINES_MATCHES']
    csvFileName = f'{Path(firstDir).name}_{Path(secondDir).name}.csv'
    print(csvFileName)
    csvFilePath = init_csv_file(resultDir, csvFileName, field)

    for firstFile in firstFileList:
        for secondFile in secondFileList:
            url = init_moss_and_send(firstFile, secondFile)
            print()
            df_list = pd.read_html(url) # this parses all the tables in webpages to a list
            df = df_list[0] # select the first table, wich contains the value i need
            values = df.values  # return a ndarray containing the value i need
            # values[0] contain the firs row containing the value i need
            try:
                file1 = values[0][0]
                file2 = values[0][1]
                lineMatch = values [0][2]
            except IndexError as ind_err:
                print("errore nell'indice a riga 120, passo al prossimo")
                continue
            except Exception as e:
                print(str(e))

            print(file1, file2, lineMatch)
            row = [file1.split(' ')[0], file2.split(' ')[0],
                get_date_from_file_name(file1), get_date_from_file_name(file2),
                url, get_perc_from_value(file1), get_perc_from_value(file2), lineMatch]
            add_row_to_csv(csvFilePath, row)


def main():
    parser = init_argparser()
    args = parser.parse_args()
    firstdir = args.firstdir
    seconddir = args.seconddir
    outdir = args.outdir

    compare_with_moss_all_file(firstdir, seconddir, outdir)


if __name__ == '__main__':
    main()
