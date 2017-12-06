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
socketio = SocketIO(app)
Session(app)

active_users = {}

if __name__ == '__main__':
    socketio.run(app)


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%H:%M'
    return native.strftime(format) 

@socketio.on("connected")
def connected(json):
	'''Adds user to active user once a user connects'''
	active_users[json['data']] = request.sid

@socketio.on("disconnect")
def disconnect():
	'''Remove user from active users when they disconnect'''

	# Go through active users
	for key, val in active_users.items():

		# Delete user once user is found
		if val == request.sid:
			print("user left", key)
			del active_users[key]

@socketio.on('client')
def new_mesage(json):
	'''Handles when a user sends a new message'''

	# Add message to the database
	json["stamp"] = str(datetime.datetime.now())
	result = insert("messages", ("username", "buddy", "text", "stamp"), (json["username"], json["buddy"], json["message"], json["stamp"]))

	# Alert if the user is no online
	json["alert"] = ""

	# If the person the user wishes to chat with is online
	if json["buddy"] in active_users:

		# Generate a room
		room = active_users[json["buddy"]]

		# Emit to user wishing to chat with the correct room
		emit("server", json, room=room)

		# Emit back to user
		emit("server", json)

	# If the user is entering the general chat
	elif json["buddy"] == '':

		# Enter room that will broadcast to all users
		emit("server", json, broadcast=True)

	# Otherwise, whoever user wants to chat with is not online
	else:

		# Add alert to json
		json["alert"] = "buddy not online"

		# Emit back to user
		emit("server", json)

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
