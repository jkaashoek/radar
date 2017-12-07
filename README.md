# radar

cs50 final project

# Using radar

The radar web site is designed to be used by users without a CS backgrond and is
quite intuitive. The easiest way to experience is to use the live site at:
http://ec2-54-164-222-23.compute-1.amazonaws.com/

# Install radar

There are two options to deploy radar yourself:

0. Deploy it for use with others.  The ec2.txt file explains all the
   instructions to get radar running on EC2, starting from creating a new EC2
   instance.
   
1. Deploy it for testing.  Create a pip virtual environment, for example:

	 $ virtualenv env
	 $ . env/bin/activate
     $ pip install flask
	 $ pip install flask_socketio
	 $ pip install flask_session
	 $ pip install python-dateutil
	 $ pip install eventlet
	 $ export FLASK_APP=application.py
	 $ create a database radar.db
	   run the commands from database.txt to create the necessary tables
	 $ run flask
       
     Open a browser and open a window with the URL that flask prints.

# Brief user guide

Once the website is running, you will see an index page with a navigation bar
with tabs for About, Register, and Login.

Register an account with a user name and password, which will also log you in.

After you login you will see a home page with similar navigation bar with tabs
for Users, Chat, Discussions, and Logout.  The page also shows your profile
(which is barebone for now but you can upload a profile picture) and a real-time
notification feed for users who want to chat with you.  Every page in Radar has
this real-time notification feed.  By clicking on the notification, you can
start a private chat with another user.

The Users tab shows all the users in the system (with a link to their profiles)
This page allows you to start a private chat session with any user.

The Chat tab is a real-time feed of broadcast messages that other users send and
you can add it to by typing a message in the box at the bottom of the page.
Users who are online will receive the messages.  Users who are not online will
not, but the messages are stored in a database at the server.  When the user
later logs in and navigates to the Chat tab, the page shows recent chats.

The Discussion tab is a real-time feed of posts (articles and thoughts), similar
to Facebook news feed. You can post new posts by typing them in the box at the
bottom of the page.  The posts are also stored in a database and the page
displays recent ones.  The intent is also have support for comments and
searching through past posts and chats, but that isn't there yet.


