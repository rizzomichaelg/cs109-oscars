import pandas as pd
from pattern import web
import gc,time,re,unicodedata,json
from HTMLParser import HTMLParser

def filter_quotes(df):
    for index,row in df.iterrows():
        text = row['quote']
        text = text.decode('utf-8').encode('ascii','ignore')
        text = re.sub(r"\\u[0-9a-zAZ]{4}", "", text)
        text = re.sub("\\\[^\'|\"]", "", text)
        text = text.replace('\n','')
        text = unicodedata.normalize('NFKC',unicode(text)).encode('ascii','ignore')
        text = "".join(i for i in text if ord(i) < 128)
        df.ix[index, 'quote'] = text

def get_imdb_movie_reviews(id,title,year):
    score_max = 10.0
    link = "http://www.imdb.com/title/tt%0.7d/" % id
    url = web.URL(link)
    dom = web.DOM(url.download(cached=True))
    overall = float(dom.by_class("titlePageSprite star-box-giga-star")[0].content.strip()) / score_max
    # try to get year directly from page; this isn't present in every entry
    try:
        year = dom('span.itemprop[itemprop=name]')[0].next.next.by_tag('a')[0].content
        year = int(year)
    except:
        pass
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
            date = div.by_tag("small")[2].content
        except:
            continue
        user = div.by_tag("a")[1].content
        p = div.next.next
        review = parser.unescape(p.content.replace("<br />","\n"))
        lst.append(dict(critic=user,norm_score=score,quote=review,
                        id=id,title=title,source="IMDB",overall_score=overall,year=year,date=date))
    return lst

def get_all_imdb_movies():
    fname = 'revised_id_data.csv'
    df = []
    result = pd.read_csv('data/%s' % fname)
    f = open('errors.txt','w+')
    year = 2003
    for index,row in result.iterrows():
        try: 
            row['imdbid'] = int(row['imdbid'])
        except:
            continue
        newyr = row['year']
        if(int(newyr) != year and df != []):
            # filter_quotes(df)
            fo = open('imdbrev%d.json' % year,'w+')
            json.dump(df,fo)
            fo.close()
            year = int(newyr)
            df = []
            gc.collect()
        try:
            df.append(get_imdb_movie_reviews(row['imdbid'],row['movie_title'],row['year']))
            print row['movie_title'], year
        except:
            print >> f, "ERROR: %s" % row['movie_title']
    f.close()
    if df:
        fo = open('imdbrev%d.json' % year,'w+')
        json.dump(df,fo)
        fo.close()

start = time.time()

if __name__ == '__main__':
    get_all_imdb_movies()
    print "Elapsed Time: %s" % (time.time() - start)