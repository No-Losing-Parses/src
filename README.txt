No Losing Parses: Q/A System
https://no-losing-parses.github.io/src/ for up-to-date documentation

Group Members

Jaecee Naylor
Jared Amen

How to Run Our Code

./QA-script.txt /path/to/inputfile.txt /path/to/out.answers
cd data
perl score-answers.pl ourtest.answers <answer_key_filename>

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

We do not know of any significant (breaking) problems at the moment. We feel that our output is a potential limitation
due to it being difficult to parse for a human. Additionally, our system is hindered by the fact that it returns the
answer as an entire sentence instead of the specific answer phrase being sought out in the gold standard. Additionally,
our system is limited in accuracy due to its relatively basic nature. In the future, we look to implement better
question typing using answer type taxonomies (either drafted ourselves or ascertained from a library such as WordNet),
confidence levels/thresholds, and potentially cosine similarity of TF-IDF cosine matching.