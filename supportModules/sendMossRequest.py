from threading import Thread
import time
import mosspy

userid = 719337169

class MossHandlingThread(Thread):

    def __init__(self, firstFileList, secondFileList, lang = 'c'):
        Thread.__init__(self)
        self.firstFileList = firstFileList
        self.secondFileList = secondFileList
        self.lang = lang
        self.result_url = None

    def run(self):
        self.result_url = init_moss_and_send(self.firstFileList, self.secondFileList, self.lang)

def summation(N):
    if N <= 0:
        return 0

    summation = 0
    for x in range(1, N+1):
        summation += x

    return summation

def get_ignore_limit(firstLen, secondLen):

    usefulComparison = firstLen*secondLen
    totalComparison = summation(firstLen+secondLen-1)
    unnecessaryComparison = totalComparison - usefulComparison

    return max(usefulComparison, unnecessaryComparison) + 10


def init_moss_and_send(firstFileList, secondFileList, lang = 'c'):
    """
        Init a mosspy.Moss object and send the comparison between
        all file contained in firstFileList and secondoFileList.
        return the result url
    """
    retries = 10
    timeout = 5 # timeout entity in seconds
    while True:
        m = mosspy.Moss(userid, lang)
        m.setIgnoreLimit(get_ignore_limit(len(firstFileList), len(secondFileList)))
        m.setNumberOfMatchingFiles(1000)

        for file in firstFileList:
            m.addFile(file)
        for file in secondFileList:
            m.addFile(file)

        try:
            result_url = m.send(lambda file_path, display_name: print('*', end='', flush=True))
            break
        except:
            # Questo blocco l´ho aggiunto perchè mi ha dato l'errore:
            # ConnectionResetError: [Errno 104] Connection reset by peer
            # Ma solo ogni tanto lo fa, non so come risolvere
            retries -= 1
            result_url = None
            time.sleep(5.0)
            if retries < 0:
                print("Errore nell'invio del gruppo:", firstFileList[0], secondFileList[0], 'ANNULLO')
                break
            else:
                print("Errore nell'invio del gruppo:", firstFileList[0], secondFileList[0], 'RIPROVO')

    return result_url

def main ():
    pass

if __name__ == '__main__':
    main()
