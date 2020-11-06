import sys
import os
import spacy
from spacy.matcher import Matcher
from spacy.lang.en import stop_words
from nltk.corpus import wordnet
import nltk
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
        self.sentences = list(self.text.sents)

    def print_attrs(self):
        print(f'STORYID: {self.story_id}')
        print(f'HEADLINE: {self.headline}')
        print(f'DATE: {self.date}')
        print(f'ENTITIES: {self.entities}')
        print(f'TEXT: {self.text.text}\n')
        print(f'SENTENCES: {self.sentences}\n')


class Question:
    def __init__(self, question_id, question, difficulty, story):
        self.question_id = question_id
        self.question = question
        self.difficulty = difficulty
        self.story = story
        self.type = None
        self.answer_type = None
        self.answer = ""
        self.entities = [(ent.text, ent.label_) for ent in self.question.ents]
        self.types = {
            'WHO': {'whom', 'who', 'whose'},
            'WHAT': ['what'],
            'WHEN': ['when'],
            'WHY': ['why'],
            'WHICH': ['which'],
            'WHERE': ['where'],
            #wordnet can be used to gather similar words to this
            'MEASURE': {
                'many', 'much',
                'often', 'few',
                'long', 'short', 'tall', 'fast', 'slow',
                'high', 'low',
                'big', 'small',
                'close', 'near', 'far',
                'new', 'old',
                'heavy', 'light'
                },
            'HOW': ['how'],
        }
        self.measure_map = {
            'many': ['CARDINAL', 'QUANTITY', 'PERCENT'], #'QUANTITY'
            'much': ['MONEY', 'QUANTITY', 'PERCENT'],
            'often': ['TIME', 'DATE', 'PERCENT'],
            'few': ['QUANTITY', 'CARDINAL'],
            'long': ['TIME', 'DATE', 'QUANTITY'],
            'close': ['TIME', 'DATE', 'QUANTITY'],
            'near': ['TIME', 'DATE', 'QUANTITY'],
            'far': ['TIME', 'DATE', 'QUANTITY'],
            'new': ['TIME', 'DATE'],
            'old': ['TIME', 'DATE'],
            'heavy': ['QUANTITY'],
            'light': ['QUANTITY'],
            'short': ['QUANTITY'],
            'tall': ['QUANTITY'],
            'fast': ['QUANTITY'],
            'slow': ['QUANTITY'],
            'big': ['QUANTITY', 'PERCENT', 'CARDINAL'],
            'small': ['QUANTITY', 'PERCENT', 'CARDINAL'],
            'high': ['QUANTITY', 'CARDINAL'],
            'low': ['QUANTITY', 'CARDINAL']
        }
        self.answer_types = {
            'WHO': {'PERSON', 'NORP', 'ORG', 'GPE'},
            #'WHAT': [''], what time is it? what is an iphone? what was the war?
            'WHEN': {'TIME', 'DATE'},
            #'WHY': [] usually what comes after because
            #'WHICH': [] could really be any of the types
            'WHERE': {'LOC', 'FAC', 'ORG', 'GPE', 'PRODUCT', 'EVENT'},
            'MEASURE': {} #'PERCENT', 'MONEY', 'QUANTITY', 'CARDINAL', 'ORDINAL'
            #'HOW': []
        }
        self.decide_on_question_type()

    def print_attrs(self):
        print(f'QUESTIONID: {self.question_id}')
        print(f'QUESTION: {self.question.text}')
        print(f'QUESTION_TYPE: {self.type}')
        print(f'ANSWER_TYPE: {self.answer_type}')
        print(f'ENTITIES: {self.entities}')
        print(f'DIFFICULTY: {self.difficulty}')
        print(f'ANSWER: {self.answer}')
        print(f'STORYID: {self.story.story_id}\n')

    def decide_on_question_type(self):
        question = self.question.text.lower()
        for q_type in self.types:
            for expression in self.types[q_type]:
                if expression in self.types['MEASURE']:
                    if expression in question and 'how' in question:
                        self.type = q_type
                        if q_type in self.answer_types:
                            self.answer_type = self.measure_map[expression]
                        break
                elif expression in question:
                    self.type = q_type
                    if q_type in self.answer_types:
                        self.answer_type = self.answer_types[q_type]
                    break
            if self.type:
                break


def read_file_lines(fp):
    with open(fp) as file:
        return [line.strip() for line in file.readlines()]


def print_responses(questions):
    for i, question in enumerate(questions):
        print(f'QuestionID: {question.question_id}')
        print(f'Answer: {question.answer}\n')


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
            words_from_question_non_syms = set([
                word for word in question.question if not word.is_stop and (word.is_alpha or word.is_digit or word.is_currency or not word.is_punct)
                ])
            verbs_from_question_non_syms = set([
                word for word in question.question if not word.is_stop and word.pos_ == 'VERB'
                ])
            words_from_question = set()
            verbs_from_question = set()
            for word in words_from_question_non_syms:
                #did this help TODO
                for syn in wordnet.synsets(word.lemma_):
                    for lm in syn.lemmas():
                        name = lm.name().split('_')
                        for spot in name:
                            if spot not in spacy.lang.en.stop_words.STOP_WORDS:
                                words_from_question.add(spot.lower())
                words_from_question.add(word.lemma_.lower())

            for word in verbs_from_question_non_syms:
                #did this help TODO
                #if word.pos_ == 'VERB':
                for syn in wordnet.synsets(word.lemma_):
                    for lm in syn.lemmas():
                        name = lm.name().split('_')
                        for spot in name:
                            if spot not in spacy.lang.en.stop_words.STOP_WORDS:
                                verbs_from_question.add(spot.lower())
                verbs_from_question.add(word.lemma_.lower())

            # selected_np = None
            # for np in question.question.noun_chunks:
            #     if np.text not in stop_words.STOP_WORDS and np.text.upper() not in question.answer_types.keys():
            #         selected_np = set(np.text.lower().split())
            #         break

            noun_phrases_from_question = list(set(nc.text.lower().split()) for nc in question.question.noun_chunks)

            # question.print_attrs()
            #print(words_from_question)
            scores = []
            high_score = 0
            for sentence in story.sentences:
                words_from_sentence = set([
                word.lemma_.lower() for word in sentence if not word.is_stop and (word.is_alpha or word.is_digit or word.is_currency or not word.is_punct)
                ])
                verbs_from_sentence = set([
                word.lemma_.lower() for word in sentence if not word.is_stop and word.pos_ == 'VERB'
                ])

                # selected_np = None
                # for np in list(noun_phrases_from_question):
                #     if np.text.upper() in question.type:
                #         continue
                #     else:
                #         selected_np = set(np.text.split())
                #         break

                # question types
                sentence_entities = [(entity.text, entity.label_) for entity in sentence.ents]

                noun_phrases_from_sentence = list(set(nc.text.lower().split()) for nc in sentence.noun_chunks)
                given_score = len(words_from_sentence.intersection(words_from_question))
                #maybe to big of verb weight
                given_score += len(verbs_from_question.intersection(verbs_from_sentence)) * 3 #verb weight
                #did not help I dont thing
                for nps in noun_phrases_from_sentence:
                    for npq in noun_phrases_from_question:
                        given_score += len(nps.intersection(npq)) * 5

                # print(noun_phrases_from_question[0])
                # for sentence_noun_phrase in noun_phrases_from_sentence:
                #     for question_noun_phrase in noun_phrases_from_question:
                #         given_score += len(sentence_noun_phrase.intersection(question_noun_phrase))*2 #noun phrase weight

                if question.type == 'WHEN':
                    index = len(sentence_entities) + 2 if len(sentence_entities) + 2 > 7 else 7
                    found = False
                    for entity in sentence_entities:
                        if entity[1] in question.answer_type and entity[0] not in question.question.text:
                            given_score += 7*index #when weight
                            found = True
                            break
                        index -= 1
                    if not found:
                        given_score = 0
                if question.type == 'WHERE':
                    index = len(sentence_entities) + 2 if len(sentence_entities) + 2 > 7 else 7
                    found = False
                    for entity in sentence_entities:
                        if entity[1] in question.answer_type and entity[0] not in question.question.text:
                            given_score += 7*index #when weight
                            found = True
                            break
                        index -= 1
                    if not found:
                        given_score = 0
                if question.type == 'WHO':
                    index = len(sentence_entities) + 2 if len(sentence_entities) + 2 > 7 else 7
                    found = False
                    for entity in sentence_entities:
                        if entity[1] in question.answer_type and entity[0] not in question.question.text:
                            given_score += 7*index #when weight
                            found = True
                            break
                        index -= 1
                    if not found:
                        given_score = 0
                if question.type == 'MEASURE':
                    index = len(sentence_entities) + 2 if len(sentence_entities) + 2 > 5 else 5
                    found = False
                    for entity in sentence_entities:
                        if entity[1] in question.answer_type and entity[0] not in question.question.text:
                            given_score += 5*index #when weight
                            found = True
                            break
                        index -= 1
                    if not found:
                        given_score = 0
                if given_score > high_score:
                    high_score = given_score
                scores.append(given_score)
            #print(words_from_question)
            # print(question.question)
            for i, score in enumerate(scores):
                if score == high_score:
                    question.answer = story.sentences[i]
                    # print([(ent.text, ent.label_) for ent in story.sentences[i].ents])

        #for story_i in stories:
        #     stories[story_i].print_attrs()


    for question_file_i in questions:
        print_responses(questions[question_file_i])


if __name__ == "__main__":
    main()


