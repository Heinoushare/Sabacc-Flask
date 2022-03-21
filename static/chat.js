$(document).ready(function() {

	// Declare socket variables
	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var chat_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/chat');

	let user = document.getElementById("user");

	// Send connection message
	chat_socket.on('connect', function() {
		chat_socket.emit("message", user.getAttribute("name") + ' has connected!');
	});

	// Recieving message
	chat_socket.on('message', function(msg) {
		$("#messages").append('<p>'+msg+'</p>');
	});

	// Send text message
	$('#sendbutton').on('click', function() {
		let msg = user.getAttribute("name") + ": " + document.getElementById("myMessage").value;
		chat_socket.emit("message", msg);
		$('#myMessage').val('');
	});

});