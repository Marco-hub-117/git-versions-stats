# Git Versions Stats
This repository contain three different script:
- analyzer.py used to extract source code from Git repository
- compareWithMoss.py used to send moss comparison between source code and to save the information retrieved into a csv file
- heatMapGenerator.py used to visualize the csv file generated from the previous script into a heatmap

# analyzer.py 
<details><summary>analyzer.py used to extract source code from Git repository (Click to expand) </summary>
------------------------------------------------------------------------------------------------------------

Here a list of possible command and option for analyzer.py

The following command show the **help** message: `python3 analyzer.py --help`

**usage**: analyzer.py [-h] [--workdir workdir] [--outputdir outdir] [--fileSearched [FILESEARCHED ...]]

- The option `--workdir workdir` ( -d is the short version of the command ) is used to specify the path containining the repository from wich to extract all commited file searched. (default is ".")

- The option `--outputdir outdir` ( -o is the short version of the command ) is used to specify the path that will contain the extracted source code (deafult is "./analyzerOutput"). The extracted source code name has the following format: `date-string_commit-hex_original-source-code-name`

- The option `[--fileSearched [FILESEARCHED ...]]` ( -fs is the short version of the command ) is used to specify the name of the file you need to extract from the repository. By default is "*.c", so the script will extract all *.c source code committed. The arguments must be enclosed into quotes .You can specify more than one file name, for example `analyzer.py --fileSearched '*.c' '*.py' 'file-testo.txt'` will search all committed file, that match one of the fileSearched argument, extracted from the git repository contained into '.' path, and will save them into ./analyzerOutput directory. In this example the script will extract all commited file that end with _.c_ and _.py_, and all committed files with the exact _file-testo.txt_ name

The following is a **summary example** for analyzer.py:

`python3 analyzer.py -d path-to-git-rep -o example-analyzer-output -fs '*.py'`

The following command will extract all the *.py command commited into path-to-git-rep repository and will save them into example-analyzer-output directory 
</details>



# compareWithMoss.py
<details><summary>compareWithMoss.py used to send moss comparison between source code and to save the information retrieved into a csv file (Click to expand)</summary>

---------------------------------------------------------------------------------------------------------------------------------------

Here a list of possible command and option for compareWithMoss.py

The script compare all .c source code contained into first directory passed with all the .c source code contained into second directory passed, sending moss request and retrieving the result from the resulting moss web page. 

It will save the result into a **csv file** with the following **field**: 

- ['FILE_NAME_1', 'FILE_NAME_2', 'TIME_STAMP_1', 'TIME_STAMP_2', 'RESULT_URL', 'PERC_SIM_1 [%]', 'PERC_SIM_2 [%]', 'LINES_MATCHES']

The **resulting csv** has the following **name** format: _firstDirName_secondDirName.csv_

When the script start it search into output directory if a csv file with the same name is already present and ask if you want to overwrite that file. If you don't the script automatically search into that csv file all missing comparison, start to send moss requests of this missing comparison and append the result into that csv file.


The following command show the **help** message: `python3 compareWithMoss.py --help`

**usage**: `compareWithMoss.py [-h] [--firstdir firstdir] [--seconddir seconddir] [--outdir outdir]`

- The option `--firstdir firstdir` is used to specify the first directory that contain c source code

- The option `--seconddir seconddir` is used to specify the second directory that contain c source code

- The option `--outdir outdir` is used to specify the output directory that will contain the csv result file
</details>





#  heatMapGenerator.py

You may need to run `sudo apt-get install python3-tk` to show the pyplot figure gui
