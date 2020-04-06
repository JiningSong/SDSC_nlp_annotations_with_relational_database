import stanza
import json


SAMPLE_SENTENCE = "This is a test sentence for stanze. "
SAMPLE_SENTENCES = "This is a test sentence for stanze. This is another sentence."
SAMPLE_SENTENCE_NER = "Chris Manning teaches at Stanford University. He lives in the Bay Area."


def build_pipeline(text):
    tokeniser = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse, ner', logging_level='WARN')
    return tokeniser(text)


# Generate sent_segmentation result
def generate_sent_segmentations(document):
    sent_segmentations = []
    for sent in document.sentences:
        sent_segmentation = []
        for el in sent.to_dict():
            sent_segmentation_dict = {
                "id": el['id'],
                "text": el["text"],
                "misc": el["misc"]
            }
            sent_segmentation.append(sent_segmentation_dict)
        sent_segmentations.append(sent_segmentation)
    return json.dumps(sent_segmentations)


# Generate POS and Morphological result
def generate_pos_annotations(document):
    pos_annotations = []
    for sent in document.sentences:
        pos_annotation = []
        for el in sent.to_dict():
            if "feats" in el:
                pos_annotation_dict = {
                    "id": el['id'],
                    "text": el["text"],
                    "upos": el["upos"],
                    "xpos": el["xpos"],
                    "feats": el["feats"]
                }
            else:
                pos_annotation_dict = {
                    "id": el['id'],
                    "text": el["text"],
                    "upos": el["upos"],
                    "xpos": el["xpos"],
                    "feats": ""
                }
            pos_annotation.append(pos_annotation_dict)
        pos_annotations.append(pos_annotation)
    return json.dumps(pos_annotations)


# Generate Lemmatization result
def generate_lemma_annotations(document):
    lemma_annotations = []
    for sent in document.sentences:
        lemma_annotation = []
        for el in sent.to_dict():
            lemma_dict = {
                "id": el['id'],
                "text": el["text"],
                "lemma": el["lemma"],
            }
            lemma_annotation.append(lemma_dict)

        lemma_annotations.append(lemma_annotation)
    return json.dumps(lemma_annotations)


# Generate Depparse result
def generate_depparse_annotations(document):
    depparse_annotations = []
    for sent in document.sentences:
        depparse_annotation = []
        for word in sent.words:
            depparse_dict = {
                "id": word.id,
                "text": word.text,
                "head": word.head,
            }
            if word.head > 0:
                depparse_dict["head_content"] = sent.words[word.head-1].text
            else:
                depparse_dict["head_content"] = "root"
            depparse_dict["deprel"] = word.deprel
            depparse_annotation.append(depparse_dict)
        depparse_annotations.append(depparse_annotation)
    return json.dumps(depparse_annotations)


# Generate NER annotation result
def generate_ner_annotations(document):
    ent_result = []
    for ent in document.ents:
        ent_dict = {
            "entity": ent.text,
            "type": ent.type
        }
        ent_result.append(ent_dict)
    return json.dumps(ent_result)


# Annotate document with 5 stanfor coreNLP tools
def annotate_document(document):

    document = build_pipeline(document)
    sent_segmentations = generate_sent_segmentations(document)
    pos_annotations = generate_pos_annotations(document)
    lemma_annotations = generate_lemma_annotations(document)
    depparse_annotations = generate_depparse_annotations(document)
    ner_annotations = generate_ner_annotations(document)

    return sent_segmentations, pos_annotations, lemma_annotations, depparse_annotations, ner_annotations
    
