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
                        help='Directory containing the git repositories. Default = "%(default)s"')
    parser.add_argument('--outputdir', '-o', metavar='outdir', default = './analyzerOutput',
                            help='Directory containing the output. Default = "%(default)s"')
    return parser

def make_dir(dirName):
    try:
        os.makedirs(dirName)
    except FileExistsError:
        print(f'la cartella {dirName} è già presente')

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

def find_necessary_file(path, fileSearchedList):
    """
        Find all file that match an element of the list passed, contained into path passed
    """
    necessaryFile = []
    for fileSearched in fileSearchedList:
        for fileFound in Path(path).rglob(fileSearched):
            if '.git' in Path(fileFound).parts:
                continue
            if '.config' in Path(fileFound).parts:
                continue
            necessaryFile.append(fileFound)

    return necessaryFile

def copy_all_committed_file(repDirectory='.',outDirectory='analyzerOutput', fileSearchedList = ['*.c']):
    """ Copy all commited file that match an element of fileSearchedList
        contained in repDirectory into outDirectory.
        fileSearchedList could contain all the pathnames matching a specified
        pattern according to the rules used by the Unix shell.
        By default fileSerchedList contain only '*.c', so the function
        will copy all .c file commited into repDirectoy.
        repDirectory could be a bare repository.
        Return True if the copy succeed
    """

    if pygit2.discover_repository(repDirectory) is None:
        print(f'{repDirectoy} is not a repository')
        return False
    source_dir_name = "source_file"
    basename = Path(repDirectory).name
    outdir = os.path.join(outDirectory, basename, source_dir_name)
    if (not Path(outdir).exists()):
        make_dir(outdir)
    repo = pygit2.Repository(repDirectory)
    with tempfile.TemporaryDirectory() as tmpdirname:
        clonedRepo = pygit2.clone_repository(repDirectory, tmpdirname)
        last = clonedRepo[repo.head.target]
        all_commit_info = get_all_commit_info(tmpdirname)
        for commit_info in all_commit_info:
            clonedRepo.checkout_tree(clonedRepo.get(commit_info.hex))

            necessaryFile = find_necessary_file(tmpdirname, fileSearchedList)
            print('NECESSARY:', necessaryFile)
            print('####################')

            for src in necessaryFile:
                committedFileName = Path(src).name
                destFilenName = os.path.join(outdir, commit_info.date+'_'+commit_info.hex+'_'+committedFileName)
                shutil.copy(src, destFilenName)

            clonedRepo.reset(last.id, pygit2.GIT_RESET_HARD)

    return True

def copy_all_commit_from_all_repository(directoryWithReps='.',outDirectory='analyzerOutput'):
    """
        Copy al committed .c file contained in every repository contained
        in directoryWithReps argument.
        it will copy in outDirectory/{repositoryName}
        keeping the name of every repository contained in directoryWithReps
    """
    if directoryWithReps == '.':
        directoryWithReps = os.getcwd()
    for repPath in Path(directoryWithReps).iterdir():
        if not repPath.is_dir():
            continue
        if pygit2.discover_repository(repPath) is None:
            continue
        if os.path.basename(repPath) == ".git":
            # the following instruction replace repPath with the parent directroy
            # that contain the git repository, only if repPath is .git directory
            repPath = Path(os.path.dirname(repPath))

        outName = os.path.join(outDirectory,repPath.name)
        copy_all_committed_file(repPath, outName)

def compile_file(workdir):
    """
        Compile all .c file contained in workdir and put them into compiled_file
        directory contained in workdir directory.
    """
    # fileList will contain the name of all file .c contained in workdir
    fileList = glob.glob(os.path.join(workdir,"**/*.c"), recursive=True)
    outDirName = os.path.join(workdir,"compiled_file")
    make_dir(outDirName) # create directory that will contain compiled file
    for fileName in fileList:
        baseFileName = os.path.basename(fileName)
        outName = os.path.join(outDirName,baseFileName[0:-2])
        completedProc = subprocess.run(['gcc', '-Wall', fileName, '-o', outName]) # program compile
        print("RETURN CODE = ",completedProc.returncode)

def compile_all_file(workdir):
    """
        Compile all .c file contained in all sub-directory of workdir
        and put them into compiled_file directory contained in all
        sub-directory of workdir.
    """
    for sourceFilePath in Path(workdir).iterdir():
        compile_file(sourceFilePath)

def main():
    parser = init_argparser()
    args = parser.parse_args()
    workdir = args.workdir
    outdir = args.outputdir
    copy_all_committed_file(workdir, outdir)
    # compile_all_file(outdir)

if __name__ == '__main__':
    main()
