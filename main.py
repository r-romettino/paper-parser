#!/usr/bin/python3

import os

alpha = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN"
words = set(open("words.txt"))

def getFileName():
    return

def getTitle():
    return

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

if __name__ == '__main__':
    print("Ok")