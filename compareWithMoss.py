import mosspy
import glob
import os
import argparse
from pathlib import Path
import pandas as pd
import csv
import re
import time
import subprocess
from supportModules.sendMossRequest import MossHandlingThread
from supportModules.csvSupport import init_csv_file, add_rows_to_csv

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

def get_valid_rows_from_url(url, firstFileGroup, secondFileGroup, necessaryComparison):
    """
        Return a nested list containing all valid information
        retieved from the moss web page.
        The result list will contain the comparison result between all file
        contained in firstFileGroup compared with the ones contained in secondFileGroup
        Each row has the following format:
        ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
            'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', 'LINES_MATCHES']
    """
    retries = 10
    while True:
        try:
            df_list = pd.read_html(url) # this parses all the tables in webpages to a list
            break
        except:
            retries -= 1
            if retries > 0:
                print(f'errore nel caricamento della pagina {url}, RIPROVO')
                time.sleep(5.0)
            else:
                print(f'errore nel caricamento della pagina {url}, tentativi finiti, ANNULLO')
                return []

    df = df_list[0] # select the first table, wich contains the value i need
    values = df.values  # return a ndarray containing the value i need
    valid_rows = []
    for value in values:
        file1 = value[0]
        file2 = value[1]
        lineMatch = value[2]
        if ((file1.split(' ')[0] in firstFileGroup) and (file2.split(' ')[0] in secondFileGroup)):
            if ([file1.split(' ')[0], file2.split(' ')[0]] not in necessaryComparison):
                continue
            print(file1, file2, lineMatch, sep = '|||')
            similarity = (float(get_perc_from_value(file1)) + float(get_perc_from_value(file2)))/2
            row = [file1.split(' ')[0], file2.split(' ')[0],
                get_date_from_file_name(file1), get_date_from_file_name(file2),
                url, get_perc_from_value(file1), get_perc_from_value(file2), similarity, lineMatch]
            valid_rows.append(row)
            try:
                necessaryComparison.remove([file1.split(' ')[0], file2.split(' ')[0]])
            except ValueError as e:
                print(e)

    # if a comparsion between two file is not present in the moss result page
    # then means that the two file doesn't match, so it need to be added
    # into valid rows a 0% match
    for elem in necessaryComparison:
        row = [elem[0], elem[1],
            get_date_from_file_name(elem[0]), get_date_from_file_name(elem[1]),
            url, 0.0, 0.0, 0.0, 0]
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

def get_all_possible_comparison(firstFileList, secondFileList):

    resultList = []
    for firstFile in firstFileList:
        for secondFile in secondFileList:
            couple = [firstFile, secondFile]
            resultList.append(couple)

    return resultList

def retrieve_completed_comparison(csvFileName):

    with open(csvFileName, 'r', newline = '') as csvfile:
        reader = csv.reader(csvfile)
        field = next(reader)
        retrievedComparisonList = []
        for row in reader:
            couple = [row[0], row[1]]
            retrievedComparisonList.append(couple)

    return retrievedComparisonList

def get_difference_between_list(firstList, secondList):
    """ Return a list containing all element of first list that are not present
    in second list
    """

    differenceList = []
    for elem in firstList:
        if elem not in secondList:
            differenceList.append(elem)

    return differenceList

def compare_with_moss_all_file(firstDir, secondDir, resultDir = './script_moss_compare'):
    """
        create a csv file into resultDir containing information retrieved
        from moss web page. It will contain information between the comparison
        of all .c file contained into firstDir and secondDir.
        The csv file has the following field:
        ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
            'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', SIMILARITY [%], 'LINES_MATCHES']
    """
    # init all variable needed
    firstAllFileList = glob.glob(os.path.join(firstDir,'**/*.c'), recursive = True)
    secondAllFileList = glob.glob(os.path.join(secondDir,'**/*.c'), recursive = True)
    firstAllFileList.sort(reverse = True)
    secondAllFileList.sort(reverse = True)
    # init result dir and csv file
    make_dir(resultDir)
    field = ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
        'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', 'SIMILARITY [%]', 'LINES_MATCHES']
    csvFileName = f'{Path(firstDir).name}_{Path(secondDir).name}.csv'
    print(csvFileName)
    csvFilePath = init_csv_file(resultDir, csvFileName, field)

    N = 160
    firstFileList = get_N_elements_from_list(firstAllFileList, N, sort = True)
    secondFileList = get_N_elements_from_list(secondAllFileList, N, sort = True)

    allComparisonsList = get_all_possible_comparison(firstFileList, secondFileList)
    print(len(allComparisonsList))

    retrievedComparisonList = retrieve_completed_comparison(csvFilePath)
    print(len(retrievedComparisonList))

    # allMissingComparison = get_difference_between_list(allComparisonsList, retrievedComparisonList)
    # print(len(allMissingComparison))

    n = 16 # number of element in each group
    for firstFileGroup in [firstFileList[i:i+n] for i in range(0, len(firstFileList), n)]:
        for secondFileGroup in [secondFileList[i:i+n] for i in range(0, len(secondFileList), n)]:
            groupComparison = get_all_possible_comparison(firstFileGroup, secondFileGroup)
            missingComparison = get_difference_between_list(groupComparison, retrievedComparisonList)
            firstFileGroupMissing = list(set([elem[0] for elem in missingComparison]))
            secondFileGroupMissing = list(set([elem[1] for elem in missingComparison]))
            print('firstFileGroupMissing NUMBER', len(firstFileGroupMissing))
            print('secondFileGroupMissing NUMBER', len(secondFileGroupMissing))
            if ((len(firstFileGroupMissing) <= 0) or (len(secondFileGroupMissing) <= 0)):
                continue
            retries = 2
            while True:
                mossThread = MossHandlingThread(firstFileGroupMissing, secondFileGroupMissing)
                mossThread.start()
                mossThread.join(300.0)
                print(mossThread.result_url)
                print()
                if mossThread.result_url == None:
                    retries -= 1
                    if (retries > 0):
                        continue
                    else:
                        break
                else:
                    break

            if mossThread.result_url == None:
                print(f"ERRORE, gruppo {firstFileGroup[0]}__{secondFileGroup[0]}")
                continue
            rows = get_valid_rows_from_url(mossThread.result_url,
                    firstFileGroupMissing, secondFileGroupMissing, missingComparison)
            add_rows_to_csv(csvFilePath, rows)



def main():
    parser = init_argparser()
    args = parser.parse_args()
    firstDir = args.firstdir
    secondDir = args.seconddir
    outdir = args.outdir

    if (not Path(firstDir).is_dir()):
        print(f"Attention, {firstDir} doesn't exist")
    elif (not Path(secondDir).is_dir()):
        print(f"Attention, {secondDir} doesn't exist")
    else :
        compare_with_moss_all_file(firstDir, secondDir, outdir)
        print("ALL COMPARISON COMPLETED")

    quit()


if __name__ == '__main__':
    main()
