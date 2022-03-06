import csv
import argparse
from datetime import datetime

def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--filetoread', '-f', metavar='filetoread', default = './file.csv',
                        help='csv file to read. Default = "%(default)s"')
    return parser




def main():
    



if __name__ == '__main__':
    main()
