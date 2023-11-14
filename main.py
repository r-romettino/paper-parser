#!/usr/bin/python3
import nltk
import pdftotext
from nltk.tag.stanford import StanfordNERTagger as NERTagger

def getFileName():
    return

# fast solution with simple list of names
# general solution for english names with nltk.tokenizer
# problems with marcu_statistics_sentence_pass_one.pdf and compression_phrases_Prog-Linear-jair.pdf
def getTitle(path):
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f)
    text = pdf[0]

    resultat = ""

    if(len(text)>300):
        text = text[:300]

    name_list = ["Minh", "Florian", "David", "James", "Vincent", "Kevin", "Andrei", "Andreas", "Juan"]

    """
    # Solution works for any english name, but requires files english.all.3class.distsim.crf.ser.gz and stanford-ner.jar
    st = NERTagger('stanford-ner/english.all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

    for sent in nltk.sent_tokenize(text):
        tokens = nltk.tokenize.word_tokenize(sent)
        tags = st.tag(tokens)
        for tag in tags:
            if tag[1] == 'PERSON': name_list.append(tag[0])
    """

    for name in name_list:
        index = text.find(name)
        if index>=0:
            lines = text[:index].split('\n')
            if(len(lines)>1):
                for i, line in enumerate(lines):
                    resultat += lines[i].strip() + " "
            else:
                resultat = lines[0]
            resultat = resultat.strip()
            break
    print("Title: " + resultat)

def getAbstract():
    return

if __name__ == '__main__':
    print("Ok")