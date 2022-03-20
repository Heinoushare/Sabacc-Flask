"""Helper file for application.py"""

# Import libraries
from flask import redirect, render_template, session
from functools import wraps
import random
from flask_socketio import emit
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///sabacc.db")

# Helper functions for application.py


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def constructDeck():
    """Construct deck and deal cards"""

    # Declare deck variable
    deck = "1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,0,0,-2,-2,-8,-8,-11,-11,-13,-13,-14,-14,-15,-15,-17,-17"
    deckList = list(deck.split(","))

    # Deal cards
    player1_hand = ""
    for i in range(2):
        randDex = random.randint(0, len(deckList) - 1)
        if player1_hand == "":
            player1_hand = deckList[randDex]
        else:
            player1_hand = player1_hand + "," + deckList[randDex]
        deckList.pop(randDex)
    player2_hand = ""
    for i in range(2):
        randDex = random.randint(0, len(deckList) - 1)
        if player2_hand == "":
            player2_hand = deckList[randDex]
        else:
            player2_hand = player2_hand + "," + deckList[randDex]
        deckList.pop(randDex)

    # "Stringify" deck
    deck = ""
    for card in deckList:
        if deck == "":
            deck = card
        else:
            deck = deck + "," + card

    data = {"deck": deck, "player1_hand": player1_hand, "player2_hand": player2_hand}
    return data


def reshuffleDeck(game, outCards):
    """Reconstruct deck from disard cards"""

    deckList = list("1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,0,0,-2,-2,-8,-8,-11,-11,-13,-13,-14,-14,-15,-15,-17,-17".split(","))
    for card in outCards:
        if card != "":
            deckList.remove(card)
    return deckList


def foldCards(game, p1Hand, p2Hand):
    """Get the results of a player folding"""

    player1_hand = ""
    player2_hand = ""
    deckList = []
    if len(deckList) < 4:
        outCards = list(p1Hand.split(",")) + list(p2Hand.split(","))
        deckList = reshuffleDeck(game, outCards)

    deck = ""

    # Deal cards
    for i in range(2):
        randDex = random.randint(0, len(deckList) - 1)
        if player1_hand == "":
            player1_hand = deckList[randDex]
        else:
            player1_hand = player1_hand + "," + deckList[randDex]
        deckList.pop(randDex)

    for i in range(2):
        randDex = random.randint(0, len(deckList) - 1)
        if player2_hand == "":
            player2_hand = deckList[randDex]
        else:
            player2_hand = player2_hand + "," + deckList[randDex]
        deckList.pop(randDex)

    # Reconstruct deck
    for card in deckList:
        if deck == "":
            deck = card
        else:
            deck = deck + "," + card

    returnDict = {"deck": deck, "player1_hand": player1_hand, "player2_hand": player2_hand}
    return returnDict


def emitGame(namespace, game, users):
    """Send game data to players"""

    try:
        emit(namespace, game, room=users[game["player1_id"]])
    except KeyError:
        pass

    try:
        emit(namespace, game, room=users[game["player2_id"]])
    except KeyError:
        pass


def calcHandVal(strHand):
    """Calculate the value of the players' hands"""

    # Construct ordered hand
    hand = []
    for card in list(strHand.split(",")):
        hand.append(int(card))
    hand.sort()

    sum = 0
    for card in hand:
        sum += card

    val = str(sum)

    # Special cases of the Idiot's Array and Fairy Empress
    if len(hand) == 3 and hand[0] == 0 and hand[1] == 2 and hand[2] == 3:
        val = "023"
    if len(hand) == 2 and hand[0] == -2 and hand[1] == -2:
        val = "-22"

    return val


def getWinner(game):
    """Find the winner of game"""

    p1Val = calcHandVal(game["player1_hand"])
    p2Val = calcHandVal(game["player2_hand"])

    # Check if anybody has the Idiot's Array
    if p1Val == "023" and p2Val == "023":
        return -1
    elif p1Val == "023":
        return game["player1_id"]
    elif p2Val == "023":
        return game["player2_id"]

    p1Abs = abs(int(p1Val))
    p2Abs = abs(int(p2Val))

    # Check if anyone has bombed out
    if (p1Abs > 23 or p1Abs == 0) and (p2Abs > 23 or p2Abs == 0):
        return -1
    elif p1Abs > 23 or p1Abs == 0:
        return game["player2_id"]
    elif p2Abs > 23 or p2Abs == 0:
        return game["player1_id"]

    # If there are no special conditions, find the winner
    if p1Abs > p2Abs:
        return game["player1_id"]
    elif p2Abs > p1Abs:
        return game["player2_id"]
    elif p1Abs == p2Abs:
        if int(p1Val) > int(p2Val):
            return game["player1_id"]
        elif int(p2Val) > int(p1Val):
            return game["player2_id"]
        else:
            deckList = game["deck"].split(",")
            if len(deckList) < 2:
                deckList = reshuffleDeck(game, game["player1_hand"].split(",") + game["player2_hand"].split(","))
            player1_hand = game["player1_hand"] + "," + deckList.pop(random.randint(0, len(deckList) - 1))
            player2_hand = game["player2_hand"] + "," + deckList.pop(random.randint(0, len(deckList) - 1))
            deck = ""
            for c in deckList:
                if deck == "":
                    deck = c
                else:
                    deck = deck + "," + c
            db.execute(
                f"UPDATE games SET player1_hand = ?, player2_hand = ?, deck = ? WHERE game_id = {game['game_id']}", player1_hand, player2_hand, deck)
            return getWinner(game)