from pattern import web
import pandas as pd
import json
from HTMLParser import HTMLParser
import time

def get_imdb_movie_reviews(id,title):
    score_max = 10.0
    link = "http://www.imdb.com/title/tt%0.7d/" % id
    url = web.URL(link)
    dom = web.DOM(url.download(cached=True))
    overall = float(dom.by_class("titlePageSprite star-box-giga-star")[0].content.strip()) / score_max
    year = dom('span.itemprop[itemprop=name]')[0].next.next.by_tag('a')[0].content
    rc = dom.by_attr(itemprop="reviewCount")[0].content.split(" ")[0].replace(",","")
    revlink = link + 'reviews?count=%s&start=0' % rc # get at most 20 reviews
    url = web.URL(revlink)
    dom = web.DOM(url.download(cached=True))
    parser = HTMLParser()
    lst = []
    hrs = dom.by_id('tn15main').by_tag('hr')
    for hr in hrs:
        div = hr.next.next
        try:
            score = float(div.by_tag("img")[1].attrs["alt"].split("/")[0]) / score_max
        except:
            continue
        user = div.by_tag("a")[1].content
        p = div.next.next
        review = parser.unescape(p.content.replace("<br />","\n"))
        lst.append(dict(critic=user,norm_score=score,quote=review,
                        id=id,title=title,source="IMDB",overall_score=overall,year=year))
    return lst

start = time.time()

def get_year(year):
    result = pd.read_csv('data/%s_top200.csv' % year)
    alist = []
    errlist = []
    for index,row in result.iterrows():
        try: 
            row['imdbid'] = int(row['imdbid'])
        except:
            continue
        try:
            tmp = get_imdb_movie_reviews(row['imdbid'],row['movie_title'])
            alist.append(tmp)
            print row['movie_title'] + ' done'
        except:
            errlist.append((row['imdbid'],row['movie_title']))

    f = open('imdb_reviews_%s.json' % year,'w+')
    json.dump(alist,f)
    f.close()
    f = open('errors_%s.txt' % year,'w+')
    fid = f.fileno()
    print >> f, "ERRORS:"
    for x in errlist:
        print >> f, x
    f.close()
    
def main():
    for year in range(2003,2008):
        get_year(year)

main()
print "Elapsed Time: %s" % (time.time() - start)