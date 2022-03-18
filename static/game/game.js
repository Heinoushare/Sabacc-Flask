$(document).ready(function() {

	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var game_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/game');

	game_socket.on('connect', function() {
		game_socket.emit("game");
	});

	game_socket.on("game", function(data) {
		location.reload();
	});

});