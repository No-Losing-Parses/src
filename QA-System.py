import sys
import os

from collections import OrderedDict
class Story:
    def __init__(self, storyId, headline, date, text):
        self.storyId = storyId
        self.headline = headline
        self.date = date
        self.text = text

class Question:
    def __init__(self, questionId, question, difficulty):
        self.questionId = questionId
        self.question = question
        self.difficulty = difficulty
        self.answer = ""

def main():
    inputfile_name = sys.argv[1]
    inputfile = open(inputfile_name, "r")
    inputfile_lines = [line.strip() for line in inputfile.readlines()]
    inputfile.close()
    directory_path = inputfile_lines[0]
    #changing the direction so we will not need 
    #to append it for future files
    os.chdir(directory_path)
    stories = OrderedDict()
    questions = OrderedDict()
    for i, line in enumerate(inputfile_lines[1:], start = 1):
        #getting story from story file
        storyfile_name = line+".story"
        storyfile = open(storyfile_name, "r")
        storyfile_lines = storyfile.readlines()
        storyfile.close()
        headline, date = storyfile_lines[0].strip(), storyfile_lines[1].strip()
        story_id, text = storyfile_lines[2].strip(), " ".join(storyfile_lines[6:])
        story = Story(story_id, headline, date, text)
        stories[story_id] = story
        #getting questions from questions file
        questionsfile_name = line+".questions"
        questionsfile = open(questionsfile_name, "r")
        questionsfile_lines = [line.strip() for line in questionsfile.readlines()]
        all_questions = [questionsfile_lines[i:i+3] for i in range(0, len(questionsfile_lines), 4)]
        #go through all questions and add then to our questions
        for j, jine in enumerate(all_questions):
            question_id = jine[0]
            question_asked = jine[1]
            difficulty = jine[2]
            question = Question(question_id, question_asked, difficulty)
            if story_id in questions:
                questions[story_id].append(question)
            else:
                questions[story_id] = [question]
                
if __name__ == "__main__":
    main()