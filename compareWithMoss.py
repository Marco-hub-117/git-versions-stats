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

def init_moss_and_send(firstFileList, secondFileList, lang = 'c'):
    """
        Init a mosspy.Moss object and send the comparison between
        all file contained in firstFileList and secondoFileList.
        return the result url
    """
    m = mosspy.Moss(userid, lang)
    m.setIgnoreLimit(250)
    m.setNumberOfMatchingFiles(500)

    for file in firstFileList:
        m.addFile(file)
    for file in secondFileList:
        m.addFile(file)

    try:
        result_url = m.send(lambda file_path, display_name: print('*', end='', flush=True))
    except:
        # Questo blocco l´ho aggiunto perchè mi ha dato l'errore:
        # ConnectionResetError: [Errno 104] Connection reset by peer
        # Ma solo ogni tanto lo fa, non so come risolvere
        print("Errore nell'invio del gruppo:", firstFileList[0], secondFileList[0])
        result_url = None

    return result_url

def add_rows_to_csv(csvFileName, rows):
    """
        append all rows passed into csvFileName
    """
    with open(csvFileName, 'a', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
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

def get_valid_rows_from_url(url, firstFileGroup, secondFileGroup):
    """
        Return a nested list containing all valid information
        retieved from the moss web page.
        The result list will contain the comparison result between all file
        contained in firstFileGroup compared with the ones contained in secondFileGroup
        Each row has the following format:
        ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
            'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', 'LINES_MATCHES']
    """
    df_list = pd.read_html(url) # this parses all the tables in webpages to a list
    df = df_list[0] # select the first table, wich contains the value i need
    values = df.values  # return a ndarray containing the value i need
    valid_rows = []
    for value in values:
        file1 = value[0]
        file2 = value[1]
        lineMatch = value[2]
        if ((file1.split(' ')[0] in firstFileGroup) and (file2.split(' ')[0] in secondFileGroup)):
            print(file1, file2, lineMatch, sep = '|||')
            row = [file1.split(' ')[0], file2.split(' ')[0],
                get_date_from_file_name(file1), get_date_from_file_name(file2),
                url, get_perc_from_value(file1), get_perc_from_value(file2), lineMatch]
            valid_rows.append(row)

    return valid_rows

def get_N_elements_from_list(list, N = 50, sort = False):
    """
        Return a list containing N elements from the list passed.
        If N is greater than the number of elements of the list passed,
        return the original list.
        If sort is True return a reverse sorted list
    """

    if (sort):
        list.sort(reverse = True)
    if (N >= len(list)):
        return list

    resultList = []
    i = 0
    multiplier = len(list) / N
    currentIndex = 0
    while (currentIndex < len(list)):
        resultList.append(list[currentIndex])
        i += 1
        currentFloatIndex = (i * multiplier)
        currentIndex = int (currentFloatIndex // 1)

    return resultList


def compare_with_moss_all_file(firstDir, secondDir, resultDir = './script_moss_compare'):
    """
        create a csv file into resultDir containing information retrieved
        from moss web page. It will contain information between the comparison
        of all .c file contained into firstDir and secondDir.
        The csv file has the following field:
        ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
            'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', 'LINES_MATCHES']
    """
    # init all variable needed
    firstAllFileList = glob.glob(os.path.join(firstDir,'**/*.c'), recursive = True)
    secondAllFileList = glob.glob(os.path.join(secondDir,'**/*.c'), recursive = True)
    firstAllFileList.sort(reverse = True)
    secondAllFileList.sort(reverse = True)
    # init result dir and csv file
    make_dir(resultDir)
    field = ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
        'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', 'LINES_MATCHES']
    csvFileName = f'{Path(firstDir).name}_{Path(secondDir).name}.csv'
    print(csvFileName)
    csvFilePath = init_csv_file(resultDir, csvFileName, field)

    N = 50
    firstFileList = get_N_elements_from_list(firstAllFileList, N, sort = True)
    secondFileList = get_N_elements_from_list(secondFileList, N, sort = True)

    n = 15 # number of element in each group
    for firstFileGroup in [firstFileList[i:i+n] for i in range(0, len(firstFileList), n)]:
        for secondFileGroup in [secondFileList[i:i+n] for i in range(0, len(secondFileList), n)]:
            url = init_moss_and_send(firstFileGroup, secondFileGroup)
            print()
            print(url)
            if (url is None):
                continue
            rows = get_valid_rows_from_url(url, firstFileGroup, secondFileGroup)
            add_rows_to_csv(csvFilePath, rows)

            # row = get_row_from_url(url)
            # if row is None:
            #     continue
            #
            # add_row_to_csv(csvFilePath, row)


def main():
    parser = init_argparser()
    args = parser.parse_args()
    firstDir = args.firstdir
    secondDir = args.seconddir
    outdir = args.outdir

    compare_with_moss_all_file(firstDir, secondDir, outdir)


if __name__ == '__main__':
    main()
