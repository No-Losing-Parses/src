No Losing Parses: Q/A System
https://no-losing-parses.github.io/src/ for up-to-date documentation

Group Members

Jaecee Naylor
Jared Amen

How to Run Our Code

To run our code with your input file and desired file output path:
  ./QA-script.txt </path/to/inputfile.txt> </path/to/out.answers>
  cd data
  perl score-answers.pl </path/to/out.answers> </path/to/answerkey.answers>

To run our code with the developset-v2 data and our provided inputfile (all possible stories in develepset-v2):
  ./QA-script.txt ./data/developset-inputfile.txt </path/to/out.answers>
  cd data
  perl score-answers.pl </path/to/out.answers (same path as in the first step)> developset-answer-key.answers

To run our code with the testset1 data and our provided inputfile (all possible stories in testset1):
  ./QA-script.txt ./data/testset1-inputfile.txt </path/to/out.answers>
  cd data
  perl score-answers.pl </path/to/out.answers (same path as in the first step)> testset1-answer-key.answers

External Libraries/Datasets Used

- WordNet, derived from NLTK
    - No other libraries/datasets were used here
    - URL: https://www.nltk.org/api/nltk.corpus.reader.html#module-nltk.corpus.reader.wordnet

- SpaCy
    - For part-of-speech tagging, tokenizing, sentencizing, named-entity recognition, etc., we used
      SpaCy's medium-sized generic pretrained model "en_core_web_md"
    - URL: https://spacy.io/

Time Expected to Run

To install the necessary libraries and run the entire program, it took roughly 1 minute and 15 seconds.

To load in the "en_core_web_md" model and parse one document, it took roughly 15 seconds.

Group Member Contribution Scale

For this project we pair programmed swapping driver and passenger every half an hour. We feel we contributed evenly and
implemented each feature together. We chose to go about the project implementation this way because we wanted to make
sure we both understood what was going on with our project. We also wanted any road blocks to be discussed and solved
almost immediately.

Notes on Limitations

We do not know of any significant (breaking) problems at the moment. At this point, our system is attempting to return
more accurate answers through named-entity recognition and dependency parsing -- as a result, if it cannot find an
accurate answer phrase or sentence, it does not answer the question. While this did increase our score, as there is
likely a limitation in how it came to conclusions using named-entity recognition and dependency parsing, it is unfortunate,
as our system was unable to answer some easy questions where the answer might not have had anything to do with named-entity
recognition or dependency parsing. We would like to fix this in the future!
