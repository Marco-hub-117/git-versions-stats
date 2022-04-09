import csv
import argparse
import os
from datetime import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--filetoread', '-f', metavar='filetoread', default = './file.csv',
                        help='csv file to read. Default = "%(default)s"')

    parser.add_argument('--saveimage', '-s', metavar='PATH-TO-SAVE-TO', default = None,
                        help='specify the path in wich save the result heatmap. If not specified, the script doesn\'t save the image ')
    parser.add_argument('--imageformat', '-format', metavar='IMAGE FORMAT', default = 'png', choices = ['png', 'svg', 'pdf'],
                        help='specify the format of the saved image. Choices are %(choices)s. Default = "%(default)s" ')

    return parser

def make_dir(dirName):
    try:
        os.makedirs(dirName)
    except FileExistsError:
        print(f'la cartella {dirName} è già presente')


def get_time_stamp_indexes(csvFileToRead):
    """
        this function return the two indexes of 'TIME_STAMP_1' and 'TIME_STAMP_2'
        based on the field of the csvfile passed.
        return None if not found
    """
    with open(csvFileToRead, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        field = next(reader)
        try:
            return field.index('TIME_STAMP_1'), field.index('TIME_STAMP_2')
        except ValueError as e:
            print('TIME_STAMP_1 and TIME_STAMP_1 not found')
            return None


def get_similarity_index(csvFileToRead):
    """
        this function return the 'SIMILARITY [%]' index
        based on the field of the csvfile passed.
        return None if not found
    """
    with open(csvFileToRead, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        field = next(reader)
        try:
            return field.index('SIMILARITY [%]')
        except ValueError as e:
            print('SIMILARITY [%] index not found')
            return None


def get_date_lists(csvFileToRead):
    """
        Return two sorted date list containing all date contained in the two
        columns of csvFileToRead that contain the timestamp
    """

    timeStampIndex1, timeStampIndex2 = get_time_stamp_indexes(csvFileToRead)

    with open(csvFileToRead, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        firstDateList = []
        secondDateList = []
        field = next(reader)

        for row in reader:

            if (not row[timeStampIndex1] in firstDateList):
                firstDateList.append(row[timeStampIndex1])
            if (not row[timeStampIndex2] in secondDateList):
                secondDateList.append(row[timeStampIndex2])

        firstDateList.sort(reverse = True)
        secondDateList.sort()

        return firstDateList, secondDateList

def get_similarity_matrix(csvFileToRead):
    """ Return tree matrices containing the similiraity percentage result
        retrieved from the csv file passed.
        The first matrix contain the mean between the two percentage
        the second contain the similarity percentage of the first file
        compared to the second, while the third matrix contain the similarity
        percentage of the second file compared to the first.

    """

    timeStampIndex1, timeStampIndex2 = get_time_stamp_indexes(csvFileToRead)
    similarityIndex = get_similarity_index(csvFileToRead)

    if(timeStampIndex1 is None or timeStampIndex2 is None or similarityIndex is None):
        print('File csv incopatible, must have the above index not found')
        return None

    firstDateList, secondDateList = get_date_lists(csvFileToRead)
    simMatrix = np.zeros((len(firstDateList), len(secondDateList)))

    print(simMatrix.shape)

    with open(csvFileToRead, newline = '') as csvfile:
        csvLineList = list(csv.reader(csvfile))
        for row in csvLineList:
            try:
                xIndex = firstDateList.index(row[timeStampIndex1])
                yIndex = secondDateList.index(row[timeStampIndex2])
            except ValueError as e:
                print(f'{row[timeStampIndex1]} and {row[timeStampIndex2]} not found')
                continue
            simMatrix[xIndex][yIndex] = float(row[similarityIndex])

    print(simMatrix)

    return simMatrix


def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (M, N).
    row_labels
        A list or array of length M with the labels for the rows.
    col_labels
        A list or array of length N with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # Show all ticks and label them with the respective list entries.
    # ax.set_xticks(np.arange(data.shape[1]), labels=col_labels, fontsize = 'small')
    # ax.set_yticks(np.arange(data.shape[0]), labels=row_labels, fontsize = 'small')
    ax.set_xticks([])
    ax.set_yticks([])

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    # ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def main():
    parser = init_argparser()
    args = parser.parse_args()
    destFile = args.filetoread
    pathToSaveImage = args.saveimage
    imageFormat = args.imageformat

    csvFileName = (Path(destFile).name).split('.')[0]

    firstDateList, secondDateList = get_date_lists(destFile)

    percSimMatrix = get_similarity_matrix(destFile)

    if(percSimMatrix is None):
        quit()

    fig, ax = plt.subplots()

    cmap = mpl.colors.ListedColormap(["lightcyan", "aquamarine", "springgreen",
                                    "greenyellow", "yellow", "gold", "darkorange",
                                    "orangered", "red", "darkred"])

    cbar_kw = { 'ticks': [x for x in range(0,110,10)], 'drawedges': True }

    im, cbar = heatmap(percSimMatrix, firstDateList, secondDateList, ax=ax,
                       cmap=cmap, cbar_kw = cbar_kw, vmin = 0.0, vmax = 100.0, cbarlabel="Percentage of similarity [%]")

    font = {'weight': 'semibold',
            'size': '28.0'
            }
    title = fig.suptitle(csvFileName+' - SIMILARITY', verticalalignment = "top", fontproperties = font )
    title.set(color = 'darkred')

    ax.set_ylabel(csvFileName.split('_')[0] , color = 'mediumblue', fontsize = 24.0)
    ax.set_xlabel(csvFileName.split('_')[1] , color = 'mediumblue', fontsize = 24.0)

    fig.set_size_inches(24, 18)

    if (pathToSaveImage is not None):
        print(f'Saving image into {pathToSaveImage}')
        make_dir(pathToSaveImage)
        plt.savefig(os.path.join(pathToSaveImage, csvFileName+'.'+imageFormat),
                format = imageFormat, dpi = 300.0)

    plt.show()



if __name__ == '__main__':
    main()
