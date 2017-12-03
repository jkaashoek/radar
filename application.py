from flask import Flask, flash, redirect, render_template, request, session, g
from flask_socketio import SocketIO, send, emit
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from helpers import apology, login_required, get_db, make_dicts, query_db, insert

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
socketio = SocketIO(app)
Session(app)

if __name__ == '__main__':
    socketio.run(app)

@socketio.on("connect")
def connected():
	print("connected")

@socketio.on('client')
def new_mesage(json):
	print('received json: ' + str(json))
	emit("server", json, broadcast=True)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
@login_required
def index():
    return render_template("index.html")


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
        return render_template("login.html")


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

    # Redirect user to about page
    return render_template("about.html")

@app.route("/chat", methods=["GET"])
@login_required
def chat():
    """Redirect to chat page"""
    return render_template("chat.html")

@app.route("/discussions", methods=["GET"])
@login_required
def discussions():
    """Redirect to about page"""

    # Redirect user to about page
    return render_template("discussions.html")


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
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
