# NLP Annotations With Relational Database
This software performs a data collection pipeline which analyzes input documents using [stanza (A Python NLP Package developed by Stanford NLP Group)](https://stanfordnlp.github.io/stanza/) and store the resulting tokens, annotations, and sentence segmentations into a postgresql relational database. The resulting dataset stored in the database can then be used in further data exploration and information extraction 

### File Structure
```
FMP-nlp_annotations_with_relational_database
│
│───README.md
│───__init__.py   
│───requirements.txt
│───main.py ........... Entry for the software. Contains main func
│
│───db.py ............. Defines a Database object which contains connection and cursor to a postgresql server.
│                       The Database object is also responsible executing SQL quries which are defined at the 
│                       top of the db.py as global variables
│
│───models.py ......... Defines several data structures to store the results from nlp pipeline 
│
│───nlp_pipelines.py .. Core NLP pipeline which applies tokenizer, pos-tagger, lemma, dependency parser, ner parser, etc.
│                       onto input documents. A document is seperated into sentences which are then tokenized into indivicual
│                       tokens. The nlp_pipeline takes a document:string as input and returns a list of Sentences objects which 
│                       contains a list of Token objects (Sentence and Token are defined in models.py)
│
│───utils.py .......... Contains wrapper functions and more complex pipleines which execute the nlp pipeline and stores the 
                        results to relational database
```


This pipeline will annotates input documents using StanfordCoreNLP tools. The annotation results are stored in a postgresql relational database. The pipeline results will fill up tables with the following schemas.

Sentence_segmentation Table:        POS_annotations Table:
1)	doc_id                          1)	doc_id
2)	sentence_id                     2)	sentence_id 
3)	sentence_text                   3)	token_id
4)	start_char                      4)	token_text
5)	end_char                        5)	start_char
                                    6)	end_char
Documents Table:                    7)	upos
1)	doc_id                          8)	xpos 
2)	text                            9)	feats                           
                                   
NER_annotations Table:              Lemma_annotations Table:
1)	doc_id                          1)	doc_id
2)	sentence_id                     2)	sentence_id 
3)	token_id                        3)	token_id
4)	token_text                      4)	token_text
5)	entity_type                     5)	start_char
6)	start_char                      6)	end_char
7)	end_char                        7)	lemma

Depparse_annotations Table:
1)	doc_id
2)	sentence_id 
3)	token_id
4)	token_text
5)	start_char
6)	end_char
7)	head_id
8)	head_text
9)	dependency_relation

STEPS TO SETUP AND RUN THE PIPELINE:
1. Create a new virtualenv: `python3 -m venv {envName}`
2. Install required packages: `pip install -r requirements.txt`
3. Go to `populate_relationalDB.py`, change DATA_FILE to the path to file containing documents and document ids. Change HOST_NAME and DATABASE to configurate database in stance.
4. Run `python populate_relationalDB.py` 
5. The six tables above should be populated with data under DATA_FILE path.





