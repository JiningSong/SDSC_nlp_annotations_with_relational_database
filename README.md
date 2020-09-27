# NLP Annotations With Relational Database
This software performs a data collection pipeline which analyzes input documents using [stanza (A Python NLP Package developed by Stanford NLP Group)](https://stanfordnlp.github.io/stanza/) and store the resulting tokens, annotations, and sentence segmentations into a postgresql relational database. The resulting dataset stored in the database can then be used in further data exploration and information extraction 
### STEPS TO SETUP AND RUN THE PIPELINE:
1. Create a new virtualenv: `python3 -m venv {envName}`
2. Install required packages: `pip install -r requirements.txt`
3. Go to `main.py`, uncomment any pipeline (populating nlp database, populating cdc dataset, removing duplicate tokens from annotations tbl, etc)
4. Go to `db.py`, change the Global variables -- DB configs to your own credentials 
5. Run `python main.py` 

### Database Schema   
```
sentence_segmentation Table:        documents Table:
1)	doc_id                          1)	doc_id
2)	sent_id                         2)	text 
3)	sentence_text                   
4)	start_char                      
5)	end_char                        

annotations table:
1)	doc_id            8)	head_text
2)	sentence_id       9)	dependency_relation
3)	token_id          10) entity type
4)	token_text_id     11) upos
5)	start_char        12) xpos
6)	end_char          13) feats
7)	head_id
```

### File Structure
```
- README.md
- __init__.py   
- requirements.txt
- main.py              Entry for the software. Contains main func

- db.py                Defines a Database object which contains connection and cursor to a postgresql server.
                       The Database object is also responsible executing SQL quries which are defined at the 
                       top of the db.py as global variables

- models.py            Defines several data structures to store the results from nlp pipeline 

- nlp_pipelines.py     Core NLP pipeline which applies tokenizer, pos-tagger, lemma, dependency parser, ner parser, etc.
                       onto input documents. A document is seperated into sentences which are then tokenized into indivicual
                       tokens. The nlp_pipeline takes a document:string as input and returns a list of Sentences objects which 
                       contains a list of Token objects (Sentence and Token are defined in models.py)

- utils.py             Contains wrapper functions and more complex pipleines which execute the nlp pipeline and stores the 
                       results to relational database
```







