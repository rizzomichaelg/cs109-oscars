

def get_top_movies_by_year(yr,num_movies=200):
    num_pages = int((num_movies-1)/100) + 1
    missing_rtid = 0
    missing_imdbid = 0
    alldata = []
    for pagenum in range(1,num_pages+1):
        url = 'http://boxofficemojo.com/yearly/chart/?page=' + str(pagenum) + '&view=releasedate&view2=domestic&yr=' + str(yr) + '&p=.htm'
        page_xml = requests.get(url).text
        dom = web.Element(page_xml)
        for table in dom.by_tag('table'):
            cellpadding = (table.attributes['cellpadding'])    
            if (cellpadding == '5'):  # isolates table with movie data
                for row in table.by_tag('tr'):
                    cols = row.by_tag('td')
                    #catches movie rows
                    try:
                        rank = int(web.strip_tags(cols[0]))
                        if (rank<=num_movies): #checks to make sure in right spot!
                            movie_title = web.strip_tags(cols[1]).strip('\t')
                            movie_title = unicodedata.normalize('NFKD', movie_title).encode('ascii', 'ignore') #removes accents
                            studio = web.strip_tags(cols[2]).strip('\t')
                            total_gross = int(((web.strip_tags(cols[3])).strip('$')).replace(',', ''))
                            num_theaters_total = int((web.strip_tags(cols[4])).replace(',', ''))
                            opening_revenue = int(((web.strip_tags(cols[5])).strip('$')).replace(',', ''))
                            num_theaters_opening = int((web.strip_tags(cols[6])).replace(',', ''))
                            date_open = web.strip_tags(cols[7]).strip('\t')
                            date_close = web.strip_tags(cols[8]).strip('\t')
                            
                            #using rotten tomatoes to get rtid/imdbid
                            url2 = 'http://api.rottentomatoes.com/api/public/v1.0/movies.json?' 'q=' + movie_title + ' &page_limit=10' + '&apikey=' + api_key
                            info_data = requests.get(url2).text
                            info_json = json.loads(info_data)
                            movie_count = 0
                            rtid=''
                            imdbid=''
                            try:
                                for movie in info_json['movies']:
                                    if movie['year']==yr:
                                        movie_count+=1
                                        rtid=movie['id']
                                        try:
                                            imdbid=(movie['alternate_ids'])['imdb']
                                        except:
                                            imdbid=''
                            except:
                                pass
                            if movie_count!=1: #case where more than one movie met description
                                rtid = ''
                                imdbid = ''
                            if imdbid=='':
                                missing_imdbid += 1
                            if rtid=='':
                                missing_rtid += 1
                            
                            data_row = [rank,movie_title,imdbid,rtid,studio,total_gross,num_theaters_total,opening_revenue,num_theaters_opening,date_open,date_close]
                            alldata.append(data_row)
                    except ValueError:
                        pass
    result = pd.DataFrame(alldata,columns=['rank','movie_title','imdbid','rtid','studio','total_gross','num_theaters_total','opening_revenue','num_theaters_opening','date_open','date_close'])
    if (missing_imdbid>0):
        print 'unable to find a imdbid for ' + str(missing_imdbid) + ' movies of ' + str(num_movies) + ' in ' + str(yr)
    if (missing_rtid>0):
        print 'unable to find a rtid for ' + str(missing_rtid) + ' movies of ' + str(num_movies) + ' in ' + str(yr)
    return result


for yr in range(2003,2013):
    num_movies=200
    result=get_top_movies_by_year(yr,num_movies)
    narrowed_data=pd.DataFrame(result, columns=['rank','movie_title','imdbid','rtid'])
    filename=str(yr) + '_top' + str(num_movies) + '.csv'
    narrowed_data.to_csv(filename, index=False)