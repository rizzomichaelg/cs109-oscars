import os

# replace all instances of dic within text with term
def replace_all(text, dic, term):
    for i in dic:
        text = text.replace(i, term)
    return text

def replace_dir():
    dic = ["dy>"]
    term = ""
    for file in os.listdir('.'):
        if file.split('.')[-1] != 'html':
            continue
        f = open(file,"r+")
        str = f.read()
        f.seek(0)
        str = replace_all(str,dic,term)
        f.write(str)
        f.truncate()
        f.close()
        print file

if __name__ == '__main__':
    replace_dir()