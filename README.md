# Git Versions Stats
This repository contain three different script:
- analyzer.py used to extract source code from Git repository
- compareWithMoss.py used to send moss comparison between source code and to save the information retrieved into a csv file
- heatMapGenerator.py used to visualize the csv file generated from the previous script into a heatmap

# analyzer.py
Here a list of possible command and option for analyzer.py

**usage**: analyzer.py [-h] [--workdir workdir] [--outputdir outdir] [--fileSearched [FILESEARCHED ...]]

The following command show the help message

`python3 analyzer.py --help`

- The option `--workdir workdir` is used to specify the path containining the repository from wich to extract all commited file searched. (default is ".")

- The option `--outputdir outdir` is used to specify the path that will contain the extracted source code (deafult is "./analyzerOutput"). The extracted source code name has the following format: `date-string_commit-hex_original-sorce-code-name`

- The option `[--fileSearched [FILESEARCHED ...]]` is used to specify the name of the file you need to extract from the repository. By default is "*.c", so the script will extract all *.c source code committed. The arguments must be enclosed into quotes .You can specify more than one file name, for example `analyzer.py --fileSearched '*.c' '*.py' 'file-testo.txt'` will search all committed file, that match one of the fileSerached argument, extracted from the git repository contained into '.' path, and will save them into ./analyzerOutput directory. In this example the script will extract all commited file that end with _.c_ and _.py_, and all committed files with the exact following name _file-testo.txt_
