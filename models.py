import psycopg2
from nlp_pipelines import *


class Document:
    def __init__(self, text, doc_id=0):
        self.doc_id = doc_id
        self.text = text
    
    # def set_doc_id(self, doc_id):
    #     self.doc_id = doc_id
    
    # def get_doc_id(self):
    #     return self.doc_id
    
    # def get_text(self):
    #     return self.text
    
    def to_db_data(self):
        return (
            self.doc_id, 
            self.text
        )


class Sentence:
    def __init__(self, doc_id, sentence_text, start_char, end_char):
        self.doc_id = doc_id
        self.sentence_text = sentence_text
        self.start_char = start_char
        self.end_char = end_char
        self.sentence_id = 0
    
    def set_sentence_id(self, sentence_id):
        self.sentence_id = sentence_id

    def to_db_data(self):
        return (
            self.doc_id,
            self.sentence_text,
            self.start_char,
            self.end_char
        )
