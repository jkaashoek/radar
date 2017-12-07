# RADR-CS50 Final Project. Justin Kaashoek. 2021.

The idea of the website is to provide a safe space for queer or questioning
individuals, geared towards teenagers and adolescents, to talk to one
another. The goal is to create a place where those who have no one in their
daily life to turn to can come to and find people who have or are going through
similar struggles. The site is live on EC2 at:
http://ec2-54-164-222-23.compute-1.amazonaws.com/

To achieve this goal, the website uses ideas from Facebook. There is a
discussion section where users can post articles or thoughts that are visible to
other users. The site also includes private messaging between users. Unlike
Facebook, however, users do not have to befriend other users before messaging
them or seeing their posts. There is also a chat with all registered users.

The requirements for the application are that it allow users to view updates in
the discussion feed in real time and also be able to communicate with one
another in real time. One of the main technical challenges was to exploit
SocketIO, which allows real time communication between browsers through a
server.


# Overview.

This application uses Python Flask as the background. Flask was chosen due to
familiarity and the ability to use SocketIO with it. It was difficult to
initially get SocketIO running because the CS50 shim initially broke it. Furthermore,
it was incompatible with the version of FireFox downloaded on my virtual box that I
switched to.  In addition to socketIO, the site uses Sqlite3, Javascript, Jquery
and Flask's templating language.

A challenge in using socketIO with Flask is that Flask encourage multi-page
applications, but when a user changes from one page to another, a new Javascript
starts running, and the socket for socketIO must set up again.  A single page web
application did not make a lot of sense, however, for this website. To solve
this problem, the decision was made that once a user logs in, they connect and
disconnect from a socket whenever a new webpage is loaded. This adds some
communication overhead between browser and server. In addition, there is slight
overhead when keeping a list of currently active users because this list is then
updated much more often than it would if a user was connected to the same socket
while they are logged in.  The server keeps track of all these connections in
connections.py.

# Public Chatting.

The general chat function was the first chatting feature that was implemented. A
line of html that includes the currently logged in user was included in
layout.html but is hidden from view. This makes it possible to determine the
username of the logged in user in any page that extends layout.  

When a user presses enter in the chat box, the message along with the username
of the user and the destination is sent to the server when socket emits "new
message". The destination of the chat, called "buddy" in the code, is set to an
empty string, which signifies that the chat is a public chat. 

When this message is received by the server, the message is stored in a database
of message and time stamped. This chat is then broadcast to all users and each
receiving browser adds the message to the html using Javascript.

If there are previous messages from public chatting, the 10 most recent messages
are shown by looking in the database of messages when the user navigates to the
chats page. The entire conversation is not shown because conversations are often long.

Messages are timestamped on the server, instead of user's browser, so there is a
consistent time (the server's) across all messages.

# Private Chatting.

Following the public chatting feature, private chatting was implemented. When a
user tries to start a private chat, the username of the user they wish to chat
with is sent to the backend and "buddy" is set to the name of the user they wish
to chat with. The message is also added to a database of messages. Instead of
broadcasting the chat to all users, however, a private room is created for the
two users. If the “buddy,” which is the name used in the code to refer to the
destination user, is not online at all, which is determined by looking in active
users (explained further in user support section), a message is shown to the
user in the chat room. Similar to public chatting, if there are previous
messages between the two users, the 10 most recent messages are shown.


# Notifications.

If the "buddy" that a user wishes to communicate with is online but is not
connected to the chat room, the server sends a notification to “buddy” that
someone wishes to chat with them. The user can click “join” in the notification to
go to the chat room with the person who is attempting to communicate with
them. Because notifications should only appear on pages when the user is logged
in, any pages that require a login extend layout.html, which includes the
notification styling, while any pages that do not require login extend
home-layout, a similar file but without notification styling.

# Discussions.

The discussions pages is similar to a Facebook news feed. Most recent posts are
shown at the top. Users can post by filling out a form. When they click submit,
socket emits "post" and sends the username of the person posting and the text of
the post to the server. The post is stored in a database of posts, and then
broadcast to all users. The post is added to the html using JavaScript. There is
currently no functionality for commenting on posts, but this is one of the next
steps for future work.

# User Support.

A user registers through the registration form, which adds a row to a database
of users that contains an id, the user's username, and his/her password. If a
user attempts to log in, their login information is compared against the data
stored in the users table of the database for the user of that username.

Users can also view all other users profiles. This is done in a similar
method as sending a private message, where the user's username that the current
user wishes to view is sent to the back end. The index page has a boolean to
determine if the user is viewing their own profile or someone else's. All of the
information that is shown on index.html is stored in the database. In the future,
functionality for uploading a profile picture will be added. To accomplish this, 
a string of the path to the image is stored in the database and all the images 
are stored in another directory. The difference between viewing another 
user's profile and the user's own profile will be that the user has the option to 
change their profile information if they choose.

Once a user is logged in, they are added to the class active users. Originally,
this class was a single python list, but that was not an efficient solution
because if a user was logged in multiple times, any socket emits were only
received by the most recently logged in page. To solve this problem, a class was
created where each username has a list of connections, and any emits are sent to
all connections.

When a user logs out, their session is terminated. 

The server code attempts to be carefully about checking that users are logged in
(using @login_required) and that messages are from users who are logged in, and
match the user logged in.


# File Overview.

radar.db: Database for application

application.py: Server code for socket and flask code for rendering templates.

helpers.py: Helper for database code, including connecting, inserting, and
reading from database

radar.wsgi: Configuration for apache (on EC2)

database.txt: Commands to create the database tables

static/script.js: Client code and html related JavaScript and jQuery

static/style.css: HTML Styling

templates/: HTML for webpages


# Reflections.

I am pleased with the overall functionality of the site. Although if I were to
go back, I would likely use meteor instead of flask because meteor applications
are single page, which would be cleaner for SocketIO.

Overall, SocketIO introduced a number of challenging errors, and often made it
difficult to test, as multiple browsers would have to be open in order to chat
with another user. SocketIO does, however, make the site real time, which was 
one of the major goals.

There is still a lot that can be done with the site, such as functionality for
chat groups, better styling, better message support, and uploading profile
pictures. I would like to continue to work on this as it has the potential to 
be something that could actually be used in the real world.  A security review 
of the code would also be necessary for a real deployment.


