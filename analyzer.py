import os
import io
import subprocess
import argparse
import pygit2
from datetime import datetime
from pathlib import Path
from shutil import copy

class CommitInfo:
    def __init__(self, hex, date):
        self.hex = hex
        self.date = date

def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    #parser.add_argument('body', action="store", type=str,
    #                    help="Text file containing the body of the message")
    parser.add_argument('--workdir', '-d', metavar='workdir', default = '.',
                        help='Directory containing the git repository. Default = "%(default)s"')
    parser.add_argument('--outputdir', '-o', metavar='outdir', default = './analyzerOutput',
                            help='Directory containing the output. Default = "%(default)s"')
    return parser

def make_dir(dirName):
    try:
        os.mkdir(dirName)
    except FileExistsError:
        print('la cartella {dirName} è già presente')

def get_all_commit_info(repDirectory):
    """ Return a list of CommitInfo object conteined in repDirectory
        Return an empty list if repDirectory isn't a repository """
    commit_info_list = []
    if pygit2.discover_repository(repDirectory) is None:
        return commit_info_list

    repo = pygit2.Repository(repDirectory)
    last = repo[repo.head.target]
    for commit in repo.walk(last.id, pygit2.GIT_SORT_TIME):
        date = datetime.fromtimestamp(commit.commit_time)
        commit_info = CommitInfo(commit.hex,date.strftime("%Y-%m-%d_%H-%M-%S"))
        commit_info_list.append(commit_info)

    return commit_info_list

def copy_all_committed_file(repDirectory='.',outDirectory='analyzerOutput'):
    """ Copy all commited file '.c' contained in repDirectory into outDirectory
        Return True if the copy succeed"""
    if pygit2.discover_repository(repDirectory) is None:
        return False
    all_commit_info = get_all_commit_info(repDirectory)
    repo = pygit2.Repository(repDirectory)
    for commit_info in all_commit_info:
        repo.checkout_tree(repo.get(commit_info.hex))
        fileList = list(Path(repDirectory).glob('**/*.c'))
        for src in fileList:
            destFilenName = os.path.join(outDirectory,commit_info.date+'_'+commit_info.hex+'.c')
            copy(src,destFilenName)
        repo.reset(all_commit_info[0].hex,pygit2.GIT_RESET_HARD)
    return True

def temp_func(workdir='.'):

    os.chdir('./fileCompilati')
    fileList = os.listdir('./') # ottengo i nomi di tutti i file ottenuti grazie ai comandi git sopra

    for fileName in fileList:
        outName = 'out'+fileName[0:-2]
        subprocess.run(['gcc', '-Wall', fileName, '-o', outName]) # compilo il programma

def main():
    parser = init_argparser()
    args = parser.parse_args()
    workdir = args.workdir
    #temp_func(workdir)
    outdir = args.outputdir
    if (copy_all_committed_file(workdir,outdir)):
        print("The copy was succesful")
    else:
        print("Copy failed")

if __name__ == '__main__':
    main()
