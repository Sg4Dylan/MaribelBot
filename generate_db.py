import sqlite3

def createDB(db_name):
    conn = sqlite3.connect(db_name)
    print ("Opened database successfully")
    conn.execute('''CREATE TABLE MARIBELLOG
           (UTCTIME TEXT PRIMARY KEY NOT NULL,
           CHATID TEXT,
           GROUPNAME TEXT,
           FIRSTNAME TEXT,
           LASTNAME TEXT,
           USERNAME TEXT,
           MESSAGE TEXT);''')
    print ("Table created successfully")
    conn.close()

createDB("maribel_log.db")
