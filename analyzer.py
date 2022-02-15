import os
import io
import subprocess
import argparse
import pygit2
from datetime import datetime
from pathlib import Path
import shutil
import tempfile
import glob

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
        os.makedirs(dirName)
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

def copy_all_committed_file_not_bare(repDirectory='.',outDirectory='analyzerOutput'):
    """ Copy all commited file '.c' contained in repDirectory into outDirectory
        repDirectory must contain a non-bare repository
        Return True if the copy succeed"""
    if pygit2.discover_repository(repDirectory) is None:
        return False
    if (not Path(outDirectory).exists()):
        make_dir(outDirectory)
    all_commit_info = get_all_commit_info(repDirectory)
    repo = pygit2.Repository(repDirectory)
    for commit_info in all_commit_info:
        repo.checkout_tree(repo.get(commit_info.hex))
        fileList = list(Path(repDirectory).glob('**/*.c'))
        for src in fileList:
            destFilenName = os.path.join(outDirectory,commit_info.date+'_'+commit_info.hex+'.c')
            shutil.copy(src,destFilenName)
        repo.reset(all_commit_info[0].hex,pygit2.GIT_RESET_HARD)
    return True

def copy_all_committed_file(repDirectory='.',outDirectory='analyzerOutput'):
    """ Copy all commited file '.c' contained in repDirectory into outDirectory
        repDirectory could be a bare repository
        Return True if the copy succeed"""
    if pygit2.discover_repository(repDirectory) is None:
        return False
    repo = pygit2.Repository(repDirectory)
    if repo.is_bare:
        with tempfile.TemporaryDirectory() as tmpdirname:
            repo_not_bare = pygit2.clone_repository(repo.path,tmpdirname)
            return copy_all_committed_file_not_bare(tmpdirname, outDirectory)
    else:
        return copy_all_committed_file_not_bare(repDirectory, outDirectory)

def compile_file(workdir):
    """
        Compile all .c file contained in workdir and put them into compiled_file
        directory contained in workdir directory.
    """
    # filList will contain the name of all file .c contained in workdir
    fileList = glob.glob(os.path.join(workdir,"*.c"))
    outDirName = os.path.join(workdir,"compiled_file")
    make_dir(outDirName) # create directory that will contain compiled file
    for fileName in fileList:
        baseFileName = os.path.basename(fileName)
        outName = os.path.join(outDirName,baseFileName[0:-2])
        subprocess.run(['gcc', '-Wall', fileName, '-o', outName]) # program compile

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

    compile_file(outdir)

if __name__ == '__main__':
    main()
