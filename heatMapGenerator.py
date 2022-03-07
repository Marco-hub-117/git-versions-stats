import csv
import argparse
from datetime import datetime
import numpy as np

def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--filetoread', '-f', metavar='filetoread', default = './file.csv',
                        help='csv file to read. Default = "%(default)s"')
    return parser

def get_date_lists(csvFileToRead):
    """
        Return two sorted date list conteining all date contained in the two
        columns of csvFileToRead that contain the timestamp
    """
    with open(csvFileToRead, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        firstDateList = []
        secondDateList = []

        for row in reader:
            if (not row[2] in firstDateList):
                firstDateList.append(row[2])
            if (not row[3] in secondDateList):
                secondDateList.append(row[3])

        firstDateList.sort(reverse = True)
        secondDateList.sort(reverse = True)

        return firstDateList, secondDateList


def main():
    parser = init_argparser()
    args = parser.parse_args()
    destFile = args.filetoread

    firstDateList, secondDateList = get_date_lists(destFile)

    print(firstDateList)
    print(secondDateList)

    print(len(firstDateList))
    print(len(secondDateList))





if __name__ == '__main__':
    main()
