# radar
cs50 final project

The idea of the website is to provide a safe space for queer or questioning individuals, geared towards teenagers and adolescents, to talk to one another. The goal is to create a place where those who have no one in their daily life to turn to can come to and find people have or are going through similar struggles.

To run this application, you will need Flask, sqlite, and SocketIO. To install SocketIO, run
$ pip install flask-socketio

Once all of these have been installed, run the application using
$ flask run


Once the application is running, navigate to the "about" tab to read more about the motivation behind the project. To test the application, you will need multiple browsers. FireFox is not recommended. For some reason, SocketIO does not work well with FireFox, and although all the features of the site do work in the browser, the application can take longer to respond than in Chrome. In each browser, register a different user in the "register" tab of the home page. If you have already made an account, simply log in at the "log in" tab. Once logged in, you will see the user's profile on each account. This page will be mostly blank, except for a few details that you have already filled in. You have the option of uploading a profile picture if you choose. 

From your profile page, you have a number of options. To enter a chat with all the users who are currently active, click the "chat" tab. Note that if you type a message in this chat, any users who are online but are not in the chat will NOT receive a notification that someone is trying to chat with them. This is intentional because otherwise a user could be flooded by messages from the group chat. Another option is to look at all the other users who are using the application by navigating to the "users" tab. On this page, you can choose to view a user's profile, which will take you to the user's profile page. You can also choose to chat privately with one user at a time by click the "Enter private chat" link. You can start typing messages in this chat and the user who you wish to chat to will receive a notification that you wish to chat with them. Once they also navigate to the "users" tab and click "enter private chat" next to your username, you will be able to chat with each other. The final option from your home page is to navigate to the "discussions" tab. This page consists of article and other thoughts posted by all users, similar to a Facebook news feed. You have the option of posting articles if you choose. Future work on this page will include functionality for commenting on posts. 

Once you have examined all tabs, you can log out again using the "logout" option in the upper right hand corner.


