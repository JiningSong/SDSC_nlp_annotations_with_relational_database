from models import Document
from db import Database
from tqdm import tqdm
import pandas as pd
import json
import time
import uuid


# Read in documents from csv file
def read_csv(filepath):
    documents = []
    data = pd.read_csv(filepath)
    for el in data.iloc[:, 4].tolist():
        if type(el) is str:
            documents.append(el)
    return documents


def read_json(filepath):
    documents = []
    with open(filepath) as f:
        data = json.load(f)
        t = tqdm(total=len(data), desc="Reading JSON File from Disk: ")
        for el in data:
            doc_id = el['id']
            text = el['news']
            text = text.replace('\n', '').replace('\r', '')
            record = [doc_id, text]
            documents.append(record)
            t.update(1)
    t.close()
    return documents


def create_documents(documents_list):
    documents = [] 
    for document in documents_list:
        doc_id = generate_unique_uuid_int()
        document = Document(document[1], doc_id)
        documents.append(document)
    return documents


def generate_unique_uuid_int():
    id = uuid.uuid1()
    return id.int
