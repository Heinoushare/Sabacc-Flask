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
	let player1_card = game.getAttribute("player1_card");
	let player2_card = game.getAttribute("player2_card");

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

    }
    else
    {
        hide("shiftPhase");
        throw "";
    }

});