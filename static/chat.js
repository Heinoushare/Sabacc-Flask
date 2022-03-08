$(document).ready(function() {

	var socket = io.connect('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev');
	var chat_socket = io('https://heinoushare-code50-76819177-g4x99w676fvqvg-5000.githubpreview.dev/chat');

	let user = document.getElementById("user");

	chat_socket.on('connect', function() {
		chat_socket.emit("message", user.getAttribute("name") + ' has connected!');
	});

	chat_socket.on('message', function(msg) {
		$("#messages").append('<p>'+msg+'</p>');
	});

	$('#sendbutton').on('click', function() {
		let msg = user.getAttribute("name") + ": " + document.getElementById("myMessage").value;
		chat_socket.emit("message", msg);
		$('#myMessage').val('');
	});

});