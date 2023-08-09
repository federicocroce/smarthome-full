var mqtt = require("mqtt");

var options = {
  host: "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud",
  port: 8883,
  protocol: "mqtts",
  username: "fcroce",
  password: "34023936Fc",
};

const mqttTopics = {
  mi_topic: "mi_topic",
  mi_topic_response: "mi_topic_response",
  update_device: "update_device",
  update_device_response: "update_device_response",
};
// functions.logger.log("Esto es una prueba onExecute");

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
  console.log(`onMessage individual`);
  // client.publish(
  //   "mi_topic_response",
  //   `${topic} desde la api : ${message.toString()}`
  // );
});

client.onResponseTopics = (cbk) => {
  console.log(`onResponseTopics`);
  client.on("message", function (topic, message) {
    // called each time a message is received
    console.log(`onMessage, ${topic}`);
    if (cbk) {
      cbk({ topic, message });
    }
    //   console.log(
    //     "Received message desde el modulo:",
    //     topic,
    //     message.toString()
    //   );
    // client.publish(
    //   "mi_topic_response",
    //   `${topic} desde la api : ${message.toString()}`
    // );
  });
};

// const newClient = { ...client, onResponseTopics };
// client.subscribe("mi_topic");

exports.clientMqtt = client;
exports.mqttTopics = mqttTopics;

// // subscribe to topic 'my/test/topic'

// // publish message 'Hello' to topic 'my/test/topic'
// client.publish("my/test/topic", "Hello");
