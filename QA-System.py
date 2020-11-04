import sys
import os

from collections import OrderedDict


class Story:
    def __init__(self, story_id, headline, date, text):
        self.story_id = story_id
        self.headline = headline
        self.date = date
        self.text = text

    def print_attrs(self):
        print(f'STORYID: {self.story_id}')
        print(f'HEADLINE: {self.headline}')
        print(f'DATE: {self.date}')
        print(f'TEXT: {self.text}\n')


class Question:
    def __init__(self, question_id, question, difficulty, story):
        self.question_id = question_id
        self.question = question
        self.difficulty = difficulty
        self.story = story
        self.answer = ""

    def print_attrs(self):
        print(f'QUESTIONID: {self.question_id}')
        print(f'QUESTION: {self.question}')
        print(f'DIFFICULTY: {self.difficulty}')
        print(f'ANSWER: {self.answer}')
        print(f'STORYID: {self.story.story_id}\n')


def read_file_lines(fp):
    with open(fp) as file:
        return [line.strip() for line in file.readlines()]


def main():
    inputfile_name = sys.argv[1]

    inputfile_lines = read_file_lines(inputfile_name)

    directory_path = inputfile_lines[0]

    # changing the direction so we will not need
    # to append it for future files
    os.chdir(directory_path)

    stories = OrderedDict()
    questions = OrderedDict()

    for i, line_i in enumerate(inputfile_lines[1:], start=1):
        # getting story from story file
        storyfile_name = line_i+".story"
        storyfile_lines = read_file_lines(storyfile_name)

        headline, date = ' '.join(storyfile_lines[0].split(': ')[1:]), storyfile_lines[1].split(': ')[1]
        story_id, text = storyfile_lines[2].split(': ')[1], ' '.join(storyfile_lines[6:])
        story = Story(story_id, headline, date, text)

        stories[story_id] = story

        # getting questions from questions file

        questionsfile_name = line_i+".questions"
        questionsfile_lines = read_file_lines(questionsfile_name)

        all_questions = [questionsfile_lines[i:i+3] for i in range(0, len(questionsfile_lines), 4)]

        # go through all question lines and add them to our questions
        for j, line_j in enumerate(all_questions):
            question_id = line_j[0].split(': ')[1]
            question_asked = ' '.join(line_j[1].split(': ')[1:])
            difficulty = line_j[2].split(': ')[1]
            question = Question(question_id, question_asked, difficulty, story)

            if story_id in questions:
                questions[story_id].append(question)
            else:
                questions[story_id] = [question]


if __name__ == "__main__":
    main()
