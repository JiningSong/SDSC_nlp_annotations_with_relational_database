import stanza
import json
import string


DATA_FILE = "/Users/jining/Projects/FMP/stanford_core_nlp_demo/newsExample.csv"


def tokenize_document(text):
    tokeniser = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse, ner', logging_level='WARN')
    return tokeniser(text)


# Generate annotated_sentence result
def annotate_document(document):

    # Store list of segmented sentences
    annotated_sentences = []

    # start character of last sentence
    sentence_start_char = 0

    for sent in document.sentences:
        annotated_sentence = {}
        annotated_sentence['start_char'] = sent.tokens[0].start_char
        annotated_sentence['end_char'] = sent.tokens[-1].end_char
        
        annotated_sentence['sentence_text'] = ""

        #Store token dicts in annotated_sentence dictionary as a list of dicts
        annotated_sentence['tokens'] = []        
        for token in sent.tokens:
            if token.text in string.punctuation:
                annotated_sentence['sentence_text'] += token.text
            else:
                annotated_sentence['sentence_text'] += ' ' + token.text

            # Store token_dict
            token_dict = {}
            token_dict['token_id'] = token.id
            token_dict['token_text'] = token.text
            token_dict['start_char'] = token.start_char - sentence_start_char
            token_dict['end_char'] = token.end_char - sentence_start_char
            token_dict['ner'] = token.ner
         
            token_lemma = ""
            token_upos = ""
            token_xpos = ""
            token_feats = ""
            
            for word in token.words:
                if word.lemma:
                    token_lemma += word.lemma + ' '
                if word.upos:
                    token_upos += word.upos + ' '
                if word.xpos:
                    token_xpos = word.xpos + ' '
                if word.feats:
                    token_feats = word.feats + ' '

            token_dict['token_lemma'] = token_lemma[:-1]
            token_dict['token_upos'] = token_upos[:-1]
            token_dict['token_xpos'] = token_xpos[:-1]
            token_dict['token_feats'] = token_feats[:-1]

            # Set head for tokens
            if len(token.words) == 1:
                token_dict["head"] = token.words[0].head
                if token.words[0].head > 0:
                    token_dict["head_text"] = sent.words[word.head-1].text
                else:
                    token_dict["head_text"] = "root"
                token_dict["dependency_relation"] = token.words[0].deprel
            
            annotated_sentence['tokens'].append(token_dict)

        sentence_start_char = sent.tokens[-1].end_char+1

        annotated_sentence['sentence_text'] = annotated_sentence['sentence_text'][1:]
        annotated_sentences.append(annotated_sentence)
        
    return annotated_sentences