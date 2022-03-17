$(document).ready(function() {

	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var shift_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/shift');

    // Reduce website hackability by defining variables pulled from the HTML as soon as possible
	let game = document.getElementById("game");
	let player = document.getElementById("player");
	let opponent = document.getElementById("opponent");

	// Create variables off of attributes of "meta" variables
	let game_id = parseInt(game.getAttribute("game_id"));
	let phase = game.getAttribute("phase");
	let player_turn = parseInt(game.getAttribute("player_turn"));
	let player1_hand = game.getAttribute("player1_hand").split(",");
	let player2_hand = game.getAttribute("player2_hand").split(",");
	let player1_protected = game.getAttribute("player1_protected");
	let player2_protected = game.getAttribute("player2_protected");

	let playerID = parseInt(player.getAttribute("player_id"));
	let player_phrase = player.getAttribute("player");

	var hand = game.getAttribute(player_phrase + "_hand").split(",");

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

    if (phase === "shift")
    {
		if (playerID != player_turn)
		{
			hide("shiftPhase");
		}
    }
    else
    {
        hide("shiftPhase");
        throw "";
    }

	let proced = game.getAttribute(player_phrase + "_protected").split(",");
	let pHand = game.getAttribute(player_phrase + "_hand").split(",");
	for (card in pHand)
	{
		console.log(pHand[card]);
		let check = false;
		for (c in proced)
		{
			if (proced[c] == pHand[card])
			{
				check = true;
				proced.splice(c, 1);
				break;
			}
		}
		$("#shiftable").append('<input type="checkbox" id="' + card.toString + '" name="' + pHand[card] + '" value="' + pHand[card] + '>' + pHand[card] + '</input>');
		$("#shiftable").append('<label for="' + card.toString + '"> ' + pHand[card] + '</label><br>');
		// document.getElementById(card.toString()).checked = check;
	}

	shift_socket.on("shift", function(data) {

		// If this is not the correct game, return
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

		// Update HTML
		document.getElementById("procCards").innerHTML = data[player_phrase + "_protected"];
		document.getElementById("opponent_cards").innerHTML = data[opponent_phrase + "_protected"];
		document.getElementById("lastRolls").inerHTML = data["dice_rolls"];

		if (playerID === player_turn)
		{
			show("shiftPhase");
		}
		else
		{
			hide("shiftPhase");
		}

		return;

	});

	$("#shiftBtn").on("click", function() {

		if (playerID === parseInt(game.getAttribute("player1_id")))
		{
			let revealed = [];
			for (card in player1_hand)
			{
				if (document.getElementById(card).checked === true)
				{
					revealed.push(player1_hand[card]);
				}
			}
			data = {"game_id": game_id, "action": "shift", "cards": revealed};
			shift_socket.emit("shift", data);
		}

		else if (playerID === parseInt(game.getAttribute("player2_id")))
		{
			let revealed = [];
			for (card in player2_hand)
			{
				if (document.getElementById(card).checked === true)
				{
					revealed.push(player2_hand[card]);
				}
			}
			data = {"game_id": game_id, "action": "shift", "cards": revealed};
			shift_socket.emit("shift", data);
		}

		hide("shiftPhase");

	});

});