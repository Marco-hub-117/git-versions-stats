from pathlib import Path

from supportModules.csvSupport import init_csv_file, add_rows_to_csv
from supportModules.compareCode.compare_code import compare_code


def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--firstdir', '-f', metavar='firstdir', default = './first',
                        help='First directory containing .c file to compare. Default = "%(default)s"')
    parser.add_argument('--seconddir', '-s', metavar='seconddir', default = './second',
                        help='second directory containing .c file to compare. Default = "%(default)s"')
    parser.add_argument('--outdir', '-o', metavar='outdir', default = './script_moss_compare',
                            help='Output directory containing the csv file with compare results. Default = "%(default)s"')
    return parser



def main():
    parser = init_argparser()
    args = parser.parse_args()
    firstDir = args.firstdir
    secondDir = args.seconddir
    outdir = args.outdir

    if (not Path(firstDir).is_dir()):
        print(f"Attention, {firstDir} doesn't exist")
    elif (not Path(secondDir).is_dir()):
        print(f"Attention, {secondDir} doesn't exist")
    else :
        ######
        print("ALL COMPARISON COMPLETED")

    quit()


if __name__ == '__main__':
    main()
