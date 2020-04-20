import pandas as pd
import json
from models import *
from tqdm import tqdm 


# Read in documents from csv file
def read_csv(filepath):
    data = pd.read_csv(filepath)
    documents_list = data.to_numpy()
    for doc in documents_list:
        doc[1] = doc[1].replace('\n', '').replace('\r', '')

    return documents_list

def read_json(filepath):
    documents_list = []
    with open(filepath) as f:
        data = json.load(f)
        t = tqdm(total=len(data), desc="Reading JSON File from Disk: ")
        for el in data:
            doc_id = el['id']
            text = el['news']
            text = text.replace('\n', '').replace('\r', '')
            record = [doc_id, text]
            documents_list.append(record)
            t.update(1)
    t.close()
    return documents_list
   

def create_documents(documents_list):
    documents = []
    for doc in documents_list:
        document = Document(doc[1], doc[0])
        documents.append(document)
    return documents

def segment_and_upload_sents(db, documents):
    t = tqdm(total=len(documents), desc="Annotating documents and Populating sentence segmentations table: ")

    for doc in documents:
        tokens = []
        annotated_text = generate_document(doc.text)
        sent_segmentations = annotate_document(annotated_text)
        
        for el in sent_segmentations:
            annotate_sent = Sentence(doc.doc_id, el['sentence_text'], el['start_char'], el['end_char'])
            
            #insert sentence to db and save generated uuid in sentence object
            uuid = db.insert_sentence(annotate_sent)
            annotate_sent.set_sentence_id(uuid)
            
            for token_dict in el['tokens']:
                token = Token(annotate_sent, token_dict)
                tokens.append(token)
        for token in tokens:
            db.insert_lemma_annotation(token)
            db.insert_pos_annotation(token)
            db.insert_depparse_annotation(token)
            db.insert_ner_annotation(token)
        t.update(1)
    t.close()
    return tokens


 