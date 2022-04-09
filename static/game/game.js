$(document).ready(function() {

	// Set socket variables
	let domain = document.getElementById("domain").getAttribute("value");
	let socket = io.connect(domain);
	let game_socket = io(domain + "/game");

	// Open socket connection with server
	game_socket.on('connect', function() {
		game_socket.emit("game");
	});

	game_socket.on("game", function(data) {
		location.reload();
	});

});