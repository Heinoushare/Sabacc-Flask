$(document).ready(function() {

	// Declare socket variables
	let domain = document.getElementById("domain").getAttribute("value");
	let socket = io.connect(domain);
	let chat_socket = io(domain + "/chat");

	// Attribute "user" contains information about the user
	let user = document.getElementById("user");

	// Send connection message
	chat_socket.on('connect', function() {
		chat_socket.emit("message", user.getAttribute("name") + ' has connected!');
	});

	// Recieving message
	chat_socket.on('message', function(msg) {
		$("#messages").append('<p>' + msg + '</p>');
	});

	// Send text message
	$('#sendbutton').on('click', function() {
		let msg = user.getAttribute("name") + ": " + document.getElementById("myMessage").value;
		chat_socket.emit("message", msg);
		$('#myMessage').val('');
	});

});