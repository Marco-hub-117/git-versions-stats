from pathlib import Path
import os
import glob
import argparse

from supportModules.csvSupport import init_csv_file, add_rows_to_csv, list_all_rows_from_csv
from supportModules.compareCode.compare_code import compare_code
import supportModules.comparisonListManager as compListMan


# The following are the csv fields with their indexes
FILE_NAME_1_IND = 0
FILE_NAME_2_IND = 1
TIME_STAMP_1_IND = 2
TIME_STAMP_2_IND = 3
ADD_TOKENS_IND = 4
REMOVE_TOKENS_IND = 5
SUM_TOKENS_IND = 6
DIFF_WITH_MAX_IND = 7
SIMILARITY_IND = 8


def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('firstdir',
                        help='First directory containing .c file to compare.')
    parser.add_argument('seconddir',
                        help='Second directory containing .c file to compare.')
    parser.add_argument('--outdir', '-o', metavar='outdir', default = './diff_compare_result',
                            help='Output directory containing the csv file with compare results. Default = "%(default)s"')
    parser.add_argument('--timedelta', '-d', metavar='TIMEDELTA', default = None , type = int,
                            help='Sepcify the max time delta in seconds between commit time of source code. Compare all source code if not specified ')

    return parser


def make_dir(dirName):
    try:
        os.makedirs(dirName)
    except FileExistsError:
        print(f'la cartella {dirName} è già presente')


def get_date_from_file_name(fileName):
    """
        This function return a string representing the date contained in .c
        fileName passed. fileName should respect the following format:
        parentDir/YYYY-MM-DD_HH-MM-SS_COMMITHEX.c
    """
    fileName = os.path.basename(fileName)
    fileNameParts = fileName.split('_')
    return fileNameParts[0] + '_' + fileNameParts[1]


def find_max(rows):
    """
        Return the max of the 'SUM_TOKENS' field.
        each row has the following field format:
        ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
            'ADD_TOKENS', 'REMOVE_TOKENS', 'SUM_TOKENS']
    """

    max = 0
    for row in rows:
        if (int(row[SUM_TOKENS_IND]) > max):
            max = int(row [SUM_TOKENS_IND]) # SUM_TOKENS_IND is a constant defined at the beginning of the script

    return max


def complete_rows_with_missing_field(partialRows):
    """
        This function complete each row with the missing information required
    """

    max = find_max(partialRows)
    print(max)
    rows = [] # this list will contain all completed row
    for partialRow in partialRows:
        diffWithMax = max - int(partialRow[SUM_TOKENS_IND]) # SUM_TOKENS is a constant defined at the beginning of the script
        similarityPerc = (diffWithMax / max) * 100
        partialRow.append(diffWithMax)
        partialRow.append(similarityPerc) # now partial row has all missing field
        rows.append(partialRow)

    return rows


def compare_with_diff_all_file(firstDir, secondDir, resultDir = './diff_compare_result', timeDelta = None):
    """
        create a csv file into resultDir containing information retrieved
        from internal comparison. It will contain information between the comparison
        of all .c file contained into firstDir and secondDir.
        The csv file has the following field:
        ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
            'ADD_TOKENS', 'REMOVE_TOKENS', 'SUM_TOKENS', 'DIFF_WITH_MAX', 'SIMILARITY [%]']
    """
    # init all variable needed
    firstAllFileList = glob.glob(os.path.join(firstDir,'**/*.c'), recursive = True)
    secondAllFileList = glob.glob(os.path.join(secondDir,'**/*.c'), recursive = True)
    firstAllFileList.sort(reverse = True)
    secondAllFileList.sort(reverse = True)
    # init result dir and csv file
    make_dir(resultDir)
    field = ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2',
        'ADD_TOKENS', 'REMOVE_TOKENS', 'SUM_TOKENS', 'DIFF_WITH_MAX', 'SIMILARITY [%]']
    csvFileName = f'{Path(firstDir).name}_{Path(secondDir).name}_diff.csv'
    print(csvFileName)
    csvFilePath = init_csv_file(resultDir, csvFileName, field)

    reformatCodePath = os.path.join(resultDir, 'reformat_code')
    make_dir(reformatCodePath)

    if (timeDelta is None):
        allComparisonsList = compListMan.get_all_possible_comparison(firstAllFileList, secondAllFileList)
    else:
        allComparisonsList = compListMan.get_comparison_based_delta(firstAllFileList, secondAllFileList, timeDelta)

    print('Retrieving already completed comparison, if present')
    retrievedComparisonList = compListMan.retrieve_completed_comparison(csvFilePath)
    allMissingComparison = compListMan.get_difference_between_list(allComparisonsList, retrievedComparisonList)

    missingComparisonNumber = len(allMissingComparison)
    completedComparisonNumber = 0

    print('Comparison start')
    for missingComparison in allMissingComparison:
        addToken, remToken = compare_code(missingComparison[0], missingComparison[1], reformatCodePath)
        partialRow = [[missingComparison[0], missingComparison[1], get_date_from_file_name(missingComparison[0]),
                    get_date_from_file_name(missingComparison[1]), addToken, remToken, addToken+remToken]] # need to be a nested list
        add_rows_to_csv(csvFilePath, partialRow)
        completedComparisonNumber += 1
        print(f'{completedComparisonNumber}/{missingComparisonNumber}')

    oldField, retrievedRowsList = list_all_rows_from_csv(csvFilePath)

    rows = complete_rows_with_missing_field(retrievedRowsList)

    csvFilePath = init_csv_file(resultDir, csvFileName, field, overwrite = True)

    add_rows_to_csv(csvFilePath, rows)

    return csvFilePath


def main():
    parser = init_argparser()
    args = parser.parse_args()
    firstDir = args.firstdir
    secondDir = args.seconddir
    outdir = args.outdir
    timedelta = args.timedelta

    if (not Path(firstDir).is_dir()):
        print(f"Attention, {firstDir} doesn't exist")
    elif (not Path(secondDir).is_dir()):
        print(f"Attention, {secondDir} doesn't exist")
    else :
        csvFilePath = compare_with_diff_all_file(firstDir, secondDir, outdir, timedelta)
        print("ALL COMPARISON COMPLETED, OUTPUT FILE IS:", csvFilePath)

    quit()


if __name__ == '__main__':
    main()
