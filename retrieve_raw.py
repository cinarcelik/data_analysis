"""
Written by Çınar Çelik.
Turkey - 2020
"""

import re
import socket
import sqlite3
import ssl
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler
from timeit import default_timer as timer

from bs4 import BeautifulSoup

timer_start = timer()


# Ignore SSL certificate errors:
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('data_raw.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Designs;
DROP TABLE IF EXISTS Designers;
DROP TABLE IF EXISTS Studios;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Awards;

CREATE TABLE Designs (
    design_id  INTEGER NOT NULL PRIMARY KEY UNIQUE,
    design_name             TEXT UNIQUE,
    award_type_id           INTEGER,
    category_id             INTEGER,
    designer_id             INTEGER,
    studio_id               INTEGER,
    design_page             TEXT,
    thumbnail_img_link   TEXT
);

CREATE TABLE Designers (
    designer_id  INTEGER NOT NULL PRIMARY KEY UNIQUE,
    designer_name   TEXT UNIQUE,
    designer_page   TEXT UNIQUE
);

CREATE TABLE Studios (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    studio_name     TEXT UNIQUE
);

CREATE TABLE Categories (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    category_name   TEXT UNIQUE
);

CREATE TABLE Awards (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    award_type      TEXT UNIQUE
);
''')

# Actual URLs:
url = "https://competition.adesignaward.com/winners.php"
root_url = "https://competition.adesignaward.com/"

# Testing URL for HTML Errors:
# url = "https://www.google.com/search?q=test"

# Wait for a response from the webpage for 5 seconds:
timeout = 5
socket.setdefaulttimeout(timeout)

try:
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request, context=ctx)
    html = response.read()
except urllib.error.HTTPError as e:
    explanation = BaseHTTPRequestHandler.responses[e.code]
    print(f"HTML Error: {e.code} = {explanation[0]}")
    print(explanation[1])
except urllib.error.URLError as e:
    print("URL Error. Failed to reach a server.")
    print(f"Reason: {e.reason}")


soup = BeautifulSoup(html, "lxml")
for tag in soup.find_all("tr"):
    recognition = tag.find(string=re.compile("Award Winner"))
    if recognition is not None:
        category_name = recognition[recognition.find("for") + 4 : recognition.find("Category") - 1].strip()
        thumbnail_img_link = root_url + tag.find("img").get("src")
        design_page = root_url + tag.find(href=re.compile("design.php")).get("href")
        design_id = design_page[design_page.find("ID=") + 3 : ]
        design_name = tag.find(href=re.compile("design.php")).get_text().strip()
        award_type = recognition[ : recognition.find("A' Design Award")].strip()
        if award_type == "":
            award_type = "Regular"
        designer_page = root_url + tag.find(href=re.compile("designer.php")).get("href")
        designer_id = designer_page[designer_page.find("profile=") + 8 : ]
        designer_studio_name = tag.find(href=re.compile("designer.php")).get_text()
        designer_name = designer_studio_name[ : designer_studio_name.find("for") - 1]
        studio_name = designer_studio_name[designer_studio_name.find("for") + 4 : ]

        cur.execute('''INSERT OR IGNORE INTO Awards (award_type)
                                                        VALUES ( ? )''', (award_type, ))
        cur.execute('SELECT id FROM Awards WHERE award_type = ? ', (award_type, ))
        award_type_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO Categories (category_name)
                                                        VALUES ( ? )''', (category_name, ))
        cur.execute('SELECT id FROM Categories WHERE category_name = ? ', (category_name, ))
        category_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO Designers (designer_id, designer_name, designer_page)
                                VALUES ( ?, ?, ? )''', (designer_id, designer_name, designer_page))

        cur.execute('''INSERT OR IGNORE INTO Studios (studio_name)
                                                        VALUES ( ? )''', (studio_name, ))
        cur.execute('SELECT id FROM Studios WHERE studio_name = ? ', (studio_name, ))
        studio_id = cur.fetchone()[0]

        cur.execute('''INSERT OR REPLACE INTO Designs
        (design_id, design_name, award_type_id, category_id, designer_id, studio_id, design_page, thumbnail_img_link) 
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)''', (design_id, design_name, award_type_id, category_id, designer_id, studio_id, design_page, thumbnail_img_link))

conn.commit()

timer_end = timer()
print(f"Code executed in {timer_end - timer_start} seconds.")
