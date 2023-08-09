/**
 * Copyright 2018 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"use strict";

// require("firebase-functions/logger/compat");

const express = require("express");
const { clientMqtt, mqttTopics } = require("./mqtt");
// Import the functions you need from the SDKs you need
const { initializeApp } = require("firebase/app");
const bodyParser = require("body-parser");
const { getDatabase, ref, update, child, get } = require("firebase/database");
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCd-Mh3TtpGvBWXOSCQmEJ1EiUr11kzll8",
  authDomain: "smart-home-fc-76670.firebaseapp.com",
  databaseURL: "https://smart-home-fc-76670-default-rtdb.firebaseio.com",
  projectId: "smart-home-fc-76670",
  storageBucket: "smart-home-fc-76670.appspot.com",
  messagingSenderId: "1045536356759",
  appId: "1:1045536356759:web:418bfff020f88ca2b26cd2",
};

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);
const dbRef = ref(getDatabase(firebaseApp));

const app = express();
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));

const port = process.env.PORT || 3000; // Puedes cambiar el puerto aquí si lo deseas

console.log(`COMIENZA LA APP`);

const actionsTopics = {
  [mqttTopics.update_device]: ({ topic, message }) => {
    const messageFormatted = JSON.parse(message);
    console.log(topic, messageFormatted);
    const { device: deviceId, value } = messageFormatted;

    const [traitName, keyValue] = Object.entries(value)[0];
    const [key, state] = Object.entries(keyValue)[0];

    update(dbRef, { [`/${deviceId}/${traitName}/${key}`]: state }).then(
      () => state
    );
  },
};

setTimeout(() => {
  console.log("Sus");
  clientMqtt.subscribe(mqttTopics.update_device);
}, 1000);

clientMqtt.onResponseTopics(({ topic, message }) => {
  console.log(`onResponseTopics`, topic);

  // clientMqtt.subscribe("update_device");
  if (topic in actionsTopics) {
    actionsTopics[topic]({ topic, message });
  }
});

// Ruta principal que muestra "Hello, World!"
app.get("/", (req, res) => {
  console.log(req.body);
  // const { devicesId } = req.body;
  res.send(`Hello, World!`);
});

app.post("/getDevicesValue", async (req, res) => {
  console.log("devicesId", req.body);
  const { devicesId } = req.body;

  const promises = devicesId.map((device) => get(child(dbRef, `${device}`)));
  // devicesId.forEach((device) => {

  // });
  try {
    const snapshots = await Promise.all(promises);
    const response = snapshots.reduce((prev, curr, index) => {
      console.log({ curr });
      return {
        ...prev,
        [devicesId[index]]: curr?.val(),
      };
    }, {});
    console.log({ response });
    res.send(response);
  } catch (error) {
    console.log({ error });
  }
});

// Inicia el servidor en el puerto especificado
app.listen(port, () => {
  console.log(`Servidor Express escuchando en http://localhost:${port}`);
});
