"""Sabacc website backend"""

# Import libraries
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *
from flask_socketio import SocketIO, send
import random
import yaml

# Get config.yaml data
config = {}
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Socket.IO message links
link = config["DOMAIN"]
socketio = SocketIO(app, cors_allowed_origins=[link, f"{link}/chat",
                                               f"{link}/game", f"{link}/bet", f"{link}/card", f"{link}/shift"])

# Declare dictionary to store key-value pairs of user ids and session ids
users = {}

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///sabacc.db")


@app.route("/")
def index():
    """Show home page"""

    # Get the user's id for later use
    user_id = session.get("user_id")

    usernames = {}
    games = db.execute(
        f"SELECT * FROM games WHERE (player1_id = ? OR player2_id = ?) AND completed = 0 ORDER BY game_id DESC", user_id, user_id)
    users = db.execute("SELECT * FROM users")
    for user in users:
        usernames[user["id"]] = user["username"]

    # Render the home page with the user's active game data
    return render_template("index.html", games=games, usernames=usernames)


@socketio.on("message", namespace="/chat")
def handleMessage(msg):
    """Global Chat Socket.IO Code"""

    # Send the message that was recieved to all users in the global chat
    send(msg, broadcast=True)


@app.route("/chat")
@login_required
def chat():
    """Global Chat"""

    user_id = session.get("user_id")
    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}")[0]
    return render_template("chat.html", user=user)


@app.route("/host", methods=["GET", "POST"])
@login_required
def host():
    """Host a game of Sabacc"""

    if request.method == "GET":
        return render_template("host.html")

    elif request.method == "POST":

        # Verify that player2 exists
        player2Username = request.form.get("player2")
        player2 = db.execute(f"SELECT * FROM users WHERE username = ? AND id != {session.get('user_id')}", player2Username)
        if len(player2) == 0:
            return apology("Invalid player 2 username")

        # Construct the deck and deal cards
        deckData = constructDeck()
        deck = deckData["deck"]
        player1_hand = deckData["player1_hand"]
        player2_hand = deckData["player2_hand"]

        db.execute("INSERT INTO games (player1_id, player2_id, player1_credits, player2_credits, hand_pot, sabacc_pot, deck, player1_hand, player2_hand, player_turn) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   session.get("user_id"), player2[0]["id"], 985, 985, 10, 20, deck, player1_hand, player2_hand, session.get("user_id"))
        game_id = db.execute("SELECT game_id FROM games WHERE player2_id = ? ORDER BY game_id DESC", player2[0]["id"])[0]["game_id"]

        # Redirect user to game
        return redirect(f"/game/{game_id}")


@socketio.on("game", namespace="/game")
def game_connect():
    """Connect to the game"""

    # Add user's Socket ID to the Socket ID dictionary for future use
    user_id = session.get("user_id")
    if not user_id:
        return
    sid = request.sid
    users[user_id] = sid


@socketio.on("bet", namespace="/bet")
def bet(data):
    """Recieve bet message"""

    # Set some variables for the whole function
    game_id = data["game_id"]
    action = data["action"]
    amount = data["amount"]
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    user_id = session.get("user_id")

    if game["phase"] != "betting":
        return

    # Find player phrases
    player = ""
    opponent = ""
    if user_id == game["player1_id"]:
        player = "player1"
        opponent = "player2"
    elif user_id == game["player2_id"]:
        player = "player2"
        opponent = "player1"
    else:
        return

    # If player 1 bets or checks
    if action == "bet" and player == "player1" and game["player_turn"] == game["player1_id"] and amount >= 0 and amount <= game["player1_credits"]:

        db.execute(f"UPDATE games SET player1_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, player_turn = ? WHERE game_id = {game_id}", game[
                   "player1_credits"] - amount, amount, None, game["hand_pot"] + amount, game["player2_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame("bet", game, users)

    # Player 2 calls
    elif action == "call" and player == "player2" and game["player_turn"] == game["player2_id"] and amount >= 0 and amount <= game["player2_credits"]:

        db.execute(f"UPDATE games SET player2_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, phase = ?, player_turn = ? WHERE game_id = {game_id}", game[
                   "player2_credits"] - amount, None, None, game["hand_pot"] + amount, "card", game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame("bet", game, users)

    # Player 1 calls
    elif action == "call" and player == "player1" and game["player_turn"] == game["player1_id"] and amount >= 0 and amount <= game["player1_credits"]:

        db.execute(f"UPDATE games SET player1_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, phase = ?, player_turn = ? WHERE game_id = {game_id}", game["player1_credits"
                                                                                                                                                                       ] - (
            game["player2_bet"] - game["player1_bet"]), None, None, game["hand_pot"] + amount - game["player1_bet"], "card", game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame("bet", game, users)

    # Player 2 folds
    elif action == "fold" and player == "player2" and game["player_turn"] == game["player2_id"]:

        # Re-deal cards
        results = foldCards(game, game["player1_hand"], game["player2_hand"])
        deck = results["deck"]
        player1_hand = results["player1_hand"]
        player2_hand = results["player2_hand"]

        db.execute(f"UPDATE games SET player1_credits = ?, player2_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, phase = ?, deck = ?, player1_hand = ?, player2_hand = ?, player_turn = ? WHERE game_id = {game_id}", game[
                   "player1_credits"] + game["hand_pot"] - 5, game["player2_credits"] - 5, None, None, 10, "betting", deck, player1_hand, player2_hand, game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame("bet", game, users)

    # Player 1 folds
    elif action == "fold" and player == "player1" and game["player_turn"] == game["player1_id"]:

        # Re-deal cards
        results = foldCards(game, game["player1_hand"], game["player2_hand"])
        deck = results["deck"]
        player1_hand = results["player1_hand"]
        player2_hand = results["player2_hand"]

        db.execute(f"UPDATE games SET player1_credits = ?, player2_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, phase = ?, deck = ?, player1_hand = ?, player2_hand = ?, player_turn = ? WHERE game_id = {game_id}", game[
                   "player1_credits"] - 5, game["player2_credits"] + game["hand_pot"] - 5, None, None, 10, "betting", deck, player1_hand, player2_hand, game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame("bet", game, users)

    # Player 2 raises
    elif action == "raise" and player == "player2" and game["player_turn"] == game["player2_id"] and amount >= game["player1_bet"] and amount <= game["player2_credits"]:

        db.execute(f"UPDATE games SET player2_credits = ?, player2_bet = ?, hand_pot = ?, player_turn = ? WHERE game_id = {game_id}", game[
                   "player2_credits"] - amount, amount, game["hand_pot"] + amount, game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame("bet", game, users)

    return


@socketio.on("card", namespace="/card")
def card(data):
    """Receive card message"""

    # Set some variables for the whole function
    game_id = data["game_id"]
    action = data["action"]
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    user_id = session.get("user_id")
    player1_hand = game["player1_hand"]
    player2_hand = game["player2_hand"]

    # Find player phrases
    player = ""
    opponent = ""
    if user_id == game["player1_id"]:
        player = "player1"
        opponent = "player2"
    elif user_id == game["player2_id"]:
        player = "player2"
        opponent = "player1"
    else:
        return

    if game["phase"] != "card":
        return

    # Player 1
    if player == "player1" and game["player_turn"] == game["player1_id"]:

        # Stand
        if action == "stand":
            db.execute(f"UPDATE games SET player1_card = ?, player_turn = ? WHERE game_id = {game_id}", action, game["player2_id"])
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
            emitGame("card", game, users)

        # Draw
        elif action == "draw":

            # Turn deck into a list
            deckList = list(game["deck"].split(","))

            # If deck is out of cards, re-shuffle discard cards
            if len(deckList) == 0:
                outCards = list(player1_hand.split(",")) + list(player2_hand.split(","))
                deckList = reshuffleDeck(game, outCards)

            # Add a card to player 1's hand
            drawn = deckList.pop(random.randint(0, len(deckList) - 1))
            if player1_hand == "":
                player1_hand = drawn
            else:
                player1_hand = player1_hand + "," + drawn

            # Reconstruct deck
            deck = ""
            for card in deckList:
                if deck == "":
                    deck = card
                else:
                    deck = deck + "," + card

            db.execute(
                f"UPDATE games SET player1_hand = ?, player1_card = ?, player_turn = ?, deck = ? WHERE game_id = {game_id}", player1_hand, action, game["player2_id"], deck)
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
            emitGame("card", game, users)

        # Trade
        elif action == "trade":
            discard = data["card"]  # If there's gonna be a KeyError, get it done early

            # Update shift protected cards
            p1_proced = game["player1_protected"]
            p1ProcList = []
            if p1_proced != None:
                p1ProcList = list(p1_proced.split(","))
                for card in p1ProcList:
                    if card == discard:
                        p1ProcList.remove(card)
                        break

                p1_proced = ""
                for card in p1ProcList:
                    if p1_proced == "":
                        p1_proced = card
                    else:
                        p1_proced = p1_proced + "," + card

            # Turn deck into a list
            deckList = list(game["deck"].split(","))

            # If deck is out of cards, re-shuffle discard cards
            if len(deckList) == 0:
                outCards = list(player1_hand.split(",")) + list(player2_hand.split(","))
                deckList = reshuffleDeck(game, outCards)

            # Randomly select a card to draw
            drawn = deckList.pop(random.randint(0, len(deckList) - 1))

            # Update player hand
            p1HandList = list(player1_hand.split(","))
            p1HandList.append(drawn)
            p1HandList.remove(discard)

            player1_hand = ""
            for card in p1HandList:
                if player1_hand == "":
                    player1_hand = card
                else:
                    player1_hand = player1_hand + "," + card

            # Reconstruct deck
            deck = ""
            for card in deckList:
                if deck == "":
                    deck = card
                else:
                    deck = deck + "," + card

            db.execute(
                f"UPDATE games SET player1_hand = ?, player1_card = ?, player1_protected = ?, player_turn = ?, deck = ? WHERE game_id = {game_id}", player1_hand, action, p1_proced, game["player2_id"], deck)
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
            emitGame("card", game, users)

        # Alderaan
        elif action == "alderaan":
            db.execute(f"UPDATE games SET player1_card = ?, player_turn = ? WHERE game_id = {game_id}", action, game["player2_id"])
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
            emitGame("card", game, users)

    # Player 2
    elif player == "player2" and game["player_turn"] == game["player2_id"]:

        # Stand
        if action == "stand":
            db.execute(
                f"UPDATE games SET player2_card = ?, phase = ?, player_turn = ? WHERE game_id = {game_id}", action, "shift", game["player1_id"])
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        # Draw
        elif action == "draw":

            # Turn deck into a list
            deckList = list(game["deck"].split(","))

            # If deck is out of cards, re-shuffle discard cards
            if len(deckList) == 0:
                outCards = list(player1_hand.split(",")) + list(player2_hand.split(","))
                deckList = reshuffleDeck(game, outCards)

            # Add a card to player 2's hand
            drawn = deckList.pop(random.randint(0, len(deckList) - 1))
            if player2_hand == "":
                player2_hand = drawn
            else:
                player2_hand = player2_hand + "," + drawn

            # Reconstruct deck
            deck = ""
            for card in deckList:
                if deck == "":
                    deck = card
                else:
                    deck = deck + "," + card

            db.execute(
                f"UPDATE games SET player2_hand = ?, phase = ?, player2_card = ?, player_turn = ?, deck = ? WHERE game_id = {game_id}", player2_hand, "shift", action, game["player1_id"], deck)
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        # Trade
        elif action == "trade":
            discard = data["card"]  # If there's gonna be a KeyError, get it done early

            # Update shift protected cards
            p2_proced = game["player2_protected"]
            p2ProcList = []
            if p2_proced != None:
                p2ProcList = list(p2_proced.split(","))
                for card in p2ProcList:
                    if card == discard:
                        p2ProcList.remove(card)
                        break

                p2_proced = ""
                for card in p2ProcList:
                    if p2_proced == "":
                        p2_proced = card
                    else:
                        p2_proced = p2_proced + "," + card

            # Turn deck into a list
            deckList = list(game["deck"].split(","))

            # If deck is out of cards, re-shuffle discard cards
            if len(deckList) == 0:
                outCards = list(game["player1_hand"].split(",")) + list(game["player2_hand"].split(","))
                deckList = reshuffleDeck(game, outCards)

            # Randomly select a card to draw
            drawn = deckList.pop(random.randint(0, len(deckList) - 1))

            # Update player hand
            p2HandList = list(player2_hand.split(","))
            player2_hand = ""
            p2HandList.append(drawn)
            p2HandList.remove(discard)

            for card in p2HandList:
                if player2_hand == "":
                    player2_hand = card
                else:
                    player2_hand = player2_hand + "," + card

            # Reconstruct deck
            deck = ""
            for card in deckList:
                if deck == "":
                    deck = card
                else:
                    deck = deck + "," + card

            db.execute(
                f"UPDATE games SET player2_hand = ?, phase = ?, player2_card = ?, player2_protected = ?, player_turn = ?, deck = ? WHERE game_id = {game_id}", player2_hand, "shift", action, p2_proced, game["player1_id"], deck)
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        # Alderaan
        elif action == "alderaan":

            # Find which player wins
            winner = getWinner(game)

            # Find which players bomb out
            p1BombOut = 0
            p2BombOut = 0
            p1Abs = abs(int(calcHandVal(game["player1_hand"])))
            p2Abs = abs(int(calcHandVal(game["player2_hand"])))

            if p1Abs > 23 or p1Abs == 0:
                p1BombOut = 0.1
            if p2Abs > 23 or p2Abs == 0:
                p2BombOut = 0.1
            sabGain = 0
            if p1BombOut == 0.1 and p2BombOut == 0.1:
                sabGain = 0.2
                p1BombOut = 0
                p2BombOut = 0

            # Calculate the winnings of players and deductions from pots
            p1Gain = 0
            p2Gain = 0
            handPotLoss = 0
            sabPotLoss = 0
            sabBomb = 0
            if winner == -1:
                sabBomb = 0.2
            elif winner == game["player1_id"]:
                p1Gain += game["hand_pot"]
                handPotLoss = game["hand_pot"]
                if abs(int(calcHandVal(game["player1_hand"]))) == 23:
                    p1Gain += game["sabacc_pot"]
                    sabPotLoss = game["sabacc_pot"]
            elif winner == game["player2_id"]:
                p2Gain += game["hand_pot"]
                handPotLoss = game["hand_pot"]
                if abs(int(calcHandVal(game["player2_hand"]))) == 23:
                    p2Gain += game["sabacc_pot"]
                    sabPotLoss = game["sabacc_pot"]

            db.execute(f"UPDATE games SET player1_credits = ?, player2_credits = ?, hand_pot = ?, sabacc_pot = ?, phase = ?, player2_card = ?, player_turn = ?, completed = ?, winner = ? WHERE game_id = {game_id}", game["player1_credits"] - round((game["hand_pot"] * p1BombOut)) + p1Gain - round((game["hand_pot"] * sabBomb * 0.5)), game["player2_credits"] - round(
                (game["hand_pot"] * p2BombOut)) + p2Gain - round((game["hand_pot"] * sabBomb * 0.5)), game["hand_pot"] + round(game["hand_pot"] * p1BombOut) + round(game["hand_pot"] * p2BombOut) - handPotLoss, game["sabacc_pot"] + round((game["hand_pot"] * sabGain)) - sabPotLoss, "completed", action, -1, 1, winner)
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        if game["player1_card"] == "alderaan":

            # Find which player wins
            winner = getWinner(game)

            # Find which players bomb out
            p1BombOut = 0
            p2BombOut = 0
            p1Abs = abs(int(calcHandVal(game["player1_hand"])))
            p2Abs = abs(int(calcHandVal(game["player2_hand"])))

            if p1Abs > 23 or p1Abs == 0:
                p1BombOut = 0.1
            if p2Abs > 23 or p2Abs == 0:
                p2BombOut = 0.1
            sabGain = 0
            if p1BombOut == 0.1 and p2BombOut == 0.1:
                sabGain = 0.2
                p1BombOut = 0
                p2BombOut = 0

            # Calculate the winnings of players and deductions from pots
            p1Gain = 0
            p2Gain = 0
            handPotLoss = 0
            sabPotLoss = 0
            sabBomb = 0
            if winner == -1:
                sabBomb = 0.2
            elif winner == game["player1_id"]:
                p1Gain += game["hand_pot"]
                handPotLoss = game["hand_pot"]
                if abs(int(calcHandVal(game["player1_hand"]))) == 23:
                    p1Gain += game["sabacc_pot"]
                    sabPotLoss = game["sabacc_pot"]
            elif winner == game["player2_id"]:
                p2Gain += game["hand_pot"]
                handPotLoss = game["hand_pot"]
                if abs(int(calcHandVal(game["player2_hand"]))) == 23:
                    p2Gain += game["sabacc_pot"]
                    sabPotLoss = game["sabacc_pot"]

            db.execute(f"UPDATE games SET player1_credits = ?, player2_credits = ?, hand_pot = ?, sabacc_pot = ?, phase = ?, player2_card = ?, player_turn = ?, completed = ?, winner = ? WHERE game_id = {game_id}", game["player1_credits"] - round((game["hand_pot"] * p1BombOut)) + p1Gain - round((game["hand_pot"] * sabBomb * 0.5)), game["player2_credits"] - round(
                (game["hand_pot"] * p2BombOut)) + p2Gain - round((game["hand_pot"] * sabBomb * 0.5)), game["hand_pot"] + round(game["hand_pot"] * p1BombOut) + round(game["hand_pot"] * p2BombOut) - handPotLoss, game["sabacc_pot"] + round((game["hand_pot"] * sabGain)) - sabPotLoss, "completed", action, -1, 1, winner)
            game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        db.execute(f"UPDATE games SET player1_card = ?, player2_card = ? WHERE game_id = {game_id}", None, None)
        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame("card", game, users)

    return


@socketio.on("shift", namespace="/shift")
def shift(data):
    """Recieve shift message"""

    # Set some variables for the whole function
    game_id = data["game_id"]
    action = data["action"]
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    user_id = session.get("user_id")

    # Find player phrases
    player = ""
    opponent = ""
    if user_id == game["player1_id"]:
        player = "player1"
        opponent = "player2"
    elif user_id == game["player2_id"]:
        player = "player2"
        opponent = "player1"
    else:
        return

    if game["phase"] != "shift":
        return

    if action != "shift":
        return

    # Player 1 shift
    if user_id == game["player1_id"]:
        revealed = ""
        for card in data["cards"]:
            if revealed == "":
                revealed = card
            else:
                revealed = revealed + "," + card

        db.execute(
            f"UPDATE games SET player_turn = ?, player1_protected = ? WHERE game_id = {game_id}", game["player2_id"], revealed)

    # Player 2 shift
    elif user_id == game["player2_id"]:
        # Update shifted cards
        revealed = ""
        for card in data["cards"]:
            if revealed == "":
                revealed = card
            else:
                revealed = revealed + "," + card

        # Immidiatly update variables and the database since this information will be used shortly
        db.execute(f"UPDATE games SET player2_protected = ? WHERE game_id = {game_id}", revealed)
        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        # Roll shift dice
        rollsList = [random.randint(1, 6), random.randint(1, 6)]

        # Set some variables for modification
        deck = ""
        deckList = game["deck"].split(",")
        player1_hand = game["player1_hand"]
        player2_hand = game["player2_hand"]

        # If the Sabacc shift strikes (i.e. dice rolls doubles)
        if rollsList[0] == rollsList[1]:
            player1_hand = ""
            player2_hand = ""

            # Go through the loop twice, once for each player
            for p in ["1", "2"]:

                # How many cards need to be drawn
                drawCnt = len(game["player" + p + "_hand"].split(",")) - len(game["player" + p + "_protected"].split(","))

                # If the player has no protected cards
                if game["player" + p + "_protected"].split(",") == [""]:
                    drawCnt += 1

                # If there are not enough cards left in the deck, shuffle the discard cards into it
                if len(deckList) < drawCnt:
                    deckList = reshuffleDeck(game, game["player1_protected"].split(",") + game["player2_protected"].split(","))

                # Draw the corresponding amount of cards
                for i in range(drawCnt):
                    if p == "1":
                        if player1_hand == "":
                            player1_hand = deckList.pop(random.randint(0, len(deckList) - 1))
                        else:
                            player1_hand = player1_hand + "," + deckList.pop(random.randint(0, len(deckList) - 1))
                    elif p == "2":
                        if player2_hand == "":
                            player2_hand = deckList.pop(random.randint(0, len(deckList) - 1))
                        else:
                            player2_hand = player2_hand + "," + deckList.pop(random.randint(0, len(deckList) - 1))

                # If the player has protected cards, add them once more to the player's hand
                if game["player" + p + "_protected"].split(",") != [""]:
                    for card in game["player" + p + "_protected"].split(","):
                        if p == "1":
                            player1_hand = player1_hand + "," + card
                        elif p == "2":
                            player2_hand = player2_hand + "," + card

        # Reconstruct deck
        for card in deckList:
            if deck == "":
                deck = card
            else:
                deck = deck + "," + card

        # "Stringify" the dice rolls
        rolls = str(rollsList[0]) + "," + str(rollsList[1])

        db.execute(
            f"UPDATE games SET player1_hand = ?, player2_hand = ?, deck = ?, phase = ?, player_turn = ?, dice_rolls = ? WHERE game_id = {game_id}", player1_hand, player2_hand, deck, "betting", game["player1_id"], rolls)

    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    emitGame("shift", game, users)

    return


@app.route("/game/<game_id>", methods=["GET", "POST"])
@login_required
def game(game_id):
    """Play Sabacc!"""

    # Set some basic variables
    user_id = session.get("user_id")
    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}")[0]
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    player = ""
    opponent = {}

    # Get player phrases
    if user["id"] == game["player1_id"]:
        player = "player1"
        opponent["player"] = "player2"
    elif user_id == game["player2_id"]:
        player = "player2"
        opponent["player"] = "player1"

    # If this is not the user's game, show them an apology page
    else:
        return apology("This is not one of your games")

    if request.method == "GET":

        # Give Jinja2 some variables
        usernames = {}
        for name in db.execute("SELECT * FROM users"):
            usernames[name["id"]] = name["username"]

        opponent["username"] = db.execute("SELECT username FROM users WHERE id = ?",
                                          game[opponent["player"] + "_id"])[0]["username"]
        opponent["cards"] = len(list(game[opponent["player"] + "_hand"].split(",")))
        opponent["credits"] = game[opponent["player"] + "_credits"]

        pHandLen = len(game[player + "_hand"].split(","))

        return render_template("game.html", game=game, player=player, opponent=opponent, username=user["username"], pHandLen=pHandLen, usernames=usernames)

    # If game is over and a player continues it
    elif request.method == "POST":
        # If game is not over (because someone has already continued it or it never ended), redirect player to the current game page
        if game["completed"] != 1:
            return redirect(f"/game/{game['game_id']}")

        # Construct deck and deal cards
        deckData = constructDeck()
        deck = deckData["deck"]
        player1_hand = deckData["player1_hand"]
        player2_hand = deckData["player2_hand"]

        db.execute(f"UPDATE games SET player1_id = ?, player2_id = ?, player1_credits = ?, player2_credits = ?, hand_pot = ?, sabacc_pot = ?, deck = ?, player1_hand = ?, player2_hand = ?, player_turn = ?, phase = ?, completed = ?, player1_card = ?, player2_card = ?, winner = ?, player1_protected = ?, player2_protected = ?, dice_rolls = ? WHERE game_id = {game_id}", game[
                   "player2_id"], game["player1_id"], game["player2_credits"] - 15, game["player1_credits"] - 15, game["hand_pot"] + 10, game["sabacc_pot"] + 20, deck, player1_hand, player2_hand, game["player2_id"], "betting", 0, None, None, None, "", "", None)
        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        # Redirect player to game page
        return redirect(f"/game/{game['game_id']}")


@app.route("/completed")
@login_required
def completed():
    """Display completed games"""

    # Get the user's id for later use
    user_id = session.get("user_id")

    # Get Jinja2 some variables
    usernames = {}
    games = db.execute(
        f"SELECT * FROM games WHERE (player1_id = ? OR player2_id = ?) AND completed = 1 ORDER BY game_id DESC", user_id, user_id)
    users = db.execute("SELECT * FROM users")
    for user in users:
        usernames[user["id"]] = user["username"]

    # Render the home page with the user's completed game data
    return render_template("completed.html", games=games, usernames=usernames)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 403)

        # Ensure password is valid
        if not request.form.get("password"):
            return apology("must provide password", 403)

        orHash = db.execute(f"SELECT * FROM users WHERE username = ?", username)[0]["hash"]
        if check_password_hash(orHash, request.form.get("password")) == False:
            return apology("invalid password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check that username is valid
        if len(rows) == 0:
            return apology("Invalid username")

        # If the user wants to change their password, do so
        change = request.form.get("change")
        if change != None:

            # Check that passwords are valid
            password = request.form.get("pass")
            if not password:
                return apology("Missing new password")

            passCon = request.form.get("passCon")
            if not passCon:
                return apology("Missing new password confirmation")

            if password != passCon:
                return apology("New passwords do not match")

            # Change user's password
            passHash = str(generate_password_hash(password))
            db.execute(f"UPDATE users SET hash = ? WHERE username = ?", passHash, username)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Check that username is inputted
        username = request.form.get("username")
        if not username:
            return apology("Missing username", 400)

        # Check passwords are there and match
        password = request.form.get("password")

        if not password:
            return apology("Missing password", 400)

        confirmation = request.form.get("confirmation")

        if not confirmation:
            return apology("Missing confirmation password", 400)

        if confirmation != password:
            return apology("Confirmation and password do not match")

        # Make sure that username is not a duplicate of an old one
        usernames = db.execute("SELECT username FROM users")
        duplicate = False
        for u in usernames:
            if username == u["username"]:
                duplicate = True
                return apology("Someone else already took that username", 400)

        # Complete registration
        username = request.form.get("username")
        password = request.form.get("password")
        passHash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, str(passHash))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    elif request.method == "GET":
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

""" For development only """
if __name__ == "__main__":
    app.run(host=config["IP"], port=config["PORT"], debug=config["DEBUG"])