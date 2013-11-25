from pattern import web
import json

def get_imdb_movie_id(title,year):
    title = title.replace(" ","%20")
    link = "http://www.omdbapi.com/?t=%s&y=%s" % (title,year)
    text = web.URL(link).download(cached=True)
    return json.loads(text)

def replace_csv(year):
    fname = '%s_top200.csv' % year
    f = open("data/%s" % fname,"rb")
    result = f.readline()
    data = f.read()
    f.close()
    data = data.split("\n")
    for row in data:
        row = row.split(',')
        if len(row) < 3: 
            continue
        if row[2] == "":
            try:
                title = row[1].split('(')[0].strip()
                row[2] = get_imdb_movie_id(title,year)["imdbID"].replace("tt","")
            except:
                print row[1] + " failed"
        result += ','.join(row)

    f = open(fname,"w+")
    f.write(result)
    f.close()

for year in range(2003,2012):
    replace_csv(str(year))