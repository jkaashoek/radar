$(document).ready(function() {
  var FADE_TIME = 150; // ms
  var TYPING_TIMER_LENGTH = 400; // ms
  var COLORS = [
    '#e21400', '#91580f', '#f8a700', '#f78b00',
    '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
    '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
  ];

  var $messages = $('.messages');

  // Prompt for setting a username
  var username = $('.user').text();

  var socket = io(); //.connect('http://' + document.domain + ':' + location.port);
 // socket.emit("new message", {data: 'Hello'});
  socket.on('connect', function() {
    console.log("connected");
    socket.emit("my event", {data: "now connected"});
  })
  
  $("#trigger").click(function() {
    console.log("clicked");
    var text = $("#chat").val();
    var data = {
        username: username,
        message: text
    };
    socket.emit("client", data);
  })

  function addChatMessage(data) {
    console.log(data);
    console.log($messages);
    var $usernameDiv = $('<span class="username"/>')
      .text(data.username)
      .css('color', getUsernameColor(data.username));

    var $messageBodyDiv = $('<span class="messageBody">')
      .text(data.message);

    var $messageDiv = $('<li class="message"/>')
      .data('username', data.username)
      .append($usernameDiv, " ", $messageBodyDiv);

    $messages.append($messageDiv);
  }

  function getUsernameColor (username) {
    // Compute hash code
    var hash = 7;
    for (var i = 0; i < username.length; i++) {
       hash = username.charCodeAt(i) + (hash << 5) - hash;
    }
    // Calculate color
    var index = Math.abs(hash % COLORS.length);
    return COLORS[index];
  }

  socket.on("server", function(data) {
    console.log("message from server");
    addChatMessage(data);
  })

});


