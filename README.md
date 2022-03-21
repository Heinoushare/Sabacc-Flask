# Sabacc
## Video Demo: \<URL HERE\>
## Description:
Sabacc, the space card game. A fast-paced, high-risk, perfect mixture of skill and luck. Engage in this perfect mixture of deception, quick calculation, and strategy, at \<INSERT WEBSITE URL\>

## Files
### application.py
application.py is the file that runs this show. It handles all user requests, Socket.IO messages, and the modification of sabacc.db.

application.py uses the following libraries and tools
#### CS50 Library
The CS50 library is used to add, update, and read data from the sqlite3 database sabacc.db. It's safety features are used to ensure that no malicious user input can damage the database.

#### Flask
The entire web application is based off of Flask. application.py uses the Flask library to handle HTTP GET and POST requests, rendering HTML files and passing data to Jinja2. Flask can also display several different HTML files per page, depending on the circumstances. application.py also uses Flask-Session and Flask-SocketIO, for saving user sessions and receiving and sending Socket.IO messages.

Each part of the web application that uses Socket.IO has it's own Socket *namespace*. A *namespace* is used to tell what a message is for, sort of like the filetype at the end of a file name (.py, .png, .jpeg, etc.). Each *namespace* has a corresponding function. application.py uses a total of five seperate *namespaces*, one for the **Global Chat**, and four for a Sabacc game, with varying functions for card phases and keeping track of players.

#### Werkzeug
Werkzeug is used for generating and checking password hashes for users, making it difficult for even the application developers to access users' passwords. Werkzeug will also display apologies to users when there are internal server errors.

#### helpers.py
application.py uses helpers.py for repetitive functions and the decorated function @login_required. If @login_required is writted at the top of a page function, the website will automatically redirect the user to the login page if they are not logged in.

### helpers.py
helpers.py is a file full of custom functions used by application.py. These functions vary from emitting Socket.IO messages, shuffling the Sabacc deck, and redirecting logged out users to the login page.

When emitting game data to players, helpers.py uses Socket.IO *rooms*. Each client using Socket.IO has their own *room*. When emitting game data, helpers.py will send the message to both players, using their corresponding *rooms*. How does helpers.py know what *room* to send game data to? When a Socket.IO client connects to the server, the client is given a *Socket ID*. The server saves their *Socket ID* into a Python *dictionary*, with the key as the *User ID* (the *User ID* is stored in the sqlite3 database and is **not** the same as the *Socket ID*), and the value as the *Socket ID*. When application.py calls the *emitGame* function in helpers.py, is passes the function the game data and the users dictionary. The game data stores both players' *User IDs*, which can be used to find their *Socket IDs*.

### requirements.txt
requiremenets.txt is a very simple file, with no actual functionality in the web application. The use of requirements.txt is to keep track of what libraries and tools the web application uses, in case one day you need to re-install said tools. An important use of requirements.txt is to keep track of what *version* of the tool is required for the web application. Without this, the risk of using incompatible library versions or deprecated methods is high. One example of this is shown with Flask-SocketIO, python-socketio, and python-engineio, the latest versions of these libraries (as of March 2022) are **incompatible**. I had to look up which specfic versions worked and noted them down in requirements.txt for later use.

### sabacc.db
sabacc.db is an sqlite3 database which stores all of the web application data. It has two tables, *users* and *games*. The table *users* stores information about every user, with a row for each user. It stores their *username*, *User ID*, and *password hash* which application.py uses to check if a user-inputted password is correct.

### layout.html
layout.html is the base template for all other HTML files. It contains information for CSS and Bootstrap stylesheets to be used, and HTML for the website navigation bar, title, site icon. It uses Jinja2, a tool to make dynamic HTML, for blocks of code in which other HTML from other files will go, and to display different navigation bars depending on whether a user is signed in or not.

### index.html
index.html *extends* layout.html, using Jinja2 to *extend* it and fill in Jinja2 HTML *blocks*. index.html uses Jinja2 to check whether a user is signed in or not. If they are, a table of the user's active games will be displayed, with data being passed from application.py, otherwise, a video and rulebook on how to play Sabacc will be displayed.

### index.js
index.js contains code which uses JQuery to copy game links to a user's clipboard on the click of a button.

### register.html
register.html contains an account creation form, which sends a POST request to the server containing registration details. application.py confirms that the details are valid, with a username that doesn't already exist in the database, and matching password and confirmation passwords.

### login.html
login.html contains and login form, which sends a POST request the server with login details. Using login.js, users can also change their password on login.html. application.py will verify user input and login and save the user's session if the user input is valid.

### login.js
login.js contains some plain JavaScript to reveal password changing inputs on login.html.

### apology.html
apology.html simply renders a image of a cat with error text on it. Using external sources and Jinja2, apology.html will generate said image. apology.html is rendered whenever there is an internal server error or invalid user input.

### completed.html
completed.html displays a user's completed games, using data passed from application.py with Jinja2.

### completed.js
completed.js contains code which uses JQuery to copy game links to a user's clipboard on the click of a button.

### chat.html
chat.html (*extends* layout.html) is used to render the application global chat, using chat.js to send and render messages to others on the chat page.

### chat.js
chat.js uses Socket.IO to interchange messages with the server. When the client recieves a message from a user connecting or sending a text message, chat.js will use JQuery to display the message, along with the sender's username in front of the message.

### host.html
host.html contains a form which prompts users to enter another user's username to play a game with them. host.html will send a POST request to the server and application.py will verify that the username inputted does exist, and then insert the game in sabacc.db.

### game.html
game.html is by far the longest HTML file made for this web application, but very little of it is actually displayed to users. Most of the HTML in game.html is in a Jinja2 if statement, eliminating a large part of the HTML. game.html contains all the HTML needed to play a game of Sabacc. game.html contains made-up HTML tags to store game and user data. game.html relies on four JavaScript files to play a game of Sabacc, game.js, bet.js, card.js, and shift.js

### game.js
