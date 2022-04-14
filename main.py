import argparse
import os
from pathlib import Path
import analyzer
import compareWithDiff
import heatMapGenerator
from datetime import datetime



def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()

    parser.add_argument('firstdir',
                        help='First git repository to compare')
    parser.add_argument('seconddir',
                        help='Second git repository to compare')
    parser.add_argument('--outputdir', '-o', metavar='outdir', default = './mainOutput',
                            help='Directory containing the output. the output are csv file and heatmap image. Default = "%(default)s"')
    parser.add_argument('--timedelta', '-d', metavar='TIMEDELTA', default = None , type = int,
                            help='Sepcify the max time delta in seconds between commit time of source code. Compare all source code if not specified ')
    parser.add_argument('--saveimage', '-si', metavar='PATH-TO-SAVE-TO', default = None,
                        help='specify the path in wich save the result heatmap. If not specified, the script doesn\'t save the image ')
    parser.add_argument('--imageformat', '-format', metavar='IMAGE FORMAT', default = 'png', choices = ['png', 'svg', 'pdf'],
                        help='specify the format of the saved image. Choices are %(choices)s. Default = "%(default)s" ')
    parser.add_argument('--suppressplot', '-suppress', action = 'store_true',
                        help='Do not show the plot figure GUI')

    return parser


def make_dir(dirName):
    try:
        os.makedirs(dirName)
    except FileExistsError:
        print(f'la cartella {dirName} è già presente')


def main():
    startTime = datetime.now()
    parser = init_argparser()
    args = parser.parse_args()
    firstdir = args.firstdir
    seconddir = args.seconddir
    outputdir = args.outputdir
    timedelta = args.timedelta
    pathToSaveImage = args.saveimage
    imageFormat = args.imageformat
    suppressPlot = args.suppressplot

    analyzerOutputDir = os.path.join(outputdir, 'analyzerOutput')
    firstSourceFileDir = analyzer.copy_all_committed_file(firstdir, analyzerOutputDir)
    secondSourceFileDir = analyzer.copy_all_committed_file(seconddir, analyzerOutputDir)
    print(firstSourceFileDir, secondSourceFileDir)

    csvFile = compareWithDiff.compare_with_diff_all_file(os.path.dirname(firstSourceFileDir), os.path.dirname(secondSourceFileDir), outputdir, timedelta)

    heatMapGenerator.plot_and_save_image(csvFile, pathToSaveImage, imageFormat, suppressPlot)

    finishTime = datetime.now()
    print('Time required: ', finishTime -  startTime)



if __name__ == '__main__':
    main()
