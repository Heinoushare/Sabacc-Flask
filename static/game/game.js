$(document).ready(function() {

	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var game_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/game');

	game_socket.on('connect', function() {
		game_socket.emit("game");
	});

	// Reduce website hackability by defining variables pulled from the HTML as soon as possible
	var game = document.getElementById("game");
	var player = document.getElementById("player");
	var opponent = document.getElementById("opponent");

	// Create variables off of attributes of "meta" variables
	var completed = parseInt(game.getAttribute("completed"));
	var winner = parseInt()

	let playerID = parseInt(player.getAttribute("player_id"));
	var username = plyaer.getAttribute("username");

	let opponent_id = parseInt(opponent.getAttribute("opponent_id"));
	let opponent_username = opponent.getAttribute("username");

});