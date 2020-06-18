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
import socket
from http.server import BaseHTTPRequestHandler

from bs4 import BeautifulSoup

# Ignore SSL certificate errors:
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Actual URL for data:
url = "https://competition.adesignaward.com/winners.php"

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
# for design in soup.find_all(""):
