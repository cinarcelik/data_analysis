"""
Data Analysis Project's main executer file.
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
from time import sleep

from bs4 import BeautifulSoup

# Ignore SSL certificate errors:
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Actual URL for data:
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


award_count_total = 0
platinum_award_count = 0
golden_award_count = 0
silver_award_count = 0
bronze_award_count = 0
regular_award_count = 0

soup = BeautifulSoup(html, "lxml")
for tag in soup.find_all("tr", limit=25):
    recognition = tag.find(string=re.compile("Award Winner"))
    if recognition is not None:
        category = recognition[recognition.find("for") + 4 : recognition.find("Category") - 1].strip()
        design_img_small_link = root_url + tag.find("img").get("src")
        design_page = root_url + tag.find(href=re.compile("design.php")).get("href")
        design_name = tag.find(href=re.compile("design.php")).get_text().strip()
        award_type = recognition[ : recognition.find("A' Design Award")].strip()
        if award_type == "":
            award_type = "Regular"
        if award_type == "Platinum":
            platinum_award_count += 1
        elif award_type == "Golden":
            golden_award_count += 1
        elif award_type == "Silver":
            silver_award_count += 1
        elif award_type == "Bronze":
            bronze_award_count += 1
        elif award_type == "Regular":
            regular_award_count += 1
        designer_page = root_url + tag.find(href=re.compile("designer.php")).get("href")
        designer_studio_name = tag.find(href=re.compile("designer.php")).get_text()
        designer_name = designer_studio_name[ : designer_studio_name.find("for") - 1]
        studio_name = designer_studio_name[designer_studio_name.find("for") + 4 : ]
        award_count_total += 1

        print("=========================================")
        print(f"Category: {category}")
        print(f"Award Type: {award_type} Award")
        print(f"Design Name: {design_name}")
        print(f"Design Image: {design_img_small_link}")
        print(f"Design Page: {design_page}")
        print(f"Designer: {designer_name}")
        print(f"Designer Page: {designer_page}")
        print(f"Studio/Client/Brand: {studio_name}")
        print("=========================================\n")

print(f"Total Award Count: {award_count_total}")
print(f"Platinum Award Count: {platinum_award_count}")
print(f"Golden Award Count: {golden_award_count}")
print(f"Silver Award Count: {silver_award_count}")
print(f"Bronze Award Count: {bronze_award_count}")
print(f"Regular Award Count: {regular_award_count}")
