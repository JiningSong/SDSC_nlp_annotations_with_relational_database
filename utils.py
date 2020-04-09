import pandas as pd
from models import *


# Read in documents from csv file
def read_csv(filepath):
    data = pd.read_csv(filepath)
    documents_list = data.to_numpy()
    for doc in documents_list:
        doc[1] = doc[1].replace('\n', '').replace('\r', '')

    #TODO: TRIM quotation marks
    return documents_list

def create_documents(documents_list):
    documents = []
    for doc in documents_list:
        document = Document(doc[1], doc[0])
        documents.append(document)
    return documents

# def annotate_documents(documents):
#     annotated_documents = []
#     for doc in documents:
#         annotated_document= Annotated_document(doc)
#         annotated_documents.append(annotate_document)
#     return annotated_documents
       

 