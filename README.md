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
The entire web application is based off of Flask. application.py uses the Flask library to handle HTTP GET and POST requests, rendering HTML files and passing data to Jinja2. application.py also uses Flask-Session and Flask-SocketIO, for saving user sessions and receiving and sending Socket.IO messages.

Each part of the web application that uses Socket.IO has it's own Socket *namespace*. A *namespace* is used to tell what a message is for, sort of like the filetype at the end of a file name (.py, .png, .jpeg, etc.). Each *namespace* has a corresponding function. application.py uses a total of five seperate *namespaces*, one for the **Global Chat**, and four for a Sabacc game, with varying functions for card phases and keeping track of players.

#### Werkzeug
Werkzeug is used for generating and checking password hashes for users, making it difficult for even the application developers to access users' passwords. Werkzeug will also display apologies to users when there are internal server errors.

#### helpers.py
application.py uses helpers.py for repetitive functions and the decorated function @login_required. If @login_required is writted at the top of a page function, the website will automatically redirect the user to the login page if they are not logged in.

### helpers.py
helpers.py is a file full of custom functions used by application.py. These functions vary from emitting Socket.IO messages, shuffling the Sabacc deck, and redirecting logged out users to the login page.

When emitting game data to players, helpers.py uses Socket.IO *rooms*. Each client using Socket.IO has their own *room*. When emitting game data, helpers.py will send the message to both players, using their corresponding *rooms*. How does helpers.py know what *room* to send game data to? When a Socket.IO client connects to the server, the client is given a *Socket ID*. The server saves their *Socket ID* into a Python *dictionary*, with the key as the *User ID* (the *User ID* is stored in the sqlite3 database and is **not** the same as the *Socket ID*), and the value as the *Socket ID*. When application.py calls the *emitGame* function in helpers.py, is passes the function the game data and the users dictionary. The game data stores both players' *User IDs*, which can be used to find their *Socket IDs*.

### requirements.txt
requiremenets.txt is a very simple file, with no actual functionality in the web application. The use of requirements.txt is to keep track of what libraries and tools the web application uses, in case one day you need to re-install said tools. An important use of requirements.txt is to keep track of what *version* is required for the web application. Without this, the risk of using incompatible library versions or deprecated methods is high. One example of this is shown with Flask-SocketIO, python-socketio, and python-engineio, the latest versions of these libraries (as of March 2022) are **incompatible**. I had to look up which specfic versions worked and noted them down in requirements.txt for later use.