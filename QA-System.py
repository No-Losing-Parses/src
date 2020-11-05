import sys
import os
import nltk
from nltk.corpus import stopwords
from spacy.matcher import Matcher
from spacy.lang.en import stop_words
import spacy

from spacy.lang.en import English

# token attrs:
# - token.i: index
# - token.text: word
# - token.is_alpha: whether or not the text is alphabetical
# - token.is_punct: whether or not the text is punctuation
# - token.like_num: whether or not the text is numerical
# - token.pos_: predicted part-of-speech for the text
# - token.dep_: predicted dependency label
# - token.head: parent token

# doc attrs:
# - doc[i] = token at index i of doc
# - doc[i:j] = a span of tokens, can be treated as one token
# - doc.ents = predicted named entities of a document

# entity attrs:
# - ent.text: word
# - ent.label_: what the entity is

# matcher attrs:
# - [{'TEXT': 'iPhone'}, {'TEXT': 'X'}]: Match exact token texts
# - [{'LOWER': 'iPhone'}, {'LOWER': 'x'}]: Match lexical attributes
# - [{'LEMMA': 'buy'}, {'POS': 'NOUN'}]: Match any token attributes
# - OP: ! (match 0 times), ? (match 0 or 1 times), + (match 1 or more times), * (match 0 or more times)
# - matcher.add(<name of pattern>, <callback>, <pattern>)

# spacy abilities:
# - spacy.explain('GPE'): Countries, cities, states
# - spacy.explain('NNP'): noun, proper singular

# linguistic attributes in context:
# - pos tags
# - syntactic dependencies
# - named entities
#   - can be updated to perform better on our specific data

from collections import OrderedDict




class Story:
    def __init__(self, story_id, headline, date, text):
        self.story_id = story_id
        self.headline = headline
        self.date = date
        self.text = text
        self.entities = [(ent.text, ent.label_) for ent in self.text.ents]

    def print_attrs(self):
        print(f'STORYID: {self.story_id}')
        print(f'HEADLINE: {self.headline}')
        print(f'DATE: {self.date}')
        print(f'ENTITIES: {self.entities}')
        print(f'TEXT: {self.text.text}\n')


class Question:
    def __init__(self, question_id, question, difficulty, story):
        self.question_id = question_id
        self.question = question
        self.difficulty = difficulty
        self.story = story
        self.answer = ""
        self.entities = [(ent.text, ent.label_) for ent in self.question.ents]

    def print_attrs(self):
        print(f'QUESTIONID: {self.question_id}')
        print(f'QUESTION: {self.question.text}')
        print(f'ENTITIES: {self.entities}')
        print(f'DIFFICULTY: {self.difficulty}')
        print(f'ANSWER: {self.answer}')
        print(f'STORYID: {self.story.story_id}\n')


def read_file_lines(fp):
    with open(fp) as file:
        return [line.strip() for line in file.readlines()]


def main():
    nlp_engine = spacy.load('en_core_web_md')
    matcher = Matcher(nlp_engine.vocab)

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
        storyfile_name = f'{line_i}.story'
        storyfile_lines = read_file_lines(storyfile_name)

        headline, date = ' '.join(storyfile_lines[0].split(': ')[1:]), storyfile_lines[1].split(': ')[1]
        story_id, text = storyfile_lines[2].split(': ')[1], ' '.join(storyfile_lines[6:])
        story = Story(story_id, headline, date, nlp_engine(text))

        stories[story_id] = story

        # getting questions from questions file
        questionsfile_name = f'{line_i}.questions'
        questionsfile_lines = read_file_lines(questionsfile_name)

        all_questions = [questionsfile_lines[i:i+3] for i in range(0, len(questionsfile_lines), 4)]

        # go through all question lines and add them to our questions
        for j, line_j in enumerate(all_questions):
            question_id = line_j[0].split(': ')[1]
            question_asked = ' '.join(line_j[1].split(': ')[1:])
            difficulty = line_j[2].split(': ')[1]
            question = Question(question_id, nlp_engine(question_asked), difficulty, story)

            if story_id in questions:
                questions[story_id].append(question)
            else:
                questions[story_id] = [question]



        # for story_i in stories:
        #     stories[story_i].print_attrs()
        #
        # for question_file_i in questions:
        #     for question_i in questions[question_file_i]:
        #         question_i.print_attrs()


if __name__ == "__main__":
    main()


