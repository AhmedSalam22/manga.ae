from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import  sqlite3

conn = sqlite3.connect("MANGA_DB.sqlite")
cur = conn.cursor()

cur.executescript(""" 
    CREATE TABLE IF NOT EXISTS Manga (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        manga_name_id INTEGER  ,
        url TEXT,
        img TEXT ,
        release_date INTEGER,
        popularity INTEGER ,
        last_chapter INTEGER,
        chapters_id INTEGER 
        
    );
    
    CREATE TABLE IF NOT EXISTS manga_name (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        arabic_name TEXT,
        english_name TEXT
    );
    
 
    
    CREATE TABLE IF NOT EXISTS chapter_id (
        id INTEGER ,
        chapter_number INTEGER,
        img TEXT
        
    );

""")

progress = -1
null = 1
for i in range(1,82):
    url = "https://www.manga.ae/manga/page:{0}".format(i)
    # handel with 402 error
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage,'html.parser')
    divs_tag = soup.find_all("div",class_ = "mangacontainer")
    # print(divs_tag)


    content = []
    index = 0
    for div in divs_tag:
        soup_div = BeautifulSoup(div.decode(),'html.parser')

        link = soup_div.find("a")
        link_href = link.get("href")
        print("link", link_href)
        img = soup_div.find("img")
        img_src = img.get("src")
        print("img", img_src )



        # print(soup_div.get_text())
        content.append(soup_div.get_text())
        line = content[index].split("\n")
        index = index +1
        print(line)
        # for i in range(11):
        #     print("{0}".format(i), line[i])
        release_date = int(line[2])
        english_name = line[3]
        arabic_name = line[4]

        lc = line[8].split(":")

        last_chapter = int(lc[1])

        pp = line[7].split(" ")
        popularity = pp[0]

        cur.execute("INSERT OR IGNORE INTO Manga (url, img, release_date, last_chapter , popularity,manga_name_id,chapters_id) VALUES (?,?,?,?,?,?,?)",(str(link_href),str(img_src),release_date, last_chapter, popularity,null,null))
        null = null + 1
        cur.execute("INSERT INTO manga_name (english_name,arabic_name ) VALUES (?,?)  ",(english_name, arabic_name))

    conn.commit()

    progress = progress + 1
    print("progress",int(progress / 82 * 100))

static_url = "{url}/{chapter}/0/full"
all_data = cur.execute("SELECT url, last_chapter,chapters_id FROM manga")

for data in all_data:

    for i in range(1,data[1]+1):
        url = "{manga_url}/{chapter}/0/full".format(manga_url = data[0],chapter =i
                                                 )
        print(url)
            # handel with 402 error
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage,'html.parser')
        divs_tag = soup.find_all("div",id = "showchaptercontainer")
        # print("*********",divs_tag)
        for div in divs_tag:
            soup_div = BeautifulSoup(div.decode(),'html.parser')

            img = soup_div.find("img")
            img_src = img.get("src")
            print("img", img_src )
            cur.execute("INSERT  OR IGNORE INTO  chapter_id (chapter_number, img, id) VALUES (?,?,?)",(i, str(img_src), data[2]))
        conn.commit()

    # break
cur.close()