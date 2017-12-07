RADR-CS50 Final Project. Justin Kaashoek. 2021.

The idea of the website is to provide a safe space for queer or questioning individuals, geared towards teenagers and adolescents, to talk to one another. The goal is to create a place where those who have no one in their daily life to turn to can come to and find people have or are going through similar struggles. The site is live on EC2 at: http://ec2-54-164-222-23.compute-1.amazonaws.com/

To achieve this goal, the website uses ideas from Facebook. Unlike Facebook, however, users do not have to befriend other users before talking to them... 

The requirements for the application are that it allow users to view updates in the discussion feed in real time and also be able to communicate with one another in real time. One of the main technical challenges was to exploit SocketIO, which allows real time communication between browsers through a server, to support these future. 

----- Overview -----

----- Chat Page -----

----- Private Chatting ------

----- Discussions -----

----- User support -----

----- File Overview -----

This application uses python flask as the background. Flask was chosen due to familiarity and the ability to use SocketIO with it. SocketIO allows messages to be sent and received by different users. It was very difficult to initially get SocketIO running because it was incompatible with the version of FireFox downloaded at the time. Once the most basic chat application was running, the next place of difficulty was keeping a socket across multiple web pages so that once a user is logged in, they keep the same socket until they log out. This proved to not be possible, however, as most SocketIO applications have to be written as a single page web application because JavaScript does not remain constant over multiple pages. A single page web application did not make a lot of sense, however, for this website. To solve this problem, the decision was made that once a user logins, they connect and disconnect from a socket whenever a new webpage is loaded. This adds some slight overhead when keeping a list of currently active users because this list is then updated much more often than it would if a user was connected to the same socket while they are logged in.  

Once a user is logged in, they are added to the class active users. Originally, this class was a single python list, but that was not an efficient solution because if a user was logged in multiple times, any socket emits were only received by the most recently logged in page. To solve this problem, a class was created where each username has a list of connections, and any emits are sent to all connections. 

The general chat function was the first chatting feature that was implemented. This was done user a basic socket broadcast statement, which broadcasts data to all users. Following this feature, private chatting was implemented. A line of html that includes the currently logged in user was included in layout.html but is hidden from view. This makes it possible to determine the username of the logged in user in any page that extends layout. When a user tries to start a private chat, the username of the user they wish to chat with is sent to the backend and the destination is set to the name of the user they wish to chat with. In the case of a public chat, that name is an empty string. Then, when a user tries to send a message, the function that runs when socket emits "new message" determines whether to broadcast the message to all users or to create a room with just the two users in it by looking at the destination of the message. If the “buddy,” which is the name used in the code to refer to the destination user, is not online at all, which is determined by looking in active users, a message is shown to the user in the chat room. If the "buddy" is not connected to the chat room, a notification is sent to “buddy” that someone wishes to chat with them. They can click “join” in the notification to go to a chat room with that buddy. Because notifications should only appear on pages when the user is logged in, any pages that require a login extend layout.html, which includes the notification styling, while any pages that do not require login extends home-layout, a similar file but without notification styling. 

Once a new message is sent, the message is stored in the database. The previous ten messages between users are shown on the screen, but the user has the option of viewing their entire transcript if they wish. Only ten messages are shown because in long conversations, it does not make sense to include extremely old messages. 

Users can also view other all other users profiles. This is done in a similar method as sending a private message, where the user's username that the current user wishes to view is sent to the backend. The index page has a boolean to determine if the user is viewing their own profile or someone else's. All of the information that is shown on index.html is stored in the database. For the profile pictures, a string of the path to the image is stored in the database and all the images are stored in another directory. The difference only between viewing another user's profile and the user's own profile is that the user has the option to change their profile information if they choose.

The final function of the site is discussions. This page is very similar to chats. Once a user clicks post, socket broadcasts the post to all users and adds it to the discussions.html page.   

Overall, socket introduced a number of challenging errors, and often made it difficult to test, as multiple browsers would have to be open in order to chat with another user. The appearance of the application is not very professional, which would be a priority in continuing to work on this project. I am pleased with the overall functionality of the site, although if I were to go back, I would likely use meteor instead of flask because meteor applications are single page, which would be cleaner for SocketIO. This was an interesting project and a learning experience, and I hope to be able to find the time to continue to work on the site in the future, as it has the potential to be something that could actually be used in the real world. 


