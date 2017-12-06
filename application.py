from flask import Flask, flash, redirect, render_template, request, session, g
from flask_socketio import SocketIO, send, emit
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from helpers import apology, login_required, get_db, make_dicts, query_db, insert, get_user
import datetime
from dateutil import parser
       
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# A class to track all connected users.  Everytime a user switches to another
# page, the table of active users will be updated, because a user will
# disconnect and reconnect on a page switch.  If we to write a single-page
# application, we could avoid these reconnect/disconnects. A user might be
# logged in several times (e.g., on different machines), so we maintain a list
# of connections per user.
class ActiveUsers():

    def __init__(self):
       self.active_users = {}

    def add_user(self, name, sid):
        print "add_user", name, sid
        if not self.active_users.has_key(name):
            self.active_users[name] = []
        self.active_users[name].append(request.sid)

    def del_user(self, name, sid):
        print "del_user", name, sid
        if self.active_users.has_key(name):
            self.active_users[name].remove(sid)
        print self.active_users

    def is_connected(self, name):
        return name in self.active_users

    def get_sids(self, name):
        return self.active_users[name]

active_users = ActiveUsers()
socketio = SocketIO(app)
Session(app)

if __name__ == '__main__':
    socketio.run(app)

# filter to print timestap for messages in templates
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%H:%M'
    return native.strftime(format) 


# Handlers for sockio events. Since anyone can setup a socketio to the server,
# we need check if user is logged in, but we are happy to take disconnects.
@socketio.on("connected")
def connected(json):
	'''Adds user to active user once a user connects.'''
        print("user wants to join", json["data"], request.sid)
        if session.has_key("user_id"):
            active_users.add_user(json["data"], request.sid)

@socketio.on("disconnect")
def disconnect():
	'''Remove user from active users when they disconnect.'''
        if session.has_key("user_id"):
            user = get_user(session["user_id"])
            active_users.del_user(user, request.sid)

@socketio.on('client')
def new_mesage(json):
	'''Handles when a user sends a new message.'''

        if not session.has_key("user_id"):
            return
                    
	# Add message to the database
	json["stamp"] = str(datetime.datetime.now())
	result = insert("messages", ("username", "buddy", "text", "stamp"), (json["username"], json["buddy"], json["message"], json["stamp"]))

	# Alert if the user is no online
	json["alert"] = ""

	# If private and the person the user wishes to chat with is online
	if json["buddy"] != "":
            if active_users.is_connected(json["buddy"]):

		# Lookup connections on which users is connected
		sids = active_users.get_sids(json["buddy"])

		# Emit to user wishing to chat on each connection.  Flask sets up
                # a room for each connection.
                for sid in sids:
                    print "emit to", sid
		    emit("server", json, room=sid)

		# Emit back to user
		emit("server", json)

	    # Otherwise, whoever user wants to chat with is not online
	    else:
		# Add alert to json
		json["alert"] = "buddy not online"
                
		# Emit back to user
		emit("server", json)
                
	# Public chat
	else:
	    # Broadcast on all connections
	    emit("server", json, broadcast=True)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
@login_required
def index():
	user = get_user(session["user_id"])
   	return render_template("index.html", user=user, my_prof=True)

@app.route("/profile/<user_id>")
@login_required
def profile(user_id):
	view_user = query_db("SELECT * FROM users WHERE id=?", [user_id], one=True)
	user = session["user_id"]
   	return render_template("index.html", user=user, view_user=view_user, my_prof=False)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = query_db("SELECT * FROM users WHERE username = ?",
                          [request.form.get("username")], one=True)

        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
   
        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", user='')


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/about", methods=["GET"])
def about():
    """Redirect to about page"""
    return render_template("about.html", user='')

@app.route("/users", methods=["GET"])
@login_required
def users():
    """Redirect to about page"""
    users = query_db("SELECT * FROM users")
    user_id = session["user_id"]
    user = get_user(session["user_id"])
    # Redirect user to about page
    return render_template("users.html", users=users, curr_user=user_id, user=user)

@app.route("/chat", methods=["GET"])
@login_required
def chat():
    """Redirect to chat page"""
    cur_user = get_user(session["user_id"])
    messages = query_db("SELECT * FROM messages WHERE buddy=?", [""])[-10:]
    return render_template("chat.html", user=cur_user, dest="", messages=messages)

@app.route("/private/<username>", methods=["GET"])
@login_required
def private(username):
    """Redirect to chat page"""
    cur_user = get_user(session["user_id"])
    user = query_db("SELECT * FROM users WHERE id=?", [session["user_id"]], one=True)
    print("Private user: ", user)
    messages = query_db("SELECT * FROM messages WHERE (username=? AND buddy=?) OR (username=? AND buddy=?) ORDER BY stamp DESC LIMIT 10",
    					[user["username"], username, username, user["username"]])
    print("Messages", messages)
    return render_template("chat.html", user=cur_user, dest=username, messages=reversed(messages))

@app.route("/discussions", methods=["GET"])
@login_required
def discussions():
    """Redirect to about page"""
    user = get_user(session["user_id"])
    # Redirect user to about page
    return render_template("discussions.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match")

        # Generate password hash
        hash = generate_password_hash(request.form.get("password"))

        # Add user into users table
        result = insert("users", ("username", "hash"), (request.form.get("username"), hash))

        print(result)

        # Handle case if username already exists
        if not result:
            return apology("username already exists")

        # Set the user's id
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html", user='')

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
