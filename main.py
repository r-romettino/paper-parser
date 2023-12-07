#!/usr/bin/python3
import nltk
import pdftotext
from nltk.tag.stanford import StanfordNERTagger as NERTagger

import subprocess
import sys
import os
import shutil

alpha = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN"
words = set(open("words.txt"))

def getFileName(fileName):
   name= fileName.replace(" ","_")
   return name

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
    return(resultat)


def getAbstract(path: str):
    abstract = ""

    os.system("pdftotext -raw " + path + " tmp")

    f = open("tmp", "r")
    corpus = f.readlines()
    f.close()

    os.remove("tmp")

    abstractFound = False
    for i in range(len(corpus)):
        line = corpus[i].strip()

        if len(line) == 0:
            continue

        if "abstract" in line.lower():
            abstractFound = True

            index = line.lower().find("abstract") + 8

            while index < len(line):
                if line[index] in alpha:
                    abstract += line[index:]
                    break

                index += 1

        if line[0] == 1 or "introduction" in line.lower():
            break

        if abstractFound and "abstract" not in line.lower():
            abstract += line

        if line[-1] != "-":
            abstract += " "
        else:
            lastWordIndex = line.rfind(" ") + 1
            lastWord = line[lastWordIndex:-1]

            firstWordIndex = corpus[i+1].find(" ")
            firstWord = corpus[i+1][:firstWordIndex]

            completeWord = lastWord + firstWord + "\n"

            if completeWord.lower() in words:
                abstract = abstract.removesuffix("-")

    return abstract.strip()

def getAutors(path):
    return
    
def getBiblio(path):
    return
    
if __name__ == '__main__':
	#recupèration du nom du repertoire
	arg = str(sys.argv[2:])
	arg= arg.replace("[","")
	arg= arg.replace("]","")
	arg= arg.replace("'","")

	#liste des fichiers du répertoire
	listFile= os.listdir(arg)
	
	#suppression du repertoire de stockage s'il existe
	pathResume = arg + "/articles_resumes"
	if  os.path.exists(pathResume):
		shutil.rmtree(pathResume)
		
	#création du répertoire de stockage
	os.mkdir(pathResume)
	
	#pour chaque fichier du répertoire, création d'un fichier texte du résumé dans le répertoire de stochage
	for file in listFile:
		if ".pdf" in file:
			pathFile = arg +"/"+ file
			
			
			if(str(sys.argv[1])=="-t"):
				txtFile = file.replace(".pdf",".txt")
				pathTxt = pathResume + "/" + txtFile
				with open(pathTxt, 'w') as sys.stdout:
					print(getFileName(file))
					print(getTitle(pathFile))
					print(getAutors(pathFile))
					print(getAbstract(pathFile))
					print(getBiblio(pathFile))
			
			if(str(sys.argv[1])=="-x"):	
				xmlFile = file.replace(".pdf",".xml")
				pathXml = pathResume + "/" + xmlFile
				with open(pathXml, 'w') as sys.stdout:
					print("<article>")
					print("		<preamble>",getFileName(file),"</preamble>")
					print("		<titre>",getTitle(pathFile),"</titre>")
					print("		<auteur>",getAutors(pathFile),"</auteur>")
					print("		<abstract>",getAbstract(pathFile),"</abstract>")
					print("		<biblio>",getAutors(pathFile),"</biblio>")
					print("</article>")
					
			
