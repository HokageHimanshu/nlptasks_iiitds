# Tamil NLP Tasks:

<p align="center">
Building Annotated Dataset and Models for Tamil lanuage.</p>

## Table of contents
1. [About](#About)
2. [Setup](#Setup)

## About
Natural language processing tools and datasets have seen a lot of advancements for languages like English, French etc. There are still many low resource languages like Tamil which require NLP tools for performing core NLP applications and datasets. 
We focus to produce a dataset of 10,000 sentences annotated in CoNLL-U format for Tamil language. The sentences are taken from a variety of sources like news articles, ebooks, grammar book, wikipedia articles and movie reviews. The medium size sentences containing 8-10 words are considered for this dataset.
We also aim to develop models and tools for every core NLP task like tokenization, morphology, pos tagging, ner prediction, dependecy parsing etc.

## Setup

1. Install virtualenv and make a python3 virtual environment named 'venv'. 
2. Activate the virtual environment in python using virtualenv. Run the following code
<br><code>`source tamilevn/bin/activate`</code>
3. Install all the libraries and dependencies using the following code
<br>`pip install -r requirements.txt`
4. Then the jupyter file should be launched in the same virtualenv using the same commands
<br><code>pip install --user ipykernel</code>
<br><code>python -m ipykernel install --user --name=venv</code>
5. Launch jupyter notebook and run it's cells
<br><code>jupyter notebook</code>

For help
"helper_classes" folder contains sample files for hendling the and traversing the data and performing different functionalities
