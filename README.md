
```
project
│   README.md
│   file001.txt    
│
└───folder1
│   │   file011.txt
│   │   file012.txt
│   │
│   └───subfolder1
│       │   file111.txt
│       │   file112.txt
│       │   ...
│   
└───folder2
    │   file021.txt
    │   file022.txt
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





