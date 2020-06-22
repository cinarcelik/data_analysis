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


def read_URL(url):
    '''
    Input:
      url   - A URL to connect and read the HTML source code.

    Outputs:
      Tries to read the given URL and returns the root URL and HTML
      source code of the website as a tuple. If the connection fails,
      prints out the error code and an explanation of it.
      (root_url, html)
    '''
    # Ignore SSL certificate errors:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Wait for a response from the webpage for 5 seconds:
    timeout = 5
    socket.setdefaulttimeout(timeout)

    root_url = url[ : url.rfind("/")]

    try:
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request, context=ctx)
        html = response.read()
        return (root_url, html)
    except urllib.error.HTTPError as e:
        explanation = BaseHTTPRequestHandler.responses[e.code]
        print(f"HTML Error: {e.code} = {explanation[0]}")
        print(explanation[1])
    except urllib.error.URLError as e:
        print("URL Error. Failed to reach a server.")
        print(f"Reason: {e.reason}")


def read_winners_page(root_url, html, parser):
    '''
    Inputs:
      root_url  - Root URL of the website which HTML is taken.
      html      - An HTML source code to read and extract data from.
      parser    - A parser to use to make a soup object with BeautifulSoup.
                  Options are: "html.parser", "lxml", "xml", "html5lib".

    Output:
      Reads the given HTML source code of A' Design Award's winners webpage.
      Returns the data about designs and winners as a dictionary of dictionaries
      in which keys are the design IDs.

    Output Dictionary Style:
      {design_id:
        {Award: award_type,
         Category: category_name,
         Designer: designer_name,
         Designer_ID: designer_id
         Design_URL: design_page
         Designer_URL: designer_page},
      }
    '''
    main_dict = dict()
    soup = BeautifulSoup(html, parser)
    for tag in soup.find_all("tr"):
        mention = tag.find(string=re.compile("Award Winner"))

        if mention is not None:
            minor_dict = {}
            design_page = root_url + "/" + tag.find(href=re.compile("design.php")).get("href")
            design_id = design_page[design_page.find("ID=") + 3 : ]
            category_name = mention[mention.find("for") + 4 : mention.find("Category") - 1].strip()
            award_type = mention[ : mention.find("A' Design Award")].strip()
            if award_type == "":
                award_type = "Regular"
            designer_page = root_url + "/" + tag.find(href=re.compile("designer.php")).get("href")
            designer_id = designer_page[designer_page.find("profile=") + 8 : ]
            x_for_y = tag.find(href=re.compile("designer.php")).get_text()
            designer_name = x_for_y[ : x_for_y.find("for") - 1]

            minor_dict["Award"] = award_type
            minor_dict["Category"] = category_name
            minor_dict["Designer"] = designer_name
            minor_dict["Designer_ID"] = int(designer_id)
            minor_dict["Design_URL"] = design_page
            minor_dict["Designer_URL"] = designer_page
            main_dict[int(design_id)] = minor_dict

    return main_dict


def read_design_page(dictionary, parser):
    '''
    Input:
      dictionary    - Winners page dictionary
      parser        - A parser to use to make a soup object with BeautifulSoup.
                      Options are: "html.parser", "lxml", "xml", "html5lib".

    Output:
      Reads the given dictionary, uses its Design URLs to retrieve data
      from them. Then builds and returns another dictionary of the
      retrieved data.

    Input Dictionary Style:
      {design_id:
        {Award: award_type,
         Category: category_name,
         Designer: designer_name,
         Designer_ID: designer_id
         Design_URL: design_page
         Designer_URL: designer_page},
      }
    '''
    titles_dict = {"DESIGN NAME:": "design_name",
    "PRIMARY FUNCTION:": "prim_func",
    "INSPIRATION:": "inspiration",
    "UNIQUE PROPERTIES / PROJECT DESCRIPTION:": "description",
    "OPERATION / FLOW / INTERACTION:": "flow",
    "PROJECT DURATION AND LOCATION:": "dur_loc",
    "FITS BEST INTO CATEGORY:": "fbt_category",
    "PRODUCTION / REALIZATION TECHNOLOGY:": "prod_tech",
    "SPECIFICATIONS / TECHNICAL PROPERTIES:": "specifications",
    "TAGS:": "tags",
    "RESEARCH ABSTRACT:": "res_abst",
    "CHALLENGE:": "challenge",
    "ADDED DATE:": "add_date",
    "TEAM MEMBERS": "team_members",
    "IMAGE CREDITS:": "img_credits",
    "PATENTS/COPYRIGHTS:": "patents"}

    for design_id in dictionary.keys():
        design_page = dictionary[design_id]["Design_URL"]
        root_url, html = read_URL(design_page)
        soup = BeautifulSoup(html, parser)
        design_image_link = root_url + "/" + f"award-winning-design.php?ID={design_id}"

        design_details_tag = soup.find(text="DESIGN DETAILS").parent
        design_details_list = []
        for element in design_details_tag.find_all_next(string=True):
            element = element.strip()
            if element == "":
                continue
            design_details_list.append(element)
            if element == "AWARD DETAILS":
                break

        design_details_dict = {}
        details = {}
        for title, variable in titles_dict.items():
            if title in design_details_list:
                details[variable] = design_details_list[design_details_list.index(title) + 1]

        design_details_dict[design_id] = details

        print(design_details_dict)


    # return titles_dict


# def sql_executer(db_file, reset=False, ):
#     '''
#     Inputs:
#       db_file   - A database file to execute SQL commands into.
#                   Should be given as: "example.sqlite"
#       reset     - (Optional) Reset the previous database file
#                   if it exists. Default: False

#     Action:
#       Updates, resets or creates a database file if it not exists into
#       the current folder.
#     '''
#     conn = sqlite3.connect(db_file)
#     cur = conn.cursor()

#     if reset:
#         cur.executescript('''
#         DROP TABLE IF EXISTS Designs;
#         DROP TABLE IF EXISTS Designers;
#         DROP TABLE IF EXISTS Studios;
#         DROP TABLE IF EXISTS Categories;
#         DROP TABLE IF EXISTS Awards;
#         ''')

#     cur.executescript('''
#     CREATE TABLE IF NOT EXISTS Designs (
#         design_id  INTEGER NOT NULL PRIMARY KEY UNIQUE,
#         design_name             TEXT UNIQUE,
#         award_type_id           INTEGER,
#         category_id             INTEGER,
#         designer_id             INTEGER,
#         studio_id               INTEGER,
#         design_page             TEXT,
#         thumbnail_img_link   TEXT
#     );

#     CREATE TABLE IF NOT EXISTS Designers (
#         designer_id  INTEGER NOT NULL PRIMARY KEY UNIQUE,
#         designer_name   TEXT UNIQUE,
#         designer_page   TEXT UNIQUE
#     );

#     CREATE TABLE IF NOT EXISTS Studios (
#         id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#         studio_name     TEXT UNIQUE
#     );

#     CREATE TABLE IF NOT EXISTS Categories (
#         id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#         category_name   TEXT UNIQUE
#     );

#     CREATE TABLE IF NOT EXISTS Awards (
#         id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#         award_type      TEXT UNIQUE
#     );
#     ''')

#     cur.execute('''INSERT OR IGNORE INTO Awards (award_type)
#                                                     VALUES ( ? )''', (award_type, ))
#     cur.execute('SELECT id FROM Awards WHERE award_type = ? ', (award_type, ))
#     award_type_id = cur.fetchone()[0]

#     cur.execute('''INSERT OR IGNORE INTO Categories (category_name)
#                                                     VALUES ( ? )''', (category_name, ))
#     cur.execute('SELECT id FROM Categories WHERE category_name = ? ', (category_name, ))
#     category_id = cur.fetchone()[0]

#     cur.execute('''INSERT OR IGNORE INTO Designers (designer_id, designer_name, designer_page)
#                             VALUES ( ?, ?, ? )''', (designer_id, designer_name, designer_page))

#     cur.execute('''INSERT OR IGNORE INTO Studios (studio_name)
#                                                     VALUES ( ? )''', (studio_name, ))
#     cur.execute('SELECT id FROM Studios WHERE studio_name = ? ', (studio_name, ))
#     studio_id = cur.fetchone()[0]

#     cur.execute('''INSERT OR REPLACE INTO Designs
#     (design_id, design_name, award_type_id, category_id, designer_id, studio_id, design_page, thumbnail_img_link)
#     VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)''', (design_id, design_name, award_type_id, category_id, designer_id, studio_id, design_page, thumbnail_img_link))

#     conn.commit()
#     conn.close()


winners_url = "https://competition.adesignaward.com/winners.php"
# Testing URL for HTML Errors:
# winners_url = "https://www.google.com/search?q=test"

root_url, winners_html = read_URL(winners_url)
winners_dict = read_winners_page(root_url, winners_html, "lxml")
designs_dict = read_design_page(winners_dict, "lxml")
# sql_executer("data_raw.sqlite", reset=True)

# for item in winners_dict.items():
#     print(item)

timer_end = timer()
print(f"Code executed in {timer_end - timer_start} seconds.")
