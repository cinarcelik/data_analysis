"""
Data Analysis Project's main executer file.
Written by Çınar Çelik.
Turkey - 2020
"""

import sqlite3
import ssl
import urllib.error
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


url = "https://competition.adesignaward.com/winners.php"

with urllib.request.urlopen(url, context=ctx) as response:
    html = response.read()

    # if html.getcode() != 200:
    #     print("Error code=", html.getcode(), url)
    #     quit()

    print(html)
