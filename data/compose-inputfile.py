import os
import sys
import glob


def read_from_file(input_fp):
    with open(input_fp, 'r') as file:
        return file.readlines()


def write_to_inputfile(output_fp, first_line, lines):
    with open(output_fp, 'w') as file:
        file.write(f'{first_line}\n')

        for i, line in enumerate(lines):
            if i == len(lines) - 1:
                file.write(line)
            else:
                file.write(f'{line}\n')


def write_to_answerkeyfile(output_fp, answers):
    with open(output_fp, 'w') as file:
        for excerpt in answers:
            for line in excerpt:
                file.write(line)


def first_sort_key(fname):
    return int(fname.split('-')[0])


def second_sort_key(fname):
    story_type = fname.split('-')[1]

    return int(story_type[1:3])


def third_sort_key(fname):
    return int(fname.split('-')[2])


os.chdir(sys.argv[1])
files = [file.split('.')[0] for file in glob.glob('*.story')]
sorted_files = sorted(files, key=lambda x: (first_sort_key(x), second_sort_key(x), third_sort_key(x)))
all_answers = []

for file in sorted_files:
    file_lines = read_from_file(f'{file}.answers')
    all_answers.append(file_lines)

write_to_inputfile(f'../{sys.argv[1]}-inputfile.txt', f'./data/{sys.argv[1]}', sorted_files)
write_to_answerkeyfile(f'../{sys.argv[1]}-answerkey.answers', all_answers)
