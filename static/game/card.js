$(document).ready(function() {

    // Define Sockets
	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var card_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/card');

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

	let opponent_id = parseInt(opponent.getAttribute("opponent_id"));
	let opponent_username = opponent.getAttribute("username");
	var opponent_phrase = opponent.getAttribute("player");

	// Define show/hide functions
	function show(id)
	{
		document.getElementById(id).hidden = false;
	}

	function hide(id)
	{
		document.getElementById(id).hidden = true;
	}

	// Figure out which HTML needs to be shown
	if (phase === "card")
	{
		if (player_phrase === "player1")
		{
			if (player1_card != "None" && player1_card != "null")
			{
				hide("p1Card");
			}
			else
			{
				hide("p1TradeDiv");
			}
		}
		else if (player_phrase === "player2")
		{
			hide("p1Card");
		}
	}
	else
	{
		throw "";
	}

	card_socket.on("card", function(data) {

		if (data["game_id"] != game_id)
		{
			return;
		}

		for (pair in data)
		{
			if (data[pair] === null)
			{
				game.setAttribute(pair.toString(), data[pair]);
			}
			else
			{
				game.setAttribute(pair.toString(), data[pair].toString());
			}
		}

		game = document.getElementById("game");
		game_id = parseInt(game.getAttribute("game_id"));
		phase = game.getAttribute("phase");
		player_turn = parseInt(game.getAttribute("player_turn"));

		if (phase != "card")
		{
			location.reload();
		}

		// Update card HTML
		document.getElementById("hand").innerHTML = data[player_phrase + "_hand"];
		let opCards = data[opponent_phrase + "_hand"].split(",").length;
		document.getElementById("opponent_cards").innerHTML = opCards;

		return;

	});

	$("#p1CardActionBtn").on("click", function() {
		let form = document.getElementById("p1CardAction").value;
		if (form === "stand")
		{
			hide("p1CardActionDiv");
			let data = {"game_id": game_id, "action": "stand"};
			card_socket.emit("card", data);
		}
		else if (form === "draw")
		{
			hide("p1CardActionDiv");
			let data = {"game_id": game_id, "action": "draw"};
			card_socket.emit("card", data);
		}
		else if (form == "trade")
		{

		}
		else
		{
			document.getElementById("p1InvalidCardAction").innerHTML == "Invalid action, please Draw, Trade, Stand, or call Alderaan";
		}
	});

});