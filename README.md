# Sabacc
## Video Demo:  <URL HERE>
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

#### Werkzeug
Werkzeug is used for 

<!--
- CS50 (For the sqlite3 database)
- Flask (For handling requests to the web application)
- Flask-Session (For storing user sessions)
- Flask-SocketIO (For receiving and sending messages with Socket.IO)
- Werkzeug (For security and server error handling)
- helpers.py (A custom helper file for functions used several times)
-->