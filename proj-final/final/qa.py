import sys
import os
import spacy
from collections import OrderedDict
from spacy.lang.en import stop_words

import nltk
try:
    nltk.data.find('wordnet')
except LookupError:
    nltk.download('wordnet')

from nltk.corpus import wordnet


def prevent_sep_on_quotes(doc):
    is_open_quote = False
    sep = False

    for token in doc:
        if not sep:
            token.is_sent_start = False

        if token.text == '"':
            if is_open_quote:
                is_open_quote = False
            else:
                is_open_quote = True

        sep = not is_open_quote

    return doc


nlp_engine = spacy.load('en_core_web_md')
nlp_engine.add_pipe(prevent_sep_on_quotes, name='better-sentencizer', before='parser')

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
            'WHO': ['whom', 'who', 'whose'],
            'WHAT': ['what'],
            'WHEN': ['when'],
            'WHY': ['why'],
            'WHICH': ['which'],
            'WHERE': ['where'],
            #wordnet can be used to gather similar words to this
            'MEASURE': [
                'many years', 'much money',
                'cost',
                'many', 'much',
                'often', 'few',
                'long', 'short', 'tall', 'fast', 'slow',
                'high', 'low',
                'big', 'small',
                'close', 'near', 'far',
                'new', 'old',
                'heavy', 'light'
            ],
            'HOW': ['how'],
        }
        self.measure_map = {
            'many years': ["DATE", "TIME"], 
            'much money': ["MONEY"],
            'cost': ["MONEY"],
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
            'WHO': ['PERSON', 'ORG', 'GPE', 'NORP'], 
            'WHEN': ['TIME', 'DATE'],
            'WHERE': ['LOC', 'FAC', 'ORG', 'GPE'], #'PRODUCT', 'EVENT'], #did better without
            'MEASURE': [] #'PERCENT', 'MONEY', 'QUANTITY', 'CARDINAL', 'ORDINAL'
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
            for i in range(len(self.types[q_type])):
                expression = self.types[q_type][i]
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
        word_list = question.answer.split()
        for j, word in enumerate(word_list):
            if word in question.question.text:
                word_list[j] = ''
        question.answer = ' '.join(word_list)
        print(f'QuestionID: {question.question_id}')
        print(f'Answer: {question.answer}\n')

def score_using_overlap_and_weights(question, story, words_from_question, verbs_from_question, noun_phrases_from_question):
    scores = []
    high_score = 0
    for sentence in story.sentences:
        words_from_sentence = set([
            word.lemma_.lower() for word in sentence
            if not word.is_stop and
            (word.is_alpha or word.is_digit or word.is_currency or not word.is_punct)
        ])
        verbs_from_sentence = set([
            word.lemma_.lower() for word in sentence
            if not word.is_stop and word.pos_ == 'VERB'
        ])
        sentence_entities = [(entity.text, entity.label_) for entity in sentence.ents]
        given_score = len(words_from_sentence.intersection(words_from_question))
        #maybe to big of verb weight
        given_score += len(verbs_from_question.intersection(verbs_from_sentence)) * 3 #verb weight

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
    return high_score, scores
        
def get_words_and_verbs_from_question(question):
    words_from_question_non_syms = set([
        word for word in question.question if not word.is_stop and (word.is_alpha or word.is_digit or word.is_currency or not word.is_punct)
        ])
    verbs_from_question_non_syms = set([
        word for word in question.question if not word.is_stop and word.pos_ == 'VERB'
        ])
    words_from_question = set()
    verbs_from_question = set()
    for word in words_from_question_non_syms:
        for syn in wordnet.synsets(word.lemma_):
            for lm in syn.lemmas():
                name = lm.name().split('_')
                for spot in name:
                    if spot not in spacy.lang.en.stop_words.STOP_WORDS:
                        words_from_question.add(spot.lower())
        words_from_question.add(word.lemma_.lower())

    for word in verbs_from_question_non_syms:
        for syn in wordnet.synsets(word.lemma_):
            for lm in syn.lemmas():
                name = lm.name().split('_')
                for spot in name:
                    if spot not in spacy.lang.en.stop_words.STOP_WORDS:
                        verbs_from_question.add(spot.lower())
        verbs_from_question.add(word.lemma_.lower())
    return words_from_question, verbs_from_question

def named_entity_match_if_question_answer_types_is_defined(question, sentences, scores, words_from_question, verbs_from_question):
    sentence_entity_results = []
    score_spot = 0
    if question.answer_type:
        for sentence in sentences:
            words_from_sentence = set([
                word.lemma_.lower() for word in sentence
                if not word.is_stop and
                (word.is_alpha or word.is_digit or word.is_currency or not word.is_punct)
            ])
            verbs_from_sentence = set([
                word.lemma_.lower() for word in sentence
                if not word.is_stop and word.pos_ == 'VERB'
            ])
            entities = [(ent.text, ent.label_) for ent in sentence.ents]
            entity_answers = [(e[0], e[1]) for e in entities if e[1] in question.answer_type]
            sentence_entity_results.append({
                "answer": entity_answers,
                "sentence": sentence,
                "similarity": sentence.similarity(question.question),
                "overlap_weight_score": scores[score_spot],
                "overlap_score": len(words_from_sentence.intersection(words_from_question)),
                "overlap_verbs_score": len(verbs_from_sentence.intersection(verbs_from_question)),
            })
            score_spot += 1
    return sentence_entity_results

def match_another_way(question, head_noun, sentences, scores, words_from_question, verbs_from_question):
    possible_answers = []
    score_spot = 0
    if len(possible_answers) == 0:
        for sentence in sentences:
            words_from_sentence = set([
                word.lemma_.lower() for word in sentence
                if not word.is_stop and
                (word.is_alpha or word.is_digit or word.is_currency or not word.is_punct)
            ])
            verbs_from_sentence = set([
                word.lemma_.lower() for word in sentence
                if not word.is_stop and word.pos_ == 'VERB'
            ])
            possible_answers.append({
                "answer": sentence,
                "sentence": sentence,
                "similarity": sentence.similarity(question.question),
                "overlap_weight_score": scores[score_spot],
                "overlap_score": len(words_from_sentence.intersection(words_from_question)),
                "overlap_verbs_score": len(verbs_from_sentence.intersection(verbs_from_question)),
            })
            score_spot += 1
    return possible_answers


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
            
            words_from_question, verbs_from_question = get_words_and_verbs_from_question(question)

            noun_phrases_from_question = list(set(nc.text.lower().split()) for nc in question.question.noun_chunks)
            head_noun = None
            for chunk in question.question.noun_chunks:
                head_noun = chunk.root

            high_score, scores = score_using_overlap_and_weights(question, story, words_from_question, verbs_from_question, noun_phrases_from_question)
            possible_answers = named_entity_match_if_question_answer_types_is_defined(question, story.sentences, scores, words_from_question, verbs_from_question)
            if len(possible_answers) == 0 or question.type == 'WHY':
                possible_answers = match_another_way(question, head_noun, story.sentences, scores, words_from_question, verbs_from_question)
            possible_answers.sort(
                key=lambda x: x["similarity"], reverse=True)
            #had a slightly negative impact
            #possible_answers.sort(
            #    key=lambda x: x["overlap_verbs_score"], reverse=True)
            #the following order was slightly better
            possible_answers.sort(
                key=lambda x: x["overlap_score"], reverse=True)

            # possible_answers.sort(
            #     key=lambda x: x["similarity"], reverse=True
            # )
            possible_answers.sort(
                key=lambda x: x["overlap_weight_score"], reverse=True)
            question_dependencies = [0,0,0,0]
            for token in question.question:
                if token.dep_ == 'ROOT':
                    question_root_lemma = token.lemma
                    question_dependencies[0] = question_root_lemma
                if token.dep_ == 'dobj':
                    question_dobj_lemma = token.lemma
                    question_dependencies[1] = question_dobj_lemma
                if token.dep_ == 'nsubj':
                    question_nsubj_lemma = token.lemma
                    question_dependencies[2] = question_nsubj_lemma
                if token.dep_ == 'pobj':
                    question_pobj_lemma = token.lemma
                    question_dependencies[3] = question_pobj_lemma
            for dependency in question_dependencies:
                potential_answers = []
                if dependency != 0:
                    for sentence_i in possible_answers:
                        for token in sentence_i["sentence"]:
                            if token.lemma == dependency:
                                potential_answers.append(sentence_i)
                    if len(potential_answers) > 0:
                        possible_answers = potential_answers.copy()
            question.answer = ''
            entities = [(ent.text, ent.label_) for ent in possible_answers[0]["sentence"].ents]
            if question.answer_type:
                question.answer = ' '.join([e[0] for e in entities if e[1] in question.answer_type])
            else:
                if question.answer == '' or len(possible_answers[0]["sentence"].text) < len(question.answer):
                    question.answer = possible_answers[0]["sentence"].text
            word_list = question.answer.split()
            for j, word in enumerate(word_list):
                if word in question.question.text or word == " ":
                    word_list[j] = ''
            question.answer = ' '.join(word_list)
            if not question.answer or question.answer == "." or question.answer.strip() == "":
                question.answer = ""

                for i, score in enumerate(scores):
                    if score == high_score:
                        if question.answer and question.answer != '':
                            if len(story.sentences[i].text) < len(question.answer):
                                if question.answer_type:
                                    question.answer += ' '.join([e[0] for e in entities if e[1] in question.answer_type])
                                else:
                                    question.answer += story.sentences[i].text + " "
                        else:
                            if question.answer_type:
                                question.answer = ' '.join([e[0] for e in entities if e[1] in question.answer_type])
                            else:
                                question.answer = story.sentences[i].text + " "

    for question_file_i in questions:
        print_responses(questions[question_file_i])


if __name__ == "__main__":
    main()
