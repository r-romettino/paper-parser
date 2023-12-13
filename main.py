#!/usr/bin/python3
import nltk
import pdftotext
from nltk.tag.stanford import StanfordNERTagger as NERTagger
import re

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

    name_list = ["Minh", "Andrei", "Juan"]

    # Solution works for any english name, but requires files english.all.3class.distsim.crf.ser.gz and stanford-ner.jar
    st = NERTagger('stanford-ner/english.all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

    for sent in nltk.sent_tokenize(text):
        tokens = nltk.tokenize.word_tokenize(sent)
        tags = st.tag(tokens)
        for tag in tags:
            if tag[1] == 'PERSON': name_list.append(tag[0])

    index = 500
    for name in name_list:
        if re.search(name, text):
            index = min(index, re.search(name, text).start())
    if index>=0:
        lines = text[:index].split('\n')
        if(len(lines)>1):
            for i, line in enumerate(lines):
                resultat += lines[i].strip() + " "
        else:
            resultat = lines[0]
        resultat = resultat.strip()

    return resultat


def getAuthors(path):
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f)
    # only first page
    text = pdf[0]

    indexFirstName = 1000
    isAbtract = re.search(r"Abstract", text, re.I)
    if isAbtract is None:
        lines = text.splitlines()
        indexAbstract = 0
        for line in lines:
            count = len(line)
            if count>80:
                break
            indexAbstract += count + 1
    else:
        indexAbstract = isAbtract.start()
    text = text[:indexAbstract]+"\n"+text[-1000:]

    dictNames = {}
    name_list = ["Minh", "Andrei", "Juan", "Daniel", "Bao", "Masaru", "Yi"]

    # Solution works for any english name, but requires files english.all.3class.distsim.crf.ser.gz and stanford-ner.jar
    st = NERTagger('stanford-ner/english.all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

    for sent in nltk.sent_tokenize(text):
        tokens = nltk.tokenize.word_tokenize(sent)
        tags = st.tag(tokens)
        for tag in tags:
            if tag[1] == 'PERSON': name_list.append(tag[0])

    # automatically found names
    for i, name in enumerate(name_list):
        name_list[i] = ''.join([i for i in name if not (i.lower()).isdigit()])

    # full names
    for name in name_list:
        index1 = text.find(name)
        if 0 < index1 < indexFirstName:
            indexFirstName = index1
        if index1>=0:
            index2 = index1
            fullName = text[index1:index2].lower()
            while not re.search(r'[,\n\\]|∗| and|\s{2,}', fullName):
                index2 = index2 + 1
                fullName = text[index1:index2]
            foundName = re.sub(r'[0-9]| and|\\|∗|,|\n', ' ', fullName).strip()
            if not (foundName in ' '.join(dictNames.keys())) and not any(name in foundName for name in dictNames.keys()):
                dictNames[foundName] = None

    mails = re.findall(r'[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+', text)
    mailsWithList = re.findall(r'{[ a-zA-Z0-9.,-]+}@[a-zA-Z0-9.-]+', text)
    if mailsWithList:
        for mail in mailsWithList:
            subStrings = re.split(r'[{}]', mail)
            names = subStrings[1].split(',')
            for name in names:
                mails.append(name.strip() + subStrings[2])

    for name in dictNames:
        for k in range(1, 6):
            for mail in mails:
                substring_list = [name[i: j].lower() for i in range(len(name))
                                   for j in range(i + 1, len(name) + 1)
                                   if len(name[i:j]) == k]
                if any(substring in mail.lower() for substring in substring_list):
                    dictNames[name] = mail

        if dictNames[name] is not None:
            mails.remove(dictNames[name])

    dictNames = {k: v for k, v in dictNames.items() if v}

    AuthorsSection = text[indexFirstName:indexAbstract]
    AuthorsSection = re.sub("\\\\|\[|]|∗|[ \t]{2,}", "", AuthorsSection)

    return dictNames, AuthorsSection

def getAbstract():
    return

if __name__ == '__main__':
    print("Ok")