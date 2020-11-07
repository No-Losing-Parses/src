# Overview

This is the first stage of No Losing Parses' question/answering system, written for CS 6340 (Natural Language Processing) in the School of Computing at the University of Utah.

# Implementations

As of the time of this commit, our question/answering system works by utilizing the following common, relatively simple answer detection strategies:

* **Word Overlap:** this was done by taking the intersection between the question added to synsets for each lemma in the question and each individual sentence
* **Noun Phrase Matching:** this was done by taking the intersection between noun phrases in the question and noun phrases in each individual sentence
* **Question Typing/Named-Entity Recognition:** this was done by parsing wh- questions as well as measurement questions and returning the most likely named entities for each question from a list of named entities determinable by the external general NLP library SpaCy.
* **Custom Weights:** this was done by assigning weights to each determination made in the tactics above in order to emphasize certain matching rules over others. For instance, named entity recognition took weight precedence over other tactics, since it was generally more likely to produce the correct answer.

For all of these strategies, we made special considerations, such as removing noun phrases and named entities in both the question and the sentence we are observing, since they often detracted from our system's determination of the correct answer.

# Limitations

Currently, our system is significantly hindered by the fact that it returns the answer as an entire sentence instead of the specific answer phrase being sought out in the gold standard. Additionally, our system is limited in accuracy due to its relatively basic nature. In the future, we look to implement better question typing using answer type taxonomies (either drafted ourselves or ascertained from a library such as WordNet), confidence levels/thresholds, and potentially cosine similarity of TF-IDF cosine matching.

# Results

As of this PR, the current results for all story files in `data/developset-v2` are as such:

```
Finished processing 511 questions, 511 of which had responses.
*************************************************************************

FINAL RESULTS

AVERAGE RECALL =    0.4195  (214.36 / 511)
AVERAGE PRECISION = 0.1548  (79.12 / 511)
AVERAGE F-MEASURE = 0.2262

*************************************************************************
```