$(document).ready(function() {
  var FADE_TIME = 150; // ms
  var TYPING_TIMER_LENGTH = 400; // ms
  var COLORS = [
    '#e21400', '#91580f', '#f8a700', '#f78b00',
    '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
    '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
  ];

  // Prompt for setting a username
  var username = "jkaashoek";

  var socket = io(); //.connect('http://' + document.domain + ':' + location.port);
 // socket.emit("new message", {data: 'Hello'});
  socket.on('connect', function() {
    console.log("connected");
    socket.emit("my event", {data: "now connected"});
  })
  
  $("#trigger").click(function() {
    console.log("clicked");
    socket.emit("my event", {data: "clicked"});
  })

});


