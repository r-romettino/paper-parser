#!/usr/bin/python3
import nltk
import pdftotext
from nltk.tag.stanford import StanfordNERTagger as NERTagger
import re
import os
import subprocess
import sys
import shutil

alpha = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN"
num = "0123456789"
numRom = "IVX"
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
    
def getTextOnePara(path):
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f)

    isAbtract = re.search(r"Abstract", pdf[0], re.I)
    if isAbtract is None:
        lines = pdf[0].splitlines()
        indexAbstract = 0
        for line in lines:
            count = len(line)
            if count > 80:
                break
            indexAbstract += count + 1
    else:
        indexAbstract = isAbtract.start()

    # create text of first 3 pages
    text = ""
    for i in range(3):
        page = pdf[i]
        if i == 0:
            page = page[indexAbstract:]
        lines1 = re.split("\n", page)
        text1para1 = text1para2 = ' '
        for line in lines1:
            if line != ' ':
                para = re.split(r"[ \t]{8,}", line)
                if len(para) == 1:
                    firstpara = re.split(r"[ \t]{8,}", line)[0]
                    text1para1 = text1para1 + firstpara.strip() + '\n'
                if len(para) == 2:
                    firstpara = re.split(r"[ \t]{8,}", line)[0]
                    text1para1 = text1para1 + firstpara.strip() + '\n'
                    secondpara = re.split(r"[ \t]{8,}", line)[1]
                    text1para2 = text1para2 + secondpara.strip() + '\n'
                if len(para) > 2:
                    firstpara = re.split(r"[ \t]{8,}", line)[1]
                    text1para1 = text1para1 + firstpara.strip() + '\n'
                    secondpara = re.split(r"[ \t]{8,}", line)[2]
                    text1para2 = text1para2 + secondpara.strip() + '\n'
        text1para1 = re.sub(r"\n+", '\n', text1para1)
        text1para2 = re.sub(r"\n+", '\n', text1para2)
        text1 = text1para1 + ' ' + text1para2
        text = text + '\n' + text1

    return text
  
  
def getIntro(path):

    text = getTextOnePara(path)

    indexIntro = re.search(r"Introduction|1[.]*[ \t]+[NTRODUCIntroduci]+[ \t]*", text, re.I)
    if indexIntro is None:
        indexIntro = re.search(r"Introduction|I[.]*[ \t]+[NTRODUCIntroduci]+", text, re.I).start()
        indexSecondPara = indexIntro + re.search(r"\n[ \t]*II[.]*[ \t]+", text[indexIntro:], re.I).start()
    else:
        indexIntro = re.search(r"Introduction|1[.]*[ \t]+[NTRODUCIntroduci]+[ \t]*", text, re.I).start()
        indexSecondPara = indexIntro + re.search(r"\n[ \t]*[.]*[ \t]+", text[indexIntro:], re.I).start()

    Intro = text[indexIntro:indexSecondPara]
    Intro = re.sub("\\\\|\[|]|∗|[ \t]{2,}", " ", Intro)

    return Intro
    
def getCorps(path):
    return("")
    
def getConclu(path):
    conclu = ""

    os.system("pdftotext -raw " + path + " tmp")

    f = open("tmp", "r")
    corpus = f.readlines()
    f.close()

    os.remove("tmp")

    concluFound = False
    for i in range(len(corpus)):
        line = corpus[i].strip()

        if len(line) == 0:
            continue

        if "onclusion" in line:
            concluFound = True

            index = line.find("onclusion") + len(line)

            while index < len(line):
                if line[index] in alpha:
                    conclu += line[index:]
                    break

                index += 1
                
        if "onclusions" in line:
            concluFound = True

            index = line.find("onclusions") + len(line)

            while index < len(line):
                if line[index] in alpha:
                    conclu += line[index:]
                    break

                index += 1
                
        if "ONCLUSION" in line:
            concluFound = True

            index = line.find("ONCLUSION") + len(line)

            while index < len(line):
                if line[index] in alpha:
                    conclu += line[index:]
                    break

                index += 1
                
        if "ONCLUSIONS" in line:
            concluFound = True

            index = line.find("ONCLUSIONS") + len(line)

            while index < len(line):
                if line[index] in alpha:
                    conclu += line[index:]
                    break

                index += 1
	
        if line[0] == 1 or "discussion" in line.lower() or "discussions" in line.lower() or "references" in line.lower() or "acknowledgements" in line.lower() or "acknowledgement" in line.lower():
            break

        if concluFound and "Conclusion" not in line and "Conclusions" not in line and "CONCLUSION" not in line and "CONCLUSIONS" not in line:
            conclu += line

        if line[-1] != "-":
            conclu += " "
        else:
            lastWordIndex = line.rfind(" ") + 1
            lastWord = line[lastWordIndex:-1]

            firstWordIndex = corpus[i+1].find(" ")
            firstWord = corpus[i+1][:firstWordIndex]

            completeWord = lastWord + firstWord + "\n"

            if completeWord.lower() in words:
                conclu = conclu.removesuffix("-")
                
    return conclu.strip()

def getDiscu(path):
    discu = ""

    os.system("pdftotext -raw " + path + " tmp")

    f = open("tmp", "r")
    corpus = f.readlines()
    f.close()

    os.remove("tmp")

    discuFound = False
    for i in range(len(corpus)):
        line = corpus[i].strip()

        if len(line) == 0:
            continue

        if "Discussion" in line and line.find("Discussion")<20:
            discuFound = True

            index = line.find("DISCUSSION") + len(line)

            while index < len(line):
                if line[index] in alpha:
                    discu += line[index:]
                    break

                index += 1
                
        if "DISCUSSION" in line and line.find("Discussion")<20:
            discuFound = True

            index = line.find("DISCUSSION") + len(line)

            while index < len(line):
                if line[index] in alpha:
                    discu += line[index:]
                    break

                index += 1

        if line[0] == 1 or "conclusions" in line.lower() or "conclusion" in line.lower() or "references" in line.lower()or "acknowledgements" in line.lower() or "acknowledgement" in line.lower():
            break

        if discuFound and "Discussion" not in line and "DISCUSSION" not in line:
            discu += line

        if line[-1] != "-":
            discu += " "
        else:
            lastWordIndex = line.rfind(" ") + 1
            lastWord = line[lastWordIndex:-1]

            firstWordIndex = corpus[i+1].find(" ")
            firstWord = corpus[i+1][:firstWordIndex]

            completeWord = lastWord + firstWord + "\n"

            if completeWord.lower() in words:
                discu = discu.removesuffix("-")

    return discu.strip()
       
def getBiblio(path):
     biblio = ""

     os.system("pdftotext -raw " + path + " tmp")

     f = open("tmp", "r")
     corpus = f.readlines()
     f.close()

     os.remove("tmp")

     biblioFound = False
     for i in range(len(corpus)):
        line = corpus[i].strip()

        if len(line) == 0:
            continue

        if "references" in line.lower():
            biblioFound = True
            continue

        if biblioFound and re.fullmatch(r'^[0-9]+$', line) == None:
            biblio += line

        if line[-1] != "-":
            biblio += " "
        else:
            lastWordIndex = line.rfind(" ") + 1
            lastWord = line[lastWordIndex:-1]

            firstWordIndex = corpus[i+1].find(" ")
            firstWord = corpus[i+1][:firstWordIndex]

            completeWord = lastWord + firstWord + "\n"

            if completeWord.lower() in words:
                biblio = biblio.removesuffix("-")

     return biblio.strip()
    
if __name__ == '__main__':
	
	if len(sys.argv) == 1:
		print("La fonction doit s'appeler avec -t ou -x en argument pour avoir soit un fichier texte soit un fichier")
	else:
		print("Menu:")
		print("1 Tout le répertoire")
		print("2 PDF spécifiques")
		choix = input("Entrer votre choix: ")
		
		if choix == "1":
			
			rep =input("Entrer les chemins du repertoir: ")
			#liste des fichiers du répertoire
			listFile = os.listdir(rep)
			
		elif choix == "2":
			#liste des fichiers à traiter
			listFile = input("Entrer les chemins de vos fichier: ")
		
		if choix == "1" or choix == "2":
			pathResume = sys.argv[2]
			#pour chaque fichier du répertoire, création d'un fichier texte du résumé dans le répertoire de stochage
			for file in listFile:
				if ".pdf" in file:
					if choix == "1":
						pathFile = rep +"/"+ file
					elif choix == "2":
						pathFile =file
					
					if(str(sys.argv[1])=="-t"):
						txtFile = file.replace(".pdf",".txt")
						pathTxt = pathResume + "/" + txtFile
						with open(pathTxt, 'w') as sys.stdout:
							print(getFileName(file))
							print(getTitle(pathFile))
							print(getAutors(pathFile))
							print(getAbstract(pathFile))
							print(getIntro(pathFile))
							print(getCorps(pathFile))
							print(getConclu(pathFile))
							print(getDiscu(pathFile))
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
							print("		<introduction>",getIntro(pathFile),"</introduction>")
							print("		<corps>",getCorps(pathFile),"</corps>")
							print("		<conclusion>",getConclu(pathFile),"</conclusion>")
							print("		<discussion>",getDiscu(pathFile),"</discussion>")
							print("		<biblio>",getAutors(pathFile),"</biblio>")
							print("</article>")				
