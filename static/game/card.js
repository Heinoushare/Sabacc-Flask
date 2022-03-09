$(document).ready(function() {

    // Define Sockets
	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var game_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/card');

    // Reduce website hackability by defining variables pulled from the HTML as soon as possible
	let game = document.getElementById("game");
	let player = document.getElementById("player");
	let opponent = document.getElementById("opponent");

	// Create variables off of attributes of "meta" variables
	let game_id = parseInt(game.getAttribute("game_id"));
	let phase = game.getAttribute("phase");
	let player_turn = parseInt(game.getAttribute("player_turn"));

	let playerID = parseInt(player.getAttribute("player_id"));
	let player_phrase = player.getAttribute("player");

	let opponent_id = parseInt(opponent.getAttribute("opponent_id"));
	let opponent_username = opponent.getAttribute("username");

	if ()

});