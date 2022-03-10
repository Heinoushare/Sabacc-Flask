$(document).ready(function() {

	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var game_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/game');

	game_socket.on('connect', function() {
		game_socket.emit("game");
	});

	// Reduce website hackability by defining variables pulled from the HTML as soon as possible
	let game = document.getElementById("game");

});