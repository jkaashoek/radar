# Impots
from flask import Flask, flash, redirect, render_template, request, session, g
from flask_socketio import SocketIO, send, emit
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from dateutil import parser
import sqlite3, datetime

from helpers import apology, login_required, get_db, make_dicts, query_db, insert, get_user
       
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
        if not self.active_users.has_key(name):
            self.active_users[name] = []
        self.active_users[name].append(request.sid)

    def del_user(self, name, sid):
        if self.active_users.has_key(name):
            self.active_users[name].remove(sid)

    def is_connected(self, name):
        return name in self.active_users

    def get_sids(self, name):
        return self.active_users[name]

active_users = ActiveUsers()
socketio = SocketIO(app)
Session(app)

if __name__ == '__main__':
    socketio.run(app)


# Handlers for sockio events. Since anyone can setup a socketio to the server,
# we need check if user is logged in, but we are happy to take disconnects.
@socketio.on("connected")
def connected(json):
	"""Adds user to active user once a user connects."""
	if session.has_key("user_id"):
		active_users.add_user(json["data"], request.sid)

@socketio.on("disconnect")
def disconnect():
	"""Remove user from active users when they disconnect."""
	if session.has_key("user_id"):
		user = get_user(session["user_id"])
		active_users.del_user(user, request.sid)

@socketio.on("post")
def new_post(json):
	"""Handle a new post from discussion.html"""

	# Add time stamp to json data
	json["stamp"] = str(datetime.datetime.now())

	# Insert post into database
	result = insert("posts", ("username", "text", "stamp"), 
					(json["username"], json["text"], json["stamp"]))

	# Broadcast emit to all users
	emit("add post", json, broadcast=True)

@socketio.on("new message")
def new_message(json):
	"""Handles when a user sends a new message"""
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

			# Emit to user wishing to chat on each connection.  Flask sets up a room for each connection.
			emit("add message", json, room=sid)

			# Emit back to user
			emit("add message", json)

		# Otherwise, whoever user wants to chat with is not online
		else:

			# Add alert to json
			json["alert"] = "buddy not online"
                
			# Emit back to user
			emit("add message", json)
                
	# Public chat
	else:

	    # Broadcast on all connections
	    emit("add message", json, broadcast=True)


# Flask code


@app.route("/")
@login_required
def index():
	"""Redirect to user's homepage"""

	# Get user's id
	user = get_user(session["user_id"])

	# Render template with my_prof set to True because user is accessing own profile
   	return render_template("index.html", user=user, my_prof=True)

@app.route("/profile/<user_id>")
@login_required
def profile(user_id):
	"""Redirect to another user's homepage"""

	# Get the information of the person the user wishes to look at
	view_user = query_db("SELECT * FROM users WHERE id=?", [user_id], one=True)

	# Get the user's id
	user = session["user_id"]

	# Render template with my_prof set to Flase because user is accessing someone else's profile
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

        # Handle case if username already exists
        if not result:
            return apology("username already exists")

        # Set the user's id
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html", user='')


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
    """Redirect to users page"""

    # Get all users 
    users = query_db("SELECT * FROM users")

    # Get current user id
    user_id = session["user_id"]

    # Get current user information
    user = get_user(session["user_id"])

    # Redirect user to about page
    return render_template("users.html", users=users, curr_user=user_id, user=user)

@app.route("/chat", methods=["GET"])
@login_required
def chat():
    """Redirect to public chat page"""

    # Get current user
    cur_user = get_user(session["user_id"])

    # Get most recent 10 public chat messages from database
    messages = query_db("SELECT * FROM messages WHERE buddy=? ORDER BY stamp DESC LIMIT 10", [""])

    # Redirect to public chat page
    return render_template("chat.html", user=cur_user, dest="", messages=messages)

@app.route("/private/<username>", methods=["GET"])
@login_required
def private(username):
    """Redirect to private chat page"""

    # Get current user
    cur_user = get_user(session["user_id"])

    # Get user current user wishes to chat with 
    user = query_db("SELECT * FROM users WHERE id=?", [session["user_id"]], one=True)

    # Get 10 most recent messages from conversation between these two users
    messages = query_db("SELECT * FROM messages WHERE (username=? AND buddy=?) OR (username=? AND buddy=?) ORDER BY stamp DESC LIMIT 10",
    					[user["username"], username, username, user["username"]])
    
    # Redirect to private chat page
    return render_template("chat.html", user=cur_user, dest=username, messages=reversed(messages))

@app.route("/discussions", methods=["GET"])
@login_required
def discussions():
    """Redirect to discussions page"""

    # Get current user
    user = get_user(session["user_id"])

    # Get posts from most to least recent
    posts = query_db("SELECT * FROM posts ORDER BY stamp DESC")

    # Redirect posts to about page
    return render_template("discussions.html", user=user, posts=reversed(posts))


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# filter to print timestap for messages in templates
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%H:%M'
    return native.strftime(format) 

@app.teardown_appcontext
def close_connection(exception):
    """Closes connection with database"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
