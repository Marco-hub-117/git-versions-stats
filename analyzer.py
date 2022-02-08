import os
import io
import subprocess
import argparse


def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    #parser.add_argument('body', action="store", type=str,
    #                    help="Text file containing the body of the message")
    parser.add_argument('--workdir', '-d', metavar='workdir',
                        help='Directory containing the git repository.')
    return parser


def temp_func(workdir='.'):
    os.chdir(workdir) # Passo alla directory che contiene il repository

    try:
        os.mkdir('fileCompilati') # Creo una cartella in cui metterò i file compilati
    except FileExistsError:
        print('la cartella è già presente')

    # Con la seguente linea di codice chiamo il comando "git reflog".
    # l'output del comando su console sarà salvato in completedProc.stdout
    completedProc = subprocess.run(['git', 'reflog'], capture_output = True,text = True)

    hashList = [] # inizializzo la lista che conterrà tutti gli hash commit
    for reflogLine in completedProc.stdout.splitlines():
        # Ottengo in una lista tutte le parole restituite in una linea dal comando git reflog
        # La prima parola (wordsList[0]) conterrà l´hash del commit
        wordsList = reflogLine.split(' ')
        hashList.append(wordsList[0])

    count = 0 # count --> variabile utile per creare nomi dei file
    comando = ['git', 'diff-tree','--no-commit-id','--name-only', '-r', ''] # l'ultimo elemento conterrà il commit hash
    for eachHash in hashList:
        comando[5] = eachHash
        # chiamo il comando git che mi restituisce tutti i nomi dei file modificati nel dato commit hash
        # il risultato viene salvato in completedProc.stdout
        completedProc = subprocess.run(comando, capture_output = True, text = True)
        fileNameList = [] # la lista conterrà tutti i nomi dei file modificati nel dato commit hash
        for fileName in completedProc.stdout.splitlines():
            fileNameList.append(fileName)

        for fileName in fileNameList:	# per tutti i nomi dei file trovati sopra
            if (fileName[-2:] == '.c'): # controllo che il nome del file termini in '.c'
                            # con il seguente comando git ottengo il contenuto del file nel particolare commit hash specificato
                            # redirigo l'output su un file .c nella directory fileCompilati
                            # il nome del file ottenuto sarà program-{count}.c , con count che indica quanto un file è meno recente
                            # -0 indica il file ottenuto con l'ultimo commit, mentre andando avanti avrò i file dei commit meno recenti
                os.system(f'git show {eachHash}:{fileName} > fileCompilati/program-{count}.c')
                count += 1

    os.chdir('./fileCompilati')
    fileList = os.listdir('./') # ottengo i nomi di tutti i file ottenuti grazie ai comandi git sopra

    for fileName in fileList:
        outName = 'out'+fileName[0:-2]
        subprocess.run(['gcc', '-Wall', fileName, '-o', outName]) # compilo il programma


def main():
    parser = init_argparser()
    args = parser.parse_args()
    if args.workdir is None:
        workdir = '.'
    else:
        workdir = args.workdir
    temp_func(workdir)


if __name__ == '__main__':
    main()

