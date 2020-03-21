import json
import sqlite3 as sq


conn = sq.connect("data.db")
cur = conn.cursor()

data = {}
with open("data.json") as file:
    data = json.load(file)


for line in data["data"]:
    key = list(line.keys())[0]
    values = line[key]
    lastrow = cur.execute("insert into users values(null, '{0}')".format(key))
    userid = lastrow.lastrowid

    for fact in values:
        insertedRow = cur.execute(
            "insert into fact values(null, '{0}')".format(fact))
        factid = insertedRow.lastrowid
        cur.execute(
            "insert into person_facts values({0}, {1})".format(userid, factid))


# ÄLÄ KOSKE JOS ET TIEDÄ MITÄ TEET!
# -------------------
# conn.commit()
# conn.close()
# -------------------
