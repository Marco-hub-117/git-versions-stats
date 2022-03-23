import csv
import argparse
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
    return parser

def get_date_lists(csvFileToRead):
    """
        Return two sorted date list containing all date contained in the two
        columns of csvFileToRead that contain the timestamp
    """
    with open(csvFileToRead, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        firstDateList = []
        secondDateList = []
        field = next(reader)

        for row in reader:

            if (not row[2] in firstDateList):
                firstDateList.append(row[2])
            if (not row[3] in secondDateList):
                secondDateList.append(row[3])

        firstDateList.sort(reverse = True)
        secondDateList.sort(reverse = True)

        return firstDateList, secondDateList

def get_sim_matrices(csvFileToRead):
    """ Return tree matrices containing the similiraity percentage result
        retireved from the csv file passed.
        The first matrix contain the mean between the two percentage
        the second contain the similarity percentage of the first file
        compared to the second, while the third matrix contain the similarity
        percentage of the second file compared to the first.

    """

    firstDateList, secondDateList = get_date_lists(csvFileToRead)
    simMeanMatrix = np.zeros((len(firstDateList), len(secondDateList)))
    simOneMatrix = np.zeros((len(firstDateList), len(secondDateList)))
    simTwoMatrix = np.zeros((len(firstDateList), len(secondDateList)))

    print(simMeanMatrix.shape)

    with open(csvFileToRead, newline = '') as csvfile:
        csvLineList = list(csv.reader(csvfile))

        for i in range (0, len(firstDateList)):
            for j in range(0, len(secondDateList)):
                for row in csvLineList:
                    if (firstDateList[i] == row[2] and secondDateList[j] == row[3]):
                        simMeanMatrix[i][j] = (float(row[5]) + float(row[6])) / 2
                        simOneMatrix[i][j] = float(row[5])
                        simTwoMatrix[i][j] = float(row[6])
                        break

    print(simMeanMatrix)
    print(simOneMatrix)
    print(simTwoMatrix)

    return simMeanMatrix, simOneMatrix, simTwoMatrix


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
    ax.set_xticks(np.arange(data.shape[1]), labels=col_labels, fontsize = 'small')
    ax.set_yticks(np.arange(data.shape[0]), labels=row_labels, fontsize = 'small')

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

def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=("black", "white"),
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = mpl.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


def main():
    parser = init_argparser()
    args = parser.parse_args()
    destFile = args.filetoread

    csvFileName = (Path(destFile).name).split('.')[0]

    firstDateList, secondDateList = get_date_lists(destFile)

    percSimMatrix = get_sim_matrices(destFile)

    fig, ax = plt.subplots()

    cmap = mpl.colors.ListedColormap(["lightcyan", "aquamarine", "springgreen",
                                    "greenyellow", "yellow", "gold", "darkorange",
                                    "orangered", "red", "darkred"])

    cbar_kw = { 'ticks': [x for x in range(0,110,10)], 'drawedges': True }

    im, cbar = heatmap(percSimMatrix[0], firstDateList, secondDateList, ax=ax,
                       cmap=cmap, cbar_kw = cbar_kw, vmin = 0.0, vmax = 100.0, cbarlabel="Percentage similarity [%]")
    # texts = annotate_heatmap(im, valfmt="{x:.1f}", size = 6.0, threshold = 60.0)
    font = {'weight': 'semibold',
            'size': '24.0'
            }
    title = fig.suptitle(csvFileName+' - MEAN', verticalalignment = "center", fontproperties = font )
    title.set(color = 'darkred')

    ax.set_ylabel(csvFileName.split('_')[0], color = 'mediumblue', fontsize = 20.0)
    ax.set_xlabel(csvFileName.split('_')[1], color = 'mediumblue', fontsize = 20.0)

    plt.show()






if __name__ == '__main__':
    main()