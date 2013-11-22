
import csv

from pattern.web import URL, DOM, plaintext, strip_between
from pattern.web import NODE, TEXT, COMMENT, ELEMENT, DOCUMENT

from unidecode import unidecode
import unicodedata

import re

def fixWeirdChars(stringy):
	matchObj = re.search(r'&#x..', stringy)
	if matchObj:
   		accentedHex = matchObj.group()
   		HexPart = accentedHex.split('x')[1]
   		Hexy = "0x" + HexPart
   		Num = int(Hexy, 16)
   		Char = chr(Num)
   		stringy = re.sub((accentedHex+';'), Char, stringy)
   		#print stringy

   		matchAgain = re.search(r'&#x..', stringy)
   		if(matchAgain):
   			return fixWeirdChars(stringy)
   		else:
   			return stringy
   	else:
   		return stringy


def clean_unicode(s):
	s.encode('ascii','ignore')
	s = fixWeirdChars(s)
 	return str(s)


'''
Gets the movie titles for all Oscars for a given year.
Outputs a dict of the format:
'Award':
	'nominees': ['a', 'b', 'c', 'd'] 
	'winner': 'f'

'''
def get_by_year(year):

	output = open("all_nominees.csv", "wb")
	writer = csv.writer(output)

	#if(year == 2012):
	url = URL("http://www.imdb.com/event/ev0000003/" + str(year))
	dom = DOM(url.download(cached=True))
	
	dictAll = {}
	#for val in range (0,5):
	awards = dom.by_class('award')
	awardTitles = awards[0].by_tag('h2')
	awardList = []
	for award in awardTitles:
		awardList.append(clean_unicode(award.content))
	 	#dictAll[award.content]
	#print awardList
	prize = awards[0].by_tag('blockquote')
	for index, title in enumerate(prize[1:25]):
		winner = title.by_tag('strong')[0].by_tag('a')[0].content
		#print winner
		nomineeList = []
	 	for each in title.by_tag('strong')[1::]:
	 		nomineeList.append(clean_unicode(each.by_tag('a')[0].content))
	 	
	 	winnersAndNominees = {}
	  	winnersAndNominees['winner'] = clean_unicode(winner)
	  	winnersAndNominees['nominees'] = nomineeList
	 	dictAll[awardList[index]] =  winnersAndNominees
	print dictAll['Best Performance by an Actor in a Leading Role']	
	return dictAll

'''
Gets the movie titles for all Oscars for all years between 1935 and 2013.
Outputs a dict of dicts the format:
'Year':
	'Award':
		'nominees': ['a', 'b', 'c', 'd'] 
		'winner': 'f'

'''
def get_all_years():
	hugeDict = {}  #lol
	for year in range(1935, 2014):
		hugeDict[year] = get_by_year(str(year))
	return hugeDict #LOLLLL


def get_by_award_all_years(oscar):
	yearDict = {}
	for year in range(1950, 2014):
		url = URL("http://www.imdb.com/event/ev0000003/" + str(year))
		dom = DOM(url.download(cached=True))
		
		awards = dom.by_class('award')
		awardTitles = awards[0].by_tag('h2')
		index = 1
		isin = False
		for award in awardTitles:
			if (oscar == clean_unicode(award.content)):
				isin = True
				break
			elif (index > 30):
				break
			else:
				index += 1
		
		if(isin):
			prize = awards[0].by_tag('blockquote')
			winnersAndNominees = {}
			
			winner = prize[index].by_tag('strong')[0].by_tag('a')[0].content
			#print winner
			nomineeList = []
			for each in prize[index].by_tag('strong')[1::]:
			 	nomineeList.append(clean_unicode(each.by_tag('a')[0].content))
			  	winnersAndNominees['winner'] = clean_unicode(winner)
			  	winnersAndNominees['nominees'] = nomineeList

			yearDict[year] =  winnersAndNominees
	print yearDict
	return yearDict

#get_by_year(2013)
get_by_award_all_years('Best Performance by an Actress in a Leading Role')