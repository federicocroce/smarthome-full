var mqtt = require("mqtt");

var options = {
  host: "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud",
  port: 8883,
  protocol: "mqtts",
  username: "fcroce",
  password: "34023936Fc",
};

// initialize the MQTT client
var client = mqtt.connect(options);

// setup the callbacks
client.on("connect", function () {
  console.log("Connected");
});

client.on("error", function (error) {
  console.log(error);
});

client.on("message", function (topic, message) {
  // called each time a message is received
  console.log("Received message:", topic, message.toString());
});

exports.clientMqtt = client;

// // subscribe to topic 'my/test/topic'
// client.subscribe("my/test/topic");

// // publish message 'Hello' to topic 'my/test/topic'
// client.publish("my/test/topic", "Hello");
