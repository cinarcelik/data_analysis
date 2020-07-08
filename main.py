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
        {"award_type": ... ,
         "category_name": ... ,
         "designer_name": ... ,
         "designer_id": ... ,
         "design_page": ... ,
         "designer_page": ...},
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

            minor_dict["award_type"] = award_type
            minor_dict["category_name"] = category_name
            minor_dict["designer_name"] = designer_name
            minor_dict["designer_id"] = int(designer_id)
            minor_dict["design_page"] = design_page
            minor_dict["designer_page"] = designer_page
            main_dict[int(design_id)] = minor_dict

    return main_dict


# def sql_executer(dictionary, design_id, db_file, reset=False):
#     '''
#     Inputs:
#       dictionary    - A dictionary of data.
#       design_id     - ID of a design in the dictionary.
#       db_file       - A database file to execute SQL commands into.
#                       Should be given as: "example.sqlite"
#       reset         - (Optional) Reset the previous database file
#                       if it exists. Default: False

#     Action:
#       Updates, resets or creates a database file if it not exists into
#       the current folder.

#     Input Dictionary Style:
#       {design_id:
#         {"image_link": ... ,
#          "team_members": ... ,
#          "design_name": ... ,
#          "prim_func": ... ,
#          "inspiration": ... ,
#          "description": ... ,
#          "flow": ... ,
#          "dur_loc": ... ,
#          "prod_tech": ... ,
#          "specifications": ... ,
#          "tags": ... ,
#          "res_abst": ... ,
#          "challenge": ... ,
#          "add_date": ... ,
#          "img_credits": ... ,
#          "patents": ... ,
#          "award_type": ... ,
#          "category_name": ... ,
#          "designer_name": ... ,
#          "designer_id": ... ,
#          "design_page": ... ,
#          "designer_page": ...},
#       }
#     '''
#     conn = sqlite3.connect(db_file)
#     cur = conn.cursor()

#     if reset:
#         cur.executescript('''
#         DROP TABLE IF EXISTS Designs;
#         DROP TABLE IF EXISTS Designers;
#         DROP TABLE IF EXISTS Categories;
#         DROP TABLE IF EXISTS Awards;
#         ''')

#     cur.executescript('''
#     CREATE TABLE IF NOT EXISTS Designs (
#         design_id           INTEGER NOT NULL PRIMARY KEY UNIQUE,
#         design_name         TEXT UNIQUE,
#         award_type_id       INTEGER,
#         category_id         INTEGER,
#         designer_id         INTEGER,
#         design_page         TEXT,
#         image_link          TEXT,
#         team_members        TEXT,
#         prim_func           TEXT,
#         inspiration         TEXT,
#         description         TEXT,
#         flow                TEXT,
#         dur_loc             TEXT,
#         prod_tech           TEXT,
#         specifications      TEXT,
#         tags                TEXT,
#         res_abst            TEXT,
#         challenge           TEXT,
#         add_date            TEXT,
#         img_credits         TEXT,
#         patents             TEXT
#     );

#     CREATE TABLE IF NOT EXISTS Designers (
#         designer_id     INTEGER NOT NULL PRIMARY KEY UNIQUE,
#         designer_name   TEXT UNIQUE,
#         designer_page   TEXT UNIQUE
#     );

#     CREATE TABLE IF NOT EXISTS Categories (
#         id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#         category_name   TEXT UNIQUE
#     );

#     CREATE TABLE IF NOT EXISTS Awards (
#         id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#         award_type      TEXT UNIQUE
#     );
#     ''')

#     cur.execute('''INSERT OR IGNORE INTO Awards (award_type)
#                                                     VALUES ( ? )''', (dictionary[design_id]["award_type"], ))
#     cur.execute('SELECT id FROM Awards WHERE award_type = ? ', (dictionary[design_id]["award_type"], ))
#     award_type_id = cur.fetchone()[0]

#     cur.execute('''INSERT OR IGNORE INTO Categories (category_name)
#                                                     VALUES ( ? )''', (dictionary[design_id]["category_name"], ))
#     cur.execute('SELECT id FROM Categories WHERE category_name = ? ', (dictionary[design_id]["category_name"], ))
#     category_id = cur.fetchone()[0]

#     cur.execute('''INSERT OR IGNORE INTO Designers (designer_id, designer_name, designer_page)
#                             VALUES ( ?, ?, ? )''', (dictionary[design_id]["designer_id"],
#                                                     dictionary[design_id]["designer_name"],
#                                                     dictionary[design_id]["designer_page"]))

#     cur.execute('''INSERT OR IGNORE INTO Designs
#     (design_id, design_name, award_type_id, category_id, designer_id, design_page, image_link, team_members, prim_func,
#     inspiration, description, flow, dur_loc, prod_tech, specifications, tags, res_abst, challenge, add_date, img_credits,
#     patents)
#     VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,? )''',
#     (design_id, dictionary[design_id]["design_name"], award_type_id, category_id,
#     dictionary[design_id]["designer_id"], dictionary[design_id]["design_page"], dictionary[design_id]["image_link"],
#     dictionary[design_id]["team_members"], dictionary[design_id]["prim_func"], dictionary[design_id]["inspiration"],
#     dictionary[design_id]["description"], dictionary[design_id]["flow"], dictionary[design_id]["dur_loc"],
#     dictionary[design_id]["prod_tech"], dictionary[design_id]["specifications"], dictionary[design_id]["tags"],
#     dictionary[design_id]["res_abst"], dictionary[design_id]["challenge"], dictionary[design_id]["add_date"],
#     dictionary[design_id]["img_credits"], dictionary[design_id]["patents"]))

#     conn.commit()
#     conn.close()


# def read_design_page(dictionary, parser):
#     '''
#     Inputs:
#       dictionary    - Winners page dictionary
#       parser        - A parser to use to make a soup object with BeautifulSoup.
#                       Options are: "html.parser", "lxml", "xml", "html5lib".

#     Actions:
#       Reads the given dictionary, uses Design URLs in it to retrieve data
#       about the designs, then builds another super dictionary with the
#       new data, including the input dictionary's keys and values. Calls
#       sql_executer() and writes the final dictionaries ID by ID to a
#       sqlite database file.

#     Input Dictionary Style:
#       {design_id:
#         {"award_type": ... ,
#          "category_name": ... ,
#          "designer_name": ... ,
#          "designer_id": ... ,
#          "design_page": ... ,
#          "designer_page": ...},
#       }

#     Output Dictionary Style:
#       {design_id:
#         {"image_link": ... ,
#          "team_members": ... ,
#          "design_name": ... ,
#          "prim_func": ... ,
#          "inspiration": ... ,
#          "description": ... ,
#          "flow": ... ,
#          "dur_loc": ... ,
#          "prod_tech": ... ,
#          "specifications": ... ,
#          "tags": ... ,
#          "res_abst": ... ,
#          "challenge": ... ,
#          "add_date": ... ,
#          "img_credits": ... ,
#          "patents": ... ,
#          "award_type": ... ,
#          "category_name": ... ,
#          "designer_name": ... ,
#          "designer_id": ... ,
#          "design_page": ... ,
#          "designer_page": ...},
#       }
#     '''
#     titles_dict = {"DESIGN NAME:": "design_name",
#     "PRIMARY FUNCTION:": "prim_func",
#     "INSPIRATION:": "inspiration",
#     "UNIQUE PROPERTIES / PROJECT DESCRIPTION:": "description",
#     "OPERATION / FLOW / INTERACTION:": "flow",
#     "PROJECT DURATION AND LOCATION:": "dur_loc",
#     "PRODUCTION / REALIZATION TECHNOLOGY:": "prod_tech",
#     "SPECIFICATIONS / TECHNICAL PROPERTIES:": "specifications",
#     "TAGS:": "tags",
#     "RESEARCH ABSTRACT:": "res_abst",
#     "CHALLENGE:": "challenge",
#     "ADDED DATE:": "add_date",
#     "IMAGE CREDITS:": "img_credits",
#     "PATENTS/COPYRIGHTS:": "patents"}

#     conn = sqlite3.connect("data.sqlite")
#     cur = conn.cursor()

#     for design_id in dictionary.keys():
#         # Check if the details of a design are already written into the database:
#         try:
#             cur.execute("SELECT * FROM Designs WHERE design_id= ?", (design_id, ))
#             d_id = cur.fetchone()[0]
#             print(f"A design with the ID of {d_id} found in the database.")
#             continue
#         except:
#             pass

#         design_page = dictionary[design_id]["design_page"]
#         root_url, html = read_URL(design_page)
#         soup = BeautifulSoup(html, parser)
#         design_image_link = root_url + "/" + f"award-winning-design.php?ID={design_id}"

#         design_details_tag = soup.find(text="DESIGN DETAILS").parent
#         design_details_list = []
#         for element in design_details_tag.find_all_next(string=True):
#             element = element.strip()
#             if element == "":
#                 continue
#             design_details_list.append(element)
#             if element == "AWARD DETAILS":
#                 break

#         design_details_dict = {}
#         details = {}
#         details["image_link"] = design_image_link
#         string = ''.join(design_details_list)
#         tm_match = re.findall(r"TEAM MEMBERS \(\d*\) :", string)[0]
#         if design_details_list[design_details_list.index(tm_match) + 1] == "IMAGE CREDITS:":
#             details["team_members"] = "-"
#         else:
#             details["team_members"] = design_details_list[design_details_list.index(tm_match) + 1]

#         for title, variable in titles_dict.items():
#             if title in design_details_list:
#                 try:
#                     details[variable] = design_details_list[design_details_list.index(title) + 1]
#                 except IndexError:
#                     details[variable] = "-"
#             else:
#                 details[variable] = "-"

#         design_details_dict[design_id] = details
#         design_details_dict[design_id].update(dictionary[design_id])

#         print(design_details_dict, "\n")
#         sql_executer(design_details_dict, design_id, "data.sqlite")
#         print(f"Details of the design no.{design_id} is written to the database. \n\n")


def read_designer_page(dictionary, parser):
    '''
    Inputs:
      dictionary    - Winners page dictionary
      parser        - A parser to use to make a soup object with BeautifulSoup.
                      Options are: "html.parser", "lxml", "xml", "html5lib".

    Actions:
      Reads the given dictionary, uses Designer URLs in it to retrieve data
      about the designers, then builds another super dictionary with the
      new data, including the input dictionary's keys and values. Calls
      sql_executer() and writes the final dictionaries ID by ID to a
      sqlite database file.

    Input Dictionary Style:
      {design_id:
        {"award_type": ... ,
         "category_name": ... ,
         "designer_name": ... ,
         "designer_id": ... ,
         "design_page": ... ,
         "designer_page": ...},
      }

    Output Dictionary Style:
      {designer_id:
        {"designer_page_name": ... ,
         "designer_img_url": ... ,
         "about": ... ,
         "stat_art": ... ,
         "organization": ... ,
         "awards": ... ,
         "lang_skills": ... ,
         "hobbies": ... ,
         "website": ... ,
         "regs_date": ... ,
         "country": ... ,
         "acc_type": ...},
      }
    '''
    titles_dict = {"STATEMENT OF ART": "stat_art",
    "ORGANIZATION": "organization",
    "EDUCATION": "education",
    "EXPERIENCE": "experience",
    "PRIVATE EXHIBITIONS": "private_exh",
    "MIXED EXHIBITIONS": "mixed_exh",
    "EVENTS": "events",
    "NON-DESIGN OCCUPATION": "non_des_occ",
    "AWARDS": "awards",
    "PRESS APPEARANCES": "press_app",
    "BOOKS": "books",
    "LANGUAGE SKILLS": "lang_skills",
    "COMPUTER LITERACY": "comp_lit",
    "COURSES, SEMINARS AND WORKSHOPS:": "cours_sems_wss",
    "HOBBIES": "hobbies",
    "CLIENTELE": "clientele",
    "WEB SITE": "website",
    "PORTFOLIO URL": "portfolio_url",
    "RSS URL": "rss_url",
    "REGISTRATION DATE": "regs_date",
    "COUNTRY": "country",
    "ACCOUNT TYPE": "acc_type"}

    # conn = sqlite3.connect("data.sqlite")
    # cur = conn.cursor()

    for design_id in dictionary.keys():
        # Check if the details of a design are already written into the database:
        # try:
        #     cur.execute("SELECT * FROM Designs WHERE design_id= ?", (design_id, ))
        #     d_id = cur.fetchone()[0]
        #     print(f"A design with the ID of {d_id} found in the database.")
        #     continue
        # except:
        #     pass

        designer_page = dictionary[design_id]["designer_page"]
        designer_id = dictionary[design_id]["designer_id"]
        root_url, html = read_URL(designer_page)
        soup = BeautifulSoup(html, parser)

        # Make list with the usable data from the designer's page to use it later:
        designer_profiles_tag = soup.find(text="Designer Profiles").parent
        designer_page_contents_list = []
        for element in designer_profiles_tag.find_all_next(string=True):
            element = element.strip()
            # Skip this iteration if the element is just a blank line, a colon or a dot:
            if element == "" or element == ":" or element == ".":
                continue
            # Stop filling the list at the "Press Members:" section:
            if element == "Press Members:":
                break
            designer_page_contents_list.append(element)

        print("\n\nDESIGNER PAGE CONTENTS LIST (designer_page_contents_list):")
        print(designer_page_contents_list, "\n")

        designer_details_dict = {}
        designer_details_dict[designer_id] = {}
        details_list = []

        # Fetch the designer name from the designer's page:
        # (In some occurences, designer name on the winners page and designer name on the designer's page are different.)
        # designer_page_name    = designer name on the designer's page
        # designer_name         = designer name on the winners page
        designer_page_name = designer_page_contents_list[1].replace(">", "").strip()
        designer_name = dictionary[design_id]["designer_name"]
        designer_details_dict[designer_id]["designer_name"] = designer_name
        if designer_name == designer_page_name:
            print("\tThe designer name on the designer's page and the winners page are the same.\n")
        else:
            print("\tTHE DESIGNER NAME ON THE DESIGNER'S PAGE AND THE WINNERS PAGE ARE DIFFERENT!")
            print(f"\tName on the winners page:    {designer_name}    <--- Selected one")
            print(f"\tName on the designer's page: {designer_page_name}\n")

        # Fetch the designer's image url:
        designer_image_link_whole = soup.find(src=re.compile("designer/"))
        if designer_image_link_whole is None:
            print("\tDESIGNER IMAGE NOT FOUND \n")
        else:
            designer_image_link = re.findall("designer.*.jpg", str(designer_image_link_whole))[0]
            designer_image_url = root_url + "/" + designer_image_link
            print(f"\tDESIGNER IMAGE URL: {designer_image_url} \n")
            designer_details_dict[designer_id]["designer_img_url"] = designer_image_url

        # Fetch the designer's "About" section:
        for element in designer_page_contents_list:
            about_match = re.match("About.*", element)
            # if there is a match... (if about_match variable is a Match object):
            if about_match:
                about_name = about_match.group().strip()    # EX: about_name = "About Nedim Mutevelic"
                about_name_index = designer_page_contents_list.index(about_name)
                about_text = designer_page_contents_list[about_name_index + 1].lstrip(":").strip()
                designer_details_dict[designer_id]["about"] = about_text

        # THE MAIN LIST TO DICTIONARY ACTION:
        index_diff = 0
        for item_1 in designer_page_contents_list:
            if item_1 in titles_dict.keys():
                title_index_1 = designer_page_contents_list.index(item_1)

                # Fix for "ACCOUNT TYPE" index. it is an irregular element for the algorithm because it is the last item in the designer_page_contents_list:
                if item_1 == "ACCOUNT TYPE":
                    designer_details_dict[designer_id][titles_dict[item_1]] = designer_page_contents_list[title_index_1 + 1]

                for item_2 in designer_page_contents_list:
                    if item_2 in titles_dict.keys():
                        title_index_2 = designer_page_contents_list.index(item_2)
                        index_diff = title_index_2 - title_index_1
                        if index_diff > 2:
                            for idx in range(title_index_1 + 1, title_index_2):
                                details_list.append(designer_page_contents_list[idx])
                            designer_details_dict[designer_id][titles_dict[item_1]] = details_list
                            details_list = []
                            # print(f"First index = {title_index_1}, Second index = {title_index_2}")
                            # print(f"\t(There are {index_diff - 1} elements between the indexes.)")
                        elif index_diff > 1:
                            designer_details_dict[designer_id][titles_dict[item_1]] = designer_page_contents_list[title_index_1 + 1]
                            # print(f"First index = {title_index_1}, Second index = {title_index_2}")
                            # print("\t(There is only 1 element between the indexes.)")
                        else:
                            continue
                        break

        print("DESIGNER DETAILS DICTIONARY (designer_details_dict):")
        print(designer_details_dict, "\n")

        # sql_executer(design_details_dict, design_id, "data.sqlite")
        # print(f"Details of the designer no.{designer_id} is written to the database. \n\n")



winners_url = "https://competition.adesignaward.com/winners.php"
# Testing URL for HTML Errors:
# winners_url = "https://www.google.com/search?q=test"

root_url, winners_html = read_URL(winners_url)
winners_dict = read_winners_page(root_url, winners_html, "lxml")
# read_design_page(winners_dict, "lxml")
read_designer_page(winners_dict, "lxml")


timer_end = timer()
tdelta = timer_end - timer_start
mins, secs = divmod(tdelta, 60)
mins = int(mins)
secs = round(secs)
print(f"Code executed in {mins} minutes and {secs} seconds ")
