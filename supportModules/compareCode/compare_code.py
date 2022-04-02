from supportModules.compareCode.code_tokenizer import tokenize

import ntpath
import subprocess


def compare_code(source1, source2, reformat_file_path):
    dst1 = reformat_code(source1, reformat_file_path)
    dst2 = reformat_code(source2, reformat_file_path)
    output = run_command(dst1, dst2)
    differences = filter_difference(output.splitlines())
    add_tokens, remove_tokens = calculate_tokens_difference(differences)

    return add_tokens, remove_tokens


def reformat_code(source_code, reformat_file_path):
    result = tokenize(source_code)
    # reformat_code_path = "./reformat_files/" + reformat_file_name(source_code)
    reformat_code_path = get_reformat_path(source_code, reformat_file_path)
    write_reformat_source(reformat_code_path, result)

    return reformat_code_path


def get_reformat_path(source_code, reformat_file_path):
    if reformat_file_path != None:
        return reformat_file_path + "/" + reformat_file_name(source_code)
    else:
        return "./reformat_files/" + reformat_file_name(source_code)


def reformat_file_name(src_path):
    filename = ntpath.basename(src_path)
    return "reformat_" + filename


def write_reformat_source(filename, code_lines):
    with open(filename, 'w+') as wf:
        for line in code_lines:
            wf.write(f'{line}\n')


def run_command(source1, source2):
    process = subprocess.run(['diff', '-u', source1, source2],
                             stdout=subprocess.PIPE, universal_newlines=True)
    return process.stdout


def filter_difference(lines):
    filter_header_lines = filter(lambda line: not line.startswith(
        '---') and not line.startswith('+++'), lines)
    filter_difference = filter(lambda line: line.startswith(
        '-') or line.startswith('+'), filter_header_lines)

    return filter_difference


def calculate_tokens_difference(differences):
    add_tokens = 0
    remove_tokens = 0
    for difference in differences:
        if difference.startswith('-'):
            remove_tokens = remove_tokens + 1
        elif difference.startswith('+'):
            add_tokens = add_tokens + 1
        else:
            print('problem to recognize the difference.')

    return add_tokens, remove_tokens
