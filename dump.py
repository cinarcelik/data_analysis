"""
Written by Çınar Çelik.
Turkey - 2020
"""

import sqlite3
from timeit import default_timer as timer

timer_start = timer()

conn = sqlite3.connect('data_raw.sqlite')
cur = conn.cursor()

cur.execute('''SELECT Designs.design_name,
                      Awards.award_type, 
                      Categories.category_name, 
                      Designers.designer_name,
                      Studios.studio_name
               FROM Designs JOIN Awards JOIN Categories JOIN Designers JOIN Studios
               ON Designs.award_type_id = Awards.id
               AND Designs.category_id = Categories.id
               AND Designs.designer_id = Designers.id
               AND Designs.studio_id = Studios.id''')

count = 0
for row in cur:
    print(row)
    count = count + 1
print(f"\nDumping ended successfully.\n{count} rows counted.")

cur.close()

timer_end = timer()
print(f"Code executed in: {timer_end - timer_start} seconds.")
