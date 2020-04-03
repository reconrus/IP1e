import nltk
import re
import codecs
import sys
import os

# sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
# for line in codecs.open('/mnt/minerva1/nlp/projects/decipher_wikipedia/Prve_vety/find/sentenceExtractors/en/abbreviation_added_to_nltk.txt','r','utf-8'):
#   sent_detector._params.abbrev_types.add(line.strip())
# for line in codecs.open('/mnt/minerva1/nlp/projects/decipher_wikipedia/Prve_vety/find/sentenceExtractors/en/english_abbreviations.txt','r','utf-8'):
#   sent_detector._params.abbrev_types.add(line.strip())

def get_paragraph_internal(text):
    return re.search("("+re.escape(text)+"[^\n]*)", text).group(1)

def abbreviations(configFileAbbr):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    for abbrFile in  configFileAbbr:
        if os.path.isfile(abbrFile):
            for line in codecs.open(abbrFile,'r','utf-8'):
                sent_detector._params.abbrev_types.add(line.strip())
        else:
            sys.stderr.write('Abbreviation file "'+abbrFile+'" from yaml doesn\'t exist!\n')
            sys.exit(1)
    return sent_detector

def getSentence(sent_detector, text, title):
    result = ""
    temp = sent_detector.tokenize(text)
    if len(temp) > 0:
        result = temp[0].strip().split('\n')[0]
    else:
        result = str()
    if result.strip() == title:
        result = result + (temp[1].strip().split('\n')[0] if len(sent_detector.tokenize(text)) > 1 else "")
    return result

def getData(text, title, paragraph=False, configFileAbbr=[]):
    from WikiExtractor import clean
    result = ""
    returnArray = []
    linkType = ""
    textL = text.lower()
    # if (( ("(disambiguation)" in title) or
    #   ("{{disambiguation" in textL) or ("{{ disambiguation" in textL) or ("disambiguation }}" in textL) or ("disambiguation}}" in textL) or
    #   ("combdisambig}}" in textL) or ("{{disambig" in textL) or ("{{ disambig" in textL) or
    #   ("{{hndis" in textL) or ("{{geodis" in textL) or ("{{schooldis" in textL) or ("tndis}}" in textL) or ("numberdis}}" in textL) or
    #   ("{{human name disambiguation" in textL) or
    #   ("{{dab}}" in textL) or ("{{mathdab" in textL) ) and not ("{{r to" in text)):
    if ( (("(disambiguation)" in title) or
        (re.search("(\{\{( ){0,1}disambiguation)|(disambiguation( ){0,1}\}\})",textL)) or
        ("combdisambig}}" in textL) or (re.search("\{\{( ){0,1}disambig",textL)) or
        (re.search("\{\{( ){0,1}(((hn)|(geo)|(school)|(math))((dis)|(dab)))|(dab((\|)|(( ){0,1}\}\})))",textL)) or
        (re.search("((tn)|(number))dis( ){0,1}\}\}",textL)) or
        (re.search("(\{\{( ){0,1}((human)|(place)) name disambiguation)|(((human)|(place)) name disambiguation( ){0,1}\}\})",textL)) or
        (re.search("\{\{( ){0,1}disamb((\|)|(( ){0,1}\}\}))",textL)) or ("{{mil-unit-dis}}" in textL)) and not ("{{r to" in text) ):
        result = title
        linkType = "disambiguation"
        returnArray.append(linkType)
        returnArray.append(result)
        return returnArray

    if ("#redirect" in text[:15].lower()):
        redirect_title = text.split("[[", 1)[1].split("]]", 1)[0] #extract title from brackets [[]]   
        linkType = "redirect"
        returnArray.append(linkType)
        if len(redirect_title) > 0:
            returnArray.append(redirect_title)
        else:
            returnArray.append("")
        return returnArray


    sent_detector = abbreviations(configFileAbbr)

    text = text.replace("\n\n", "S_%neW-paragraph%_E")
    text = text.replace("\n=", "S_%neW-paragraph%_E")
    text = text.replace("\n*", "S_%neW-paragraph%_E")
    text = re.sub("from ?{{", "{{", text)
    text = re.sub("\({{lang-[^)]+(}}|/)\)", "", text)
    #print (text[2000:4000])
    #print ("-----------------------------------")
    #text = re.sub("ref", "XXXXX", text)
    text = clean(text)
    
    text = text.strip().replace("<br>", "").replace("<br/>", "").replace("<br />", "")
    text = re.sub("^:?\"[^\n\.\!\?]*[\.\!\?]?\"\n", "", text)
    text = re.sub("\[\[Image:[^\]]+\]\]", "", text)
    text = re.sub("__NOTOC__", "", text)
    text = re.sub("S?_?%neW-paragraph%_?E?", "\n\n", text)
    text = re.sub(".*&quot;.*For the .*, see .*&quot;.*", "", text)
    

    while len(text.strip()) > 0 and text.strip()[:1] == "=":
        text = (text.split("\n", 1)[1] if len(text.split("\n", 1)) > 1 else "").strip()
    if text[:2] == "* ":
        text = text[2:]
    if text[:1] == "*":
        text = text[1:]
    
    if paragraph:
        paragraphs = text.split("\n\n")
        result = str()
        for p in paragraphs:
            temp = sent_detector.tokenize(p)
            if len(temp) > 0 and temp[0].strip().split('\n')[0] is not title:
                result = " ".join(temp).replace("\n", " ")
                break
    else:
        result = getSentence(sent_detector, text, title)
    
    result = re.sub("\s*\([\s\W]*(or)?[\s\W]*\)", "", result)
    result = re.sub("&nbsp;", " ", result)
    result = re.sub("\([^\w&]+", "(", result)
    result = re.sub("[^\w&.]+\)", ")", result)
    result = re.sub("(\s?)[,;:'\\-–\s]+(\\s?)([,;:'\\-–])", "\\1\\2\\3", result)
    result = re.sub("<[^>]+>", "", result)

    if result[-1:] == ":":
        result = result[:-1] + "."
    if result[:2] == "is":
        result = title.strip() + " " + result
    # if "#redirect" == result[:9].lower():
    #   if len(result) < 11:
    #       result = ""
    #   elif result[9] == " ":
    #       result = result[10:]
    #   else:
    #       result = result[9:]
    #   linkType = "redirect"
    # elif " #redirect" == result[:10].lower():
    #   if len(result) < 12:
    #       result = ""
    #   elif result[10] == " ":
    #       result = result[11:]
    #   else:
    #       result = result[10:]
    #   linkType = "redirect"
    returnArray.append(linkType)
    returnArray.append(result)
    return returnArray

def getSentenceCirrusearch(text, title, sent_detector):

    #Clean Text
    # while True:
    #     count = 0
    #     if re.search("^Tento článek (nebo jeho část ){0,1}potřebuje",text):
    #         count = 3
    #     if re.search("^Tento článek ((není dostatečně ozdrojován)|(nepokrývá téma))",text):
    #         count = 2
    #     if re.search("^Tento článek ((vyžaduje kontrolu)|(zřejmě obsahuje)|(má znaky reklamy,))",text):
    #         count = 4
    #     if re.search("(((^Možná hledáte:)|(^Další významy jsou uvedeny na stránce))|(^Tento článek ((je o)|(pojednává o)))|(^(K){0,1}onkrétní problémy:)|(Související informace naleznete také v článku))",text):
    #         count = 1
    #     for i in range(count):
    #         text = text[text.find(".")+2:]
    #     if count == 0:
    #         break;
    #Get First Sentence
    return getSentence(sent_detector, text, title)