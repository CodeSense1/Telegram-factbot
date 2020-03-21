import requests  # Tällä tehdään http pyyntöjä ja postauksia
import json
from difflib import get_close_matches

import sqlite3 as sq

from random import choice


class SimpleBot:

    """ Hieno botti, se osaa lähetellä viestejä, sekä vastaanottaa päivityksiä """

    def __init__(self):
        self.db = "data.db"
        self.token = '1113220905:AAGTEpqiKVspGryGfGKkfwzP188jGSxtcUA'  # self.initBot()
        self.baseUrl = "https://api.telegram.org/bot{}".format(self.token)

    def pollEvents(self, offset=None):
        """ Tekee http-get pyynnön telegram api sivustolle, sieltä
            saa tarvittavat tiedot botin loogisen toiminnallisuuden
            toteuttamiseen.

            Voit katsoa esimerkin json-tiedostosta, joka tämä funktio palauttaa
            osoitteessa: https://api.telegram.org/bot726370229:AAFf-Dcw_TWzeRzRLGuKCx5XuqUetfvMWI8/getUpdates?timeout=100
        """
        url = self.baseUrl + "/getUpdates?timeout=100"
        if offset:
            url = url + "&offset={}".format(offset + 1)

        req = requests.get(url)
        return json.loads(req.content)

    def sendMessage(self, msg, chatId):
        """ Tekee http-post pyynnön annettuun chatIdseen ja kirjoittaa annetun viestin """
        url = self.baseUrl + \
            "/sendMessage?chat_id={}&text={}".format(chatId, msg)
        if msg is not None:
            requests.post(url)

    def initBot(self):
        conn = sq.connect(self.db)
        cur = conn.cursor()
        cur.execute("select * from secret")
        return cur.fetchone()[0]


class AwesomeBot(SimpleBot):

    def __init__(self):
        super().__init__()
        self.replies = [
            "Kaikkea kanssa, tämmöistä ei saisi äidille näyttää...",
            "Jaahas, vai tuli semmonen lisättyä...\nMeneeköhän tuo hallitukselta läpi?",
            "Voisit sinäkin siitä mennä vaikka töihin!"
        ]

    def advancedReply(self, msg):
        """ Personoitu vastaus """
        words = msg.split()
        if (words[0] == "/lisaa"):
            # Lisätään uusi himmeli
            # select name, fact from users u inner join person_facts on userid = u.id inner join fact f on f.id = factid where u.id = 34;
            try:
                name = words[1]
                fact = " ".join(words[2:])
                addfactToDb(name, fact, self.db)
            except IndexError:
                return "Luulisi insinöörin osaavan antaa inputtia oikeassa muodossa!\n Oikea muoto: \lisaa <nimi> <fakta>"

            return choice(self.replies)

        # Tähän pitää keksiä tehokkaampi ratkaisu
        # koska tätä kutsutaan usein,
        # lineaarinen tehokkuus ei ole kovin hyvä
        conn = sq.connect(self.db)
        cur = conn.cursor()
        for word in words:
            quote = findRandomQuoteByName(word, self.db)
            if quote:
                return quote
        return None

        conn.close()

    # def addReply(self, person, reply):
    #     if person in self.data["data"]:
    #         self.data["data"][person].append(reply)
    #         # Send message that adding was succesful?

    #     else:
    #         self.data["data"][person] = [reply]


def findRandomQuoteByName(name, dbname):

    # Tämä on hirveän näköistä,
    # älä ota mallia!
    conn = sq.connect(dbname)
    cur = conn.cursor()
    q = "select id from users where name = '{0}' limit 1".format(name)
    cur.execute(q)
    uid = cur.fetchone()
    if uid:
        cur.execute(
            "select fact from person_facts inner join fact f on f.id = factid where userid = {0}".format(uid[0]))
        ret = cur.fetchall()

        return choice(ret)[0]
    else:
        return None


def addfactToDb(name, fact, dbname):
    conn = sq.connect(dbname)
    cur = conn.cursor()

    q = "select id from users where name = '{0}' limit 1".format(name)
    cur.execute(q)
    res = cur.fetchone()
    if res:
        # There is already entry with this name
        userid = res[0]
    else:
        lastrow = cur.execute(
            "insert into users values(null, '{0}')".format(name))
        userid = lastrow.lastrowid

    insertedRow = cur.execute(
        "insert into fact values(null, '{0}')".format(fact))
    factid = insertedRow.lastrowid
    cur.execute(
        "insert into person_facts values({0}, {1})".format(userid, factid))
    conn.commit()
    conn.close()


bot = AwesomeBot()
updateId = None
disabled = False

while not disabled:
    updates = bot.pollEvents(offset=updateId)

    try:
        updates = updates["result"]
    except KeyError:
        print("Mitä vittua?!\n\n")
        print(updates)

        disabled = True

    if updates:
        for item in updates:
            updateId = item["update_id"]

            try:
                message = item["message"]["text"]  # text that was sent
                reply = bot.advancedReply(message)

                # Who ever sent the message
                chatId = item["message"]["chat"]["id"]

                bot.sendMessage(reply, chatId)

            except KeyError:
                reply = None
