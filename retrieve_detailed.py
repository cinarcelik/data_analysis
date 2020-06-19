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

conn_1 = sqlite3.connect('data_raw.sqlite')
cur_1 = conn_1.cursor()

cur_1.execute('''SELECT Designs.design_name,
                      Awards.award_type, 
                      Categories.category_name, 
                      Designers.designer_name,
                      Studios.studio_name,
                      Designs.design_page,
                      Designs.designer_page
               FROM Designs JOIN Awards JOIN Categories JOIN Designers JOIN Studios
               ON Designs.award_type_id = Awards.id
               AND Designs.category_id = Categories.id
               AND Designs.designer_id = Designers.id
               AND Designs.studio_id = Studios.id''')

conn_2 = sqlite3.connect('data_detailed.sqlite')
cur_2 = conn_2.cursor()

cur_2.executescript('''
DROP TABLE IF EXISTS Designs;
DROP TABLE IF EXISTS Designers;

CREATE TABLE Designs (
    id  INTEGER NOT NULL PRIMARY KEY UNIQUE,
    design_name             TEXT UNIQUE,
    award_type_id           INTEGER,
    category_id             INTEGER,
    design_image_link       TEXT,
    design_page             TEXT,
    designer_id             INTEGER,
    designer_page           TEXT,
    studio_id               INTEGER
);

CREATE TABLE Designers (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    designer_name   TEXT UNIQUE
);
''')

for row in cur_1:
    print(row)
    award_type = row[1]
    category_name = row[2]
    design_page = row[5]
    designer_page = row[6]


cur_1.close()
conn_2.commit()

timer_end = timer()
print(f"Code executed in {timer_end - timer_start} seconds.")
