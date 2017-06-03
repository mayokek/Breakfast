import sqlite3

con = sqlite3.connect("data/Breakfast.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

def get_tables():
    cur.execute("""CREATE TABLE IF NOT EXISTS servers(id TEXT, type TEXT, value TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS blacklist(id TEXT, name TEXT, discrim TEXT, reason TEXT)""")

def insert_data_entry(id, type, value):
    cur.execute("""INSERT INTO servers(id, type, value) VALUES (?, ?, ?)""", (id, type, value))
    con.commit()

def read_data_entry(id, type):
    cur.execute("""SELECT value FROM servers WHERE id=(?) AND type=(?)""", (id, type))
    x = None
    try:
        x = cur.fetchone()[0]
    except:
        if type == "mod-role":
            insert_data_entry(id, type, "Mods")
            x = "Mods"
        elif type == "mute-role":
            insert_data_entry(id, type, "Muted")
            x = "Muted"
        elif type == "join-leave-channel":
            insert_data_entry(id, type, None)
            x = None
        elif type == "auto-role":
            insert_data_entry(id, type, None)
            x = None
    return x

def update_data_entry(id, type, value):
    e = read_data_entry(id, type)
    cur.execute("""UPDATE servers SET value=(?) WHERE id=(?) AND type=(?)""", (value, id, type))
    con.commit()

def delete_data_entry(id, type):
    cur.execute("""DELETE FROM servers WHERE id=(?) AND type=(?)""", (id, type))
    con.commit()

def blacklistuser(id, name, discrim, reason):
    cur.execute("""INSERT INTO blacklist(id, name, discrim, reason) VALUES (?, ?, ?, ?)""", (id, name, discrim, reason))
    con.commit()

def unblacklistuser(id):
    cur.execute("""DELETE FROM blacklist WHERE id=""" + id)
    con.commit()

def getblacklistuser(id):
    cur.execute("""SELECT id FROM blacklist WHERE id=""" + id)
    id = None
    name = None
    discrim = None
    reason = None
    try:
        id = cur.fetchone()[0]
    except:
        return None
    cur.execute("""SELECT name FROM blacklist WHERE id=""" + id)
    name = cur.fetchone()[0]
    cur.execute("""SELECT discrim FROM blacklist WHERE id=""" + id)
    discrim = cur.fetchone()[0]
    cur.execute("""SELECT reason FROM blacklist WHERE id=""" + id)
    reason = cur.fetchone()[0]
    entry = {"ID":id, "Name":name, "Discriminator":discrim, "reason":reason}
    return entry

def getblacklist():
    cur.execute("""SELECT id, name, discrim, reason FROM blacklist""")
    entries = []
    rows = cur.fetchall()
    for row in rows:
        entry = "ID: \"" + row["id"] + "\" Name: \"" + row["name"]  + "\" Discriminator: \"" + row["discrim"] + "\" Reason: \"" + row["reason"] + "\""
        entries.append(entry)
    return entries

get_tables()
