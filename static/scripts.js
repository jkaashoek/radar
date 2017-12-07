// Inspiration for chat messaging and colors from SocketIO demo: https://socket.io/demos/chat/

$(document).ready(function() {

  // Color for styling
  var COLORS = [
    '#e21400', '#91580f', '#f8a700', '#f78b00',
    '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
    '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
  ];

  // Get variables from html

  // The username of the logged in user. Empty string if user is not logged in
  var username = $('.user').text();

  // The destination of a private message. Empty string if not a private message
  var buddy = $('.buddy').text();

  // List of messages
  var $messages = $('.messages');

  // List of notification
  var $notifications = $('.notifications');

  // List of posts
  var $posts = $('.posts');

  // Window the user is in
  var $window = $(window);

  // Variable to store socket
  var socket;

  // Check if the user has not already logged in
  if (username != '') {

    // Initialize socket
    socket = io();

    // User connects
    socket.on('connect', function() {
      socket.emit("connected", {data: username});
    })

    // User disconnects
    socket.on('disconnect', function() {
      username = '';
    })

    // User posts something in discussions
    socket.on(('add post'), function(data){
      addPost(data);
    })

    // User sends a message in a chat. NOTE: The following if block could be condensed
    // but is left the way it is for clarity. 
    socket.on("add message", function(data) {

      // Private chat and both users are on page
      if (buddy != "" && data.username == buddy && data.buddy != "") {
        addChatMessage(data);
      }

      // Public chat
      else if (buddy == "" && data.buddy == "") {
        addChatMessage(data);
      }

      // Server has emited back to user
      else if (data.username == username) {
        addChatMessage(data);
      }

      // Private chat and one user is not on chat page 
      else if (data.buddy != "") {
        addNotification(data);
      }
    })
  }

  // User is clicks submit for a post
  $("#postSubmit").click(function() {

    // Get text from post
    var text = $("#postText").val();

    // Check that the message is not blank
    if (text != "") {

      // Remove the users text from input on html page
      $("#postText").val('');

      // Data from the post
      var data = {
        username: username,
        text: text
      };

      // Tell server there is a new post
      socket.emit("post", data);
    }
  })

  // Check for inputMessage id
  if ($("#inputMessage")[0]) {
    document.getElementById("inputMessage")

      // Keep track of keys pressed in inputMessage
      .addEventListener("keyup", function(event) {

        // Get value from inputMessage when a key is pressed
        var text = $("#inputMessage").val();

        // If the key is enter and the message is not blank
        if(event.keyCode === 13 && text != "") {
          
          // Remove the user's message from input on html page
          $("#inputMessage").val('');

          // Data for a message
          var data = {
            username: username,
            message: text,
            buddy: buddy,
          };
          
          // Tell server that there is a new message
          socket.emit("new message", data);
        }
      })
  }
  
  // Style usernames from old messages in database
  $('.username').each(function(){
    var n = $(this).text();
    $(this).css('color', getUsernameColor(n));
  });

  // Add a post to html
  function addPost(data) {
    
    // Add username of the user who posted
    var $usernameDiv = $('<span class="postUsername"/>')
      .text(data.username)
      .css('color', getUsernameColor(data.username));

    // Add time the post was posted
    var d = new Date(data.stamp);
    var t = " (" + d.getHours()+ ":" + d.getMinutes()+")"
    var $stampDiv = $('<span class="postStamp">')
       .text(t);

    // Add the text of the post
    var $postBodyDiv = $('<span class="postBody">')
      .text(data.text);

    // Combine username, time, and text
    var $postDiv = $('<li class="post"/>')
      .data('username', data.username)
      .append($usernameDiv, " ", $stampDiv, "<br> ", $postBodyDiv);

    // Add post to list of posts
    $posts.prepend($postDiv);
  }
  
  // Add a chat message to html
  function addChatMessage(data) {

    // Add username of the user who posted
    var $usernameDiv = $('<span class="username"/>')
      .text(data.username)
      .css('color', getUsernameColor(data.username));

    // Add the text of the message
    var $messageBodyDiv = $('<span class="messageBody">')
      .text(data.message);

    // Add the time the message was sent
    var d = new Date(data.stamp);
    var t = " (" + d.getHours()+ ":" + d.getMinutes()+")";
    var $stampDiv = $('<span class="stamp">')
	     .text(t);

    // Add an alert if the user receiving is not online. Empty if the message is not a private message
    var $messageAlertDiv = $('<span class="alertBody">')
      .text(data.alert)
      .css('color', '#FF0000');

    // Combine username, text, time, and alert
    var $messageDiv = $('<li class="message"/>')
      .data('username', data.username)
      .append($usernameDiv, " ", $messageBodyDiv,  $stampDiv, "<br>", $messageAlertDiv);

    // Add to list of messages
    $messages.append($messageDiv);
  }

  // Add a notification
  function addNotification(data) {

      // Add join button to send user to private chat
      var $input = $('<input class="notif btn-primary" type="button" name="' + data.username + '"value="join" />');
      
      // Add notification message
      var $notificationDiv = $('<span class="notif"/>')
        .append("Chat request from ", data.username)
        .css('color', "blue");

      // Combine message and button
      $notifications.append($notificationDiv, " ", $input, "<br>");

      // When join button is clicked
      $(".notif").click(function() {

        // Get id
        id = $(this).attr('name');

        // Send to chat rooom
        window.location.href = "private/" + data.username;
      })

  }

  // Colors username differntly
  function getUsernameColor (username) {

    // Compute hash code
    var hash = 7;
    for (var i = 0; i < username.length; i++) {
       hash = username.charCodeAt(i) + (hash << 5) - hash;
    }

    // Calculate color
    var index = Math.abs(hash % COLORS.length);

    // Return color from list of colors
    return COLORS[index];
  }
});

