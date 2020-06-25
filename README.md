## A Data Analysis Project on A' Design Award 2019-2020 Period Winners
This is a practise project I have been developing on data analysis and visualization, using **SQLite**, **BeautifulSoup4** and **Matplotlib**.

As an **Industrial Designer**, I have wanted to work on a topic relevant to my major. So I have decided to use data from **A' Design Award**. It is one of the most famous among the various international design awards with its diverse categories and remarkable jury. My goal is to retrieve and analyze data about the winner designs from the [website](https://competition.adesignaward.com/winners.php), then beautifully visualize it to see the correlations between the designs and their designers.

## Dependencies
```python
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
```

## To-Do List
- [x] Repository setup and initial commit - *17.06.2020*
- [x] Retrieve raw data ------------------- *18.06.2020 - 19.06.2020*
- [x] Retrieve detailed data -------------- *20.06.2020 -*
- [ ] Organize all data ------------------- 
- [ ] Data visualization ------------------ 
