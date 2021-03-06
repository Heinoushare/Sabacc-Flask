$(document).ready(function() {

    // Define Sockets
	let domain = document.getElementById("domain").getAttribute("value");
	let socket = io.connect(domain);
	let card_socket = io(domain + "/card");

    // Reduce website hackability by defining variables pulled from the HTML as soon as possible
	let game = document.getElementById("game");
	let player = document.getElementById("player");
	let opponent = document.getElementById("opponent");

	// Create variables off of attributes of "meta" variables
	let game_id = parseInt(game.getAttribute("game_id"));
	let phase = game.getAttribute("phase");
	let player_turn = parseInt(game.getAttribute("player_turn"));
	let player1_card = game.getAttribute("player1_card");
	let player2_card = game.getAttribute("player2_card");

	let playerID = parseInt(player.getAttribute("player_id"));
	let player_phrase = player.getAttribute("player");

	var hand = game.getAttribute(player_phrase + "_hand").split(",");

	let opponent_id = parseInt(opponent.getAttribute("opponent_id"));
	let opponent_username = opponent.getAttribute("username");
	var opponent_phrase = opponent.getAttribute("player");

	// Define show/hide functions
	function show(id) {
		document.getElementById(id).hidden = false;
	}

	function hide(id) {
		document.getElementById(id).hidden = true;
	}

	// Figure out which HTML needs to be shown
	if (phase === "card") {
		if (player_phrase === "player1") {
			hide("p2Card");
			if (player1_card != "None" && player1_card != "null") {
				hide("p1Card");
			} else {
				hide("p1TradeDiv");
			}
		} else if (player_phrase === "player2") {
			hide("p1Card");
			if (player1_card != "None" && player1_card != "null" && (player2_card === "None" || player2_card === "null")) {
				let p1Txt = document.getElementById("p1CardActionTxt");
				if (game.getAttribute("player1_card") === "draw") {
					p1Txt.innerHTML = "drew.";
				} else if (game.getAttribute("player1_card") === "trade") {
					p1Txt.innerHTML = "traded.";
				} else if (game.getAttribute("player1_card") === "stand") {
					p1Txt.innerHTML = "stood (skipped).";
				} else if (game.getAttribute("player1_card") === "alderaan") {
					p1Txt.innerHTML = "called Alderaan, this is your last turn!";
				}
				hide("p2TradeDiv");
			} else {
				hide("p2CardActionDiv");
				hide("p2TradeDiv");
			}
		}
	} else {
		// If not card phase
		hide("cardPhase");
		throw "";
	}

	// Recieving message through card_socket
	card_socket.on("card", function(data) {

		// This isn't the game you're looking for
		if (data["game_id"] != game_id) {
			return;
		}

		// Update game HTML tag
		for (pair in data) {
			if (data[pair] === null) {
				game.setAttribute(pair.toString(), data[pair]);
			} else {
				game.setAttribute(pair.toString(), data[pair].toString());
			}
		}

		// Update globabl variables
		game = document.getElementById("game");
		game_id = parseInt(game.getAttribute("game_id"));
		phase = game.getAttribute("phase");
		player_turn = parseInt(game.getAttribute("player_turn"));

		if (phase != "card") {
			location.reload();
		}

		// Update HTML
		document.getElementById("hand").innerHTML = data[player_phrase + "_hand"];
		let opCards = data[opponent_phrase + "_hand"].split(",");
		document.getElementById("opponent_cards").innerHTML = opCards.length;
		document.getElementById("procCards").innerHTML = data[player_phrase + "_protected"];
		document.getElementById("opponent_proc").innerHTML = data[opponent_phrase + "_protected"];

		// If user is player 2 and it's their  turn
		if (playerID === data["player2_id"] && playerID === data["player_turn"]) {
			let p1Txt = document.getElementById("p1CardActionTxt");
			if (data["player1_card"] === "draw") {
				p1Txt.innerHTML = "drew.";
			} else if (data["player1_card"] === "trade") {
				p1Txt.innerHTML = "traded.";
			} else if (data["player1_card"] === "stand") {
				p1Txt.innerHTML = "stood (skipped).";
			} else if (data["player1_card"] === "alderaan") {
				p1Txt.innerHTML = "called Alderaan, this is your last turn!";
			}
			show("p2CardActionDiv");
		}

		return;

	});

	// P1 card action
	$("#p1CardActionBtn").on("click", function() {
		let form = document.getElementById("p1CardAction").value;

		// Find out what action P1 is taking and act accordingly
		if (form === "stand") {
			let data = { "game_id": game_id, "action": "stand" };
			card_socket.emit("card", data);
		} else if (form === "draw") {
			let data = { "game_id": game_id, "action": "draw" };
			card_socket.emit("card", data);
		} else if (form === "trade") {
			for (card in hand) {
				$("#p1Trade").append('<option value=\"' + hand[card] + '\">' + hand[card] + '</option>');
			}
			show("p1TradeDiv");
		} else if (form === "alderaan") {
			let data = { "game_id": game_id, "action": "alderaan" };
			card_socket.emit("card", data);
		} else {
			document.getElementById("p1InvalidCardAction").innerHTML =
		  "Invalid action, please Draw, Trade, Stand, or call Alderaan";
		}
		hide("p1CardActionDiv");
	});

	// P1 Trade
	$("#p1TradeBtn").on("click", function() {

		// Confirm that card being traded is in hand
		let card = document.getElementById("p1Trade").value;
		let cardIn = false;
		for (c in hand) {
			if (card === hand[c]) {
				cardIn = true;
				break;
			}
		}
		if (cardIn === false) {
			document.getElementById("p1InvalidTrade").innerHTML = "Invalid selection.";
			return;
		}

		hide("p1TradeDiv");
		let data = { "game_id": game_id, "action": "trade", "card": card };
		card_socket.emit("card", data);
		return;
	});

	// P2 card action
	$("#p2CardActionBtn").on("click", function() {

		// Find out what action P1 is taking and act accordingly
		let form = document.getElementById("p2CardAction").value;
		if (form === "stand") {
			let data = { "game_id": game_id, "action": "stand" };
			card_socket.emit("card", data);
		} else if (form === "draw") {
			let data = { "game_id": game_id, "action": "draw" };
			card_socket.emit("card", data);
		} else if (form === "trade") {
			for (card in hand) {
				$("#p2Trade").append('<option value=\"' + hand[card] + '\">' + hand[card] + '</option>');
			}
			show("p2TradeDiv");
		} else if (form === "alderaan") {
			let data = { "game_id": game_id, "action": "alderaan" };
			card_socket.emit("card", data);
		} else {
			document.getElementById("p2InvalidCardAction").innerHTML =
		  "Invalid action, please Draw, Trade, Stand, or call Alderaan";
		}
		hide("p2CardActionDiv");
	});

	// P2 trade
	$("#p2TradeBtn").on("click", function() {

		// Confirm that card being traded is in hand
		let card = document.getElementById("p2Trade").value;
		let cardIn = false;
		for (c in hand) {
			if (card === hand[c]) {
				cardIn = true;
				break;
			}
		}
		if (cardIn === false) {
			document.getElementById("p2InvalidTrade").innerHTML = "Invalid selection.";
			return;
		}

		hide("p2TradeDiv");
		let data = { "game_id": game_id, "action": "trade", "card": card };
		card_socket.emit("card", data);
		return;
	});

});