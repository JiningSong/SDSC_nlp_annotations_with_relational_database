# NLP Annotations With Relational Database
<!-- ABOUT THE PROJECT -->
## About The Project
This software provides a data collection pipeline which analyzes input documents with 2 powerful nlp annotators: [stanza (A Python NLP Package developed by Stanford NLP Group)](https://stanfordnlp.github.io/stanza/) and [spaCy](https://spacy.io). The resulting tokens, annotations, and sentence segmentations will be stored into a postgresql relational database. The resulting dataset stored in the database can then be used in further data exploration and information extraction tasks.


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/JiningSong/SDSC_nlp_annotations_with_relational_database
   ```
2. Create a virtual enviroment for easier package management
   ```sh
   python3 -m venv <env_name>
   ```
3. Activate virtual enviroment
   ```sh
   source <env_name>/bin/activate
   ```
4. Install pip packages required to run this project
   ```sh
   pip install -r requirements.txt
   ```
5. Download Stanza (CoreNLP) models
   ```sh
   python download_stanza_models.py
   ```
6. Download spaCy resources
   ```sh
   python -m spacy download en_core_web_lg
   ```
7. Enter SOURCEFILE, DATABASECONFIG, TABLENAMES, ANNOTATOR in `configs.ini`
   ```sh
   [SOURCEFILE]
   # Replace with absolute path to sourcefile
   PATH = ../src/newspaper.md.json

   [DATABASECONFIG]
   HOST_NAME = localhost                # db_host
   DB_NAME = nlp_annotations_local      # db_name
   USER =                               # user (optinoal)
   PASSWORD =                           # password (optional)
   ACCEPT_DUPLICATE_DOCUMENT = false    # if true, pipeline will accept duplicate document

   [TABLENAMES]
   DOC_TBL = test.documents             
   SENT_TBL = test.sentences
   ANNOTATION_TBL = test.annotations

   [ANNOTATOR]
   NAME = spacy                         # put either spacy or corenlp           
   ```
8. Create Database with the same properties as specified above
   ```sql
   create table test.documents
   (
     doc_id numeric not null
       constraint documents_pk
         primary key,
     text text
   );

   create unique index documents_doc_id_uindex
     on test.documents (doc_id);

   create table test.sentences
   (
     doc_id numeric,
     sent_id numeric,
     sentence_text text,
     start_char integer,
     end_char integer
   );

   create table test.annotations
   (
     doc_id numeric,
     sent_id numeric,
     token_id integer,
     doc_token_id integer,
     token_text text,
     start_char integer,
     end_char integer,
     head_id integer,
     head_text text,
     dependency_relation text,
     entity_type text,
     upos text,
     xpos text
   );
   ```
9. Try out the project in main
   ```python
   python main.py
   ```
<!-- USAGE EXAMPLES -->
## Usage

 ```python
    # Specify path to config file
    path_to_configfile = "config.ini"

    # Create an Inserter
    inserter = Inserter(path_to_configfile)

    # Start insertion from src file to database (both are specified in config file)
    inserter.start_insertion()
 ```

### File Structure
```
- README.md
- __init__.py   
- requirements.txt
- config.ini                  Config file.
- download_stanza_models.py   Script for dowloading models from stanza.
- main.py                     Entry for the software. Contains main func.
- inserter.py                 Wrapping object for insertion pipeline.Initialize with path to configfile, then start_insertion.
- db.py                       Defines a Database object which contains connection and cursor to a postgresql server.
                              The Database object is also responsible executing SQL quries which are defined at the 
                              top of the db.py as global variables

- models.py                   Defines several data structures to store the results from nlp pipeline 

- nlp_pipelines.py            Core NLP pipeline which applies tokenizer, pos-tagger, lemma, dependency parser, ner parser, etc.
                              onto input documents. A document is seperated into sentences which are then tokenized into indivicual
                              tokens. The nlp_pipeline takes a document:string as input and returns a list of Sentences objects which 
                              contains a list of Token objects (Sentence and Token are defined in models.py)
- pipeline.py                 Higher level pipelines coordinates main functionalities
- utils.py                    Util functions
```
