import csv

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


def main():
    testList = [1, 2, 3, 4, 5]
    testList2 = [2, 3, 4, 5, 6, 7, 8]

    print(get_N_elements_from_list(testList, 3, sort = True))
    print(get_all_possible_comparison(testList, testList2))
    print(get_difference_between_list(testList, testList2))

    #print(retrieve_completed_comparison('../mainOutput/aa0612_ab0343_diff.csv'))




if __name__ == '__main__':
    main()
