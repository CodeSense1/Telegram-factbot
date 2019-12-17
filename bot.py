import requests  # Tällä tehdään http pyyntöjä ja postauksia
import json

from random import choice


class SimpleBot:

    """ Hieno botti, se osaa lähetellä viestejä, sekä vastaanottaa päivityksiä """

    def __init__(self):
        with open("data.json") as jsonFile:
            self.data = json.load(jsonFile)

        self.token = self.data["token"]
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
        url = self.baseUrl + "/sendMessage?chat_id={}&text={}".format(chatId, msg)
        if msg is not None:
            requests.post(url)


class AwesomeBot(SimpleBot):

    def advancedReply(self, msg):
        """ Personoitu vastaus """
        for word in msg.split():
            try:
                for item in self.data["data"]:
                    if item.get(word.lower(), None) is not None:
                        return word.capitalize() + ": " + choice(item.get(word.lower()))
            except KeyError:
                continue

        return None

    def addReply(self, person, reply):
        if person in self.data["data"]:
            self.data["data"][person].append(reply)
            # Send message that adding was succesful?

        else:
            self.data["data"][person] = [reply]


bot = AwesomeBot()


def makeReply(msg):
    reply = None
    if msg:
        reply = "Hi i am a bot"

    return reply


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

                # if "stop" in message:
                #     disabled = True
                #     reply = "I am now disabled :("

                chatId = item["message"]["chat"]["id"]  # Who ever sent the message

                bot.sendMessage(reply, chatId)

            except KeyError:
                reply = None
