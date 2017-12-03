$(document).ready(function() {
  var FADE_TIME = 150; // ms
  var TYPING_TIMER_LENGTH = 400; // ms
  var COLORS = [
    '#e21400', '#91580f', '#f8a700', '#f78b00',
    '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
    '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
  ];
  var username = $('.user').text();
  var buddy = $('.buddy').text();
  var $messages = $('.messages');
  var $window = $(window);
  var socket;

  // Prompt for setting a username
  console.log("username og: ", username, username.length);


  if (username != '') {
    console.log("connect ", username)
    socket = io();

    socket.on('connect', function() {
      console.log("connected", username);
      socket.emit("connected", {data: username});
    })

    socket.on('disconnect', function() {
      username = '';
      console.log("disconnected");
    })

    socket.on("server", function(data) {
      console.log("message from server");
      addChatMessage(data);
    })
  }


  $window.keydown(function (event) {
    var text = $("#inputMessage").val();
    if(event.which == 13 && text != "") {
      $("#inputMessage").val('');
      var data = {
        username: username,
        message: text,
        buddy: buddy
      };
      console.log("DATA: ", data);
      socket.emit("client", data);
    }
  })

  $(".btnmsg").click(function() {
    console.log("link clicked");
    id = $(this).attr('name');
    console.log(id)
    socket.emit("private message", id)

  })
  
  // $("#trigger").click(function() {
  //   console.log("clicked");
  //   var text = $("#inputMessage").val();
  //   var data = {
  //       username: username,
  //       message: text
  //   };
  //   socket.emit("client", data);
  // })

  function addChatMessage(data) {
    console.log(data);
    console.log($messages);
    var $usernameDiv = $('<span class="username"/>')
      .text(data.username)
      .css('color', getUsernameColor(data.username));

    var $messageBodyDiv = $('<span class="messageBody">')
      .text(data.message);

    var $messageAlertDiv = $('<span class="alertBody">')
      .text(data.alert);

    var $messageDiv = $('<li class="message"/>')
      .data('username', data.username)
      .append($usernameDiv, " ", $messageBodyDiv, " ", $messageAlertDiv);

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


});


