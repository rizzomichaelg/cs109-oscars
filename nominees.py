
# HELPER FUNCTIONS

from pattern.web import URL, DOM, plaintext, strip_between
from pattern.web import NODE, TEXT, COMMENT, ELEMENT, DOCUMENT

import re
import json

#get rid of accents etc. 
def fixWeirdChars(phrase):
    HexEncode = ['E9','E1','E0','B7']
    matchObj = re.search(r'&#x..', phrase)
    if matchObj:
        accentedHex = matchObj.group()
        HexPart = accentedHex.split('x')[1]
        if(HexPart in HexEncode):
            phrase = re.sub((accentedHex+';'), 'e', phrase)
        else:
            Hexy = "0x" + HexPart
            Num = int(Hexy, 16)
            Char = chr(Num)
            phrase = re.sub((accentedHex+';'), Char, phrase)

        matchAgain = re.search(r'&#x..', phrase)
        return fixWeirdChars(phrase)
    return phrase


def clean_unicode(s):
    s = str(s)
    s.encode('ascii','ignore')
    s = fixWeirdChars(s)
    return str(s)

# repair dictionary names
def repair_dict(dictionary):
    for year in dictionary:
        for award in dictionary[year]:
            if(award == 'Best Motion Picture of the Year'):
                dictionary[year]['Best Picture'] = dictionary[year]['Best Motion Picture of the Year']
                del dictionary[year]['Best Motion Picture of the Year']

            if(award == 'Best Performance by an Actor in a Leading Role'):
                dictionary[year]['Best Actor in a Leading Role'] = dictionary[year]['Best Performance by an Actor in a Leading Role']
                del dictionary[year]['Best Performance by an Actor in a Leading Role']

            if(award == 'Best Performance by an Actress in a Leading Role'):
                dictionary[year]['Best Actress in a Leading Role'] = dictionary[year]['Best Performance by an Actress in a Leading Role']
                del dictionary[year]['Best Performance by an Actress in a Leading Role']

            if(award == 'Best Performance by an Actress in a Supporting Role'):
                dictionary[year]['Best Actress in a Supporting Role'] = dictionary[year]['Best Performance by an Actress in a Supporting Role']
                del dictionary[year]['Best Performance by an Actress in a Supporting Role']

            if(award == 'Best Performance by an Actor in a Supporting Role'):
                dictionary[year]['Best Actor in a Supporting Role'] = dictionary[year]['Best Performance by an Actor in a Supporting Role']
                del dictionary[year]['Best Performance by an Actor in a Supporting Role']

            if(award == 'Best Writing, Original Screenplay'):
                dictionary[year]['Best Writing, Screenplay Written Directly for the Screen'] = dictionary[year]['Best Writing, Original Screenplay']
                del dictionary[year]['Best Writing, Original Screenplay']

            if(award == 'Best Writing, Adapted Screenplay'):
                dictionary[year]['Best Writing, Screenplay Based on Material from Another Medium'] = dictionary[year]['Best Writing, Adapted Screenplay']
                del dictionary[year]['Best Writing, Adapted Screenplay']

            if(award == 'Best Foreign Language Film of the Year'):
                newAwardName = award
                newAwardName = re.sub(' of the Year', '', newAwardName)
                dictionary[year][newAwardName] = dictionary[year][award]
                del dictionary[year][award]

            # check to see if it includes best achievement
            if('Best Achievement' in award):
                if(award == 'Best Achievement in Directing'):
                    dictionary[year]['Best Director'] = dictionary[year]['Best Achievement in Directing']
                    del dictionary[year]['Best Achievement in Directing']
                else:
                    newAwardName = award
                    if('Mixing' in award):
                        newAwardName = re.sub(' Mixing', '', newAwardName)

                    if(' and Hairstyling' in award):
                        newAwardName = re.sub(' and Hairstyling', '', newAwardName)

                    if('Music Written for Motion Pictures, Original Song' or 'Music Written for Motion Pictures, Original Score' in award):
                        newAwardName = re.sub(' Written for Motion Pictures', '', newAwardName)


                    newAwardName = re.sub(' Achievement in', '', newAwardName)

                    if 'Visual Effects' in newAwardName:
                        #add comma
                        newAwardName = 'Best Effects, Visual Effects' 

                    dictionary[year][newAwardName] = dictionary[year][award]
                    del dictionary[year][award]
                    
    return dictionary

# END OF HELPER FUNCTIONS


"""
Gets the movie titles for all Oscars for a given year. i.e. get_by_year(2012)
Function
--------
get_by_year

Input int year

Outputs a dict of the format:
'Award':
    'nominees': ['a', 'b', 'c', 'd'] 
    'winner': 'f'

"""
def get_by_year(year):

    url = URL("http://www.imdb.com/event/ev0000003/" + str(year))
    dom = DOM(url.download(cached=True))
    
    dictAll = {}
    
    awards = dom.by_class('award')
    awardTitles = awards[0].by_tag('h2')
    awardList = []
    for award in awardTitles:
        awardList.append(award.content)

    prize = awards[0].by_tag('blockquote')
    for index, title in enumerate(prize[1:25]):
        winner = title.by_tag('strong')[0].by_tag('a')[0].content
        winner_id = str(title.by_tag('strong')[0].by_tag('a')[0].attrs['href'][-8:-1])

        nomineeList = []
        for each in title.by_tag('strong')[1::]:
            name = each.by_tag('a')[0].content
            id = str(each.by_tag('a')[0].attrs['href'][-8:-1])
            nomineeList.append((clean_unicode(name),id))
            
        winnersAndNominees = {}
        winnersAndNominees['winner'] = (clean_unicode(winner),winner_id)
        winnersAndNominees['nominees'] = nomineeList
        dictAll[awardList[index]] =  winnersAndNominees
    return dictAll



"""
Gets the movie titles for all Oscars for all years between 1935 and 2013.
Function
--------
get_all_years()


Outputs a dict of dicts the format:
'Year':
    'Award':
        'nominees': ['a', 'b', 'c', 'd'] 
        'winner': 'f'
"""

def get_all_years():
    hugeDict = {}  #lol
    for year in range(2003, 2014):
        hugeDict[year] = get_by_year(str(year))
    return hugeDict



'''
Gets all data for every year for a specific oscar
Function
------
get_by_award_all_years(oscar, dictionary)

Outputs a dict of the format
'Year':
    'nominees': ['a', 'b', 'c', 'd'] 
    'winner': 'f'
        
'''
def get_by_award_all_years(oscar, dictionary):
    yearDict = {}
    for year in dictionary:
        if oscar in dictionary[year].keys():
            yearDict[year] = dictionary[year][oscar]
    return yearDict


dict = get_all_years()

dict = repair_dict(dict)

f = open('data/oscars.json','wb')
json.dump(dict,f)
f.close()