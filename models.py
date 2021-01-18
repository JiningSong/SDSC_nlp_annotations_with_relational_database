import psycopg2
import uuid 


class Document:
    def __init__(self, text, doc_id=0):
        self.doc_id = doc_id
        self.text = text
    

    def to_db_data(self):
        return (
            self.doc_id, 
            self.text
        )


class Sentence:
    def __init__(self, doc_id, sentence_text, start_char, end_char):
        self.doc_id = doc_id
        self.sentence_id = uuid.uuid1().int
        self.sentence_text = sentence_text
        self.start_char = start_char
        self.end_char = end_char
    

    def set_sentence_id(self, sentence_id):
        self.sentence_id = sentence_id


    def to_db_data(self):
        return (
            self.doc_id,
            self.sentence_id,
            self.sentence_text,
            self.start_char,
            self.end_char
        )


class Token:
    def __init__(self, sentence, annotation_dict):
        # Common member fields (from sentence)
        self.doc_id = sentence.doc_id
        self.sentence_id = sentence.sentence_id

        # Common member fields (coreNLP pipeline on sentence)
        self.token_id = annotation_dict['token_id']
        self.doc_token_id = annotation_dict['doc_token_id']
        self.token_text = annotation_dict['token_text']
        self.start_char = annotation_dict['start_char']
        self.end_char = annotation_dict['end_char']
        
        # Member fields for depparse
        self.head_id = annotation_dict['head']
        self.head_text = annotation_dict['head_text']
        self.dependency_relation = annotation_dict['dependency_relation']
        
        
        # Member fields for POS
        self.upos = annotation_dict['token_upos']
        self.xpos = annotation_dict['token_xpos']

        # Memebr fields for NER
        self.ner = annotation_dict['ner']


    def to_db_data (self):
        return (
            self.doc_id,
            self.sentence_id,
            self.token_id,
            self.doc_token_id,
            self.token_text,
            self.start_char,
            self.end_char,
            self.head_id,
            self.head_text,
            self.dependency_relation,
            self.ner,
            self.upos,
            self.xpos,
        )

