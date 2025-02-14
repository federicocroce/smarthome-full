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
const { smarthome } = require("actions-on-google");
const util = require("util");

// const { onValueUpdated } = require("firebase-functions/v2/database");

const express = require("express");
const { clientMqtt, mqttTopics } = require("./mqtt");
const { bot, sendTelegramMessage } = require("./telegram");
// Import the functions you need from the SDKs you need
const { initializeApp } = require("firebase/app");
const bodyParser = require("body-parser");
const {
  getDatabase,
  ref,
  update,
  child,
  get,
  onValue,
} = require("firebase/database");
const { google } = require("googleapis");

let publishToMqtt = true;

let lastPingDevices = {};

// const credentials = "./smart-home-key.json"; // Reemplaza con la ruta de tu archivo de credenciales

const credentials = require("./service-account.json");

const fs = require("fs");
const https = require("https");

// Hardcoded user ID
// const USER_ID = "117076068345703080494";
const USER_ID = "123";

const app = express();
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));

const port = process.env.PORT || 8443; // Puedes cambiar el puerto aquí si lo deseas

console.log(`COMIENZA LA APP`);

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
const db = getDatabase(firebaseApp);
const dbRef = ref(db);

const auth = new google.auth.GoogleAuth({
  credentials,
  scopes: "https://www.googleapis.com/auth/homegraph",
});
const homegraph = google.homegraph({
  version: "v1",
  auth: auth,
});

const commands = {
  // {[commandName]: traitName} => {SetFanSpeed: FanSpeed} (HomeGraph)
  OnOff: { traitName: "OnOff", stateKey: "on" },
  BrightnessAbsolute: { traitName: "Brightness", stateKey: "brightness" },
  ColorAbsolute: { traitName: "ColorSetting", stateKey: "color" },
  // SetFanSpeed: { attribute:"FanSpeed",
  // SetModes: { attribute:"Modes",
  // ThermostatTemperatureSetpoint: { attribute:"TemperatureSetting",
  // ThermostatSetMode: { attribute:"TemperatureSetting",
  // ThermostatTemperatureSetRange: "TemperatureSetting",
};

const actionsTopics = {
  [mqttTopics?.update_device?.name]: ({ topic, message }) => {
    publishToMqtt = false;
    const messageFormatted = JSON.parse(message);
    console.log(topic, messageFormatted);
    const { device: deviceId, value } = messageFormatted;

    Object.entries(value).forEach((val) => {
      const [traitName, keyValue] = val;
      const [key, state] = Object.entries(keyValue)[0];

      update(dbRef, { [`/${deviceId}/${traitName}/${key}`]: state }).then(
        () => state
      );
    });
  },
  [mqttTopics?.status?.name]: ({ topic, message }) => {
    const messageFormatted = JSON.parse(message);
    console.log(topic, messageFormatted);

    sendTelegramMessage(JSON.stringify(messageFormatted));
  },
  [mqttTopics?.reconnect?.name]: ({ topic, message }) => {
    console.log(topic, message.toString("utf-8"));
    sendTelegramMessage(message.toString("utf-8"));
  },
  [mqttTopics?.sendTelegramMessage?.name]: ({ topic, message }) => {
    console.log("sendTelegramMessage", { topic, message });
    if (typeof message.toString("utf-8") === "string") {
      sendTelegramMessage(message.toString("utf-8"));
    } else {
      const messageFormatted = JSON.parse(message);
      console.log(topic, messageFormatted);

      sendTelegramMessage(JSON.stringify(messageFormatted));
    }
  },
};

setTimeout(() => {
  console.log("Sus");
  Object.entries(mqttTopics).forEach(([, { name, hasSubscribe }]) => {
    console.log({ name, hasSubscribe });
    if (hasSubscribe) clientMqtt.subscribe(name);
  });
}, 1000);

clientMqtt.onResponseTopics(({ topic, message }) => {
  console.log(`onResponseTopics`, topic);

  // clientMqtt.subscribe("update_device");
  if (topic in actionsTopics) {
    console.log("topic in actionsTopics", topic);

    // publishToMqtt = mqttTopics[topic].publishToMqtt || false;
    actionsTopics[topic]({ topic, message });
  }
});

// Ruta principal que muestra "Hello, World!"
app.get("/", (req, res) => {
  console.log("soy el /", req.body);
  // const { devicesId } = req.body;
  res.send(`Hello, World! 1`);
});

const getAllDevices = async () => {
  const snapshot = await get(child(dbRef, "/"));
  return snapshot.val();
};

bot.command("deviceStatus", async (ctx) => {
  /**
  1- Desde telegram se escribe /deviceStatus.
  2- El esp32 recibe el topic "device_status" desde el mqtt. 
  3- El esp32 envia el topic "status" al mqtt con los datos de sus dispositivos.
  4- El server recibe el topic "status" con los datos del dispositivo y lo en via a Telegram por medio de sendTelegramMessage
 */
  console.log("deviceStatus local");
  clientMqtt.publish("device_status", "obtiene el estado");
});

app.get("/deviceIsConnected", async (req, res) => {
  console.log(req.query.deviceId);
  const device = req.query.deviceId;
  try {
    const snapshot = await get(child(dbRef, `${device}`));
    if (snapshot.exists()) {
      const value = snapshot.val();
      lastPingDevices[device] = new Date().getTime();
      res.status(200).send(value);
    } else {
      console.log("No data available");
    }
  } catch (error) {
    console.log({ error });
  }
});

app.get("/getAllDevices", async (req, res) => {
  console.log(req.body);
  const devicesData = await getAllDevices();
  res.status(200).send(devicesData);
});

app.post("/getDevicesValue", async (req, res) => {
  console.log("devicesId", req.body);
  const { devicesId } = req.body;

  if (!devicesId) res.send("Ids invalidos.");

  const promises = devicesId.map((device) => get(child(dbRef, `${device}`)));

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

app.get("/getDevicesValue", async (req, res) => {
  const devicesId = req.query.devicesId.split(",");
  console.log(devicesId);

  const promises = devicesId.map((device) => get(child(dbRef, `${device}`)));

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

////////////////////////////////////////////////////
//

app.get("/login", (req, res) => {
  console.log("login get");
  res.send(`
  <html>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <body>
      <form action="/login" method="post">
        <input type="hidden"
          name="responseurl" value="${req.query.responseurl}" />
        <button type="submit" style="font-size:14pt">
          Link this service to Google
        </button>
      </form>
    </body>
  </html>
  `);
});

app.post("/login", (req, res) => {
  const responseurl = decodeURIComponent(req.body.responseurl);
  console.log(`Redirect to ${responseurl}`);
  res.redirect(responseurl);
});

app.get("/fakeauth", (req, res) => {
  console.log(`req.query get ${req.query}`);
  const responseurl = util.format(
    "%s?code=%s&state=%s",
    decodeURIComponent(req.query.redirect_uri),
    "xxxxxx",
    req.query.state
  );
  console.log(`Set redirect as ${responseurl}`);
  res.redirect(`/login?responseurl=${encodeURIComponent(responseurl)}`);
});

/**
 *
 */

app.post("/faketoken", (req, res) => {
  const grantType = req.query.grant_type || req.body.grant_type;
  console.log(`Grant type ${grantType}`);

  let obj;
  if (grantType === "authorization_code") {
    obj = {
      token_type: "bearer",
      access_token: "123access",
      refresh_token: "123refresh",
      expires_in: secondsInDay,
    };
  } else if (grantType === "refresh_token") {
    obj = {
      token_type: "bearer",
      access_token: "123access",
      expires_in: secondsInDay,
    };
  }
  res.status(HTTP_STATUS_OK).json(obj);
});

let jwt;
try {
  jwt = require("./smart-home-key.json");
} catch (e) {
  functions.logger.warn("Service account key is not found");
  functions.logger.warn("Report state and Request sync will be unavailable");
}

/////////////////////////////////////////////////////
//

const appSmarthome = smarthome({
  jwt: jwt,
  debug: true,
});

let devicelist;
devicelist = require("./devices.json");
const deviceitems = JSON.parse(JSON.stringify(devicelist));

async function getUserIdOrThrow(headers) {
  const userId = await getUser(headers);
  const userExists = await firestore.userExists(userId);
  if (!userExists) {
    throw new Error(
      `User ${userId} has not created an account, so there are no devices`
    );
  }
  return userId;
}

appSmarthome.onSync(async (body, headers) => {
  const snapshot = await get(child(dbRef, "/"));

  const userId = await getUserIdOrThrow(headers);

  console.log(snapshot.val());
  // firebaseRef.once("value", (snapshot) => {
  const children = snapshot.val();
  for (devicecounter = 0; devicecounter < deviceitems.length; devicecounter++) {
    const device = deviceitems[devicecounter];
    const { traits } = device;
    const deviceRef = child(dbRef, device.id);
    // const deviceRef = firebaseRef.child(device.id);

    if (!children || !children[device.id]) {
      for (let indexTrait = 0; indexTrait < traits.length; indexTrait++) {
        const trait = traits[indexTrait];
        const traitName = trait.split("action.devices.traits.")[1];
        set(deviceRef, `${traitName}`, "");
        // deviceRef.child(traitName).set("");
      }
    }
  }
  return {
    requestId: body.requestId,
    payload: {
      agentUserId: userId,
      devices: deviceitems,
    },
  };
  // });
});

const queryFirebase = async (deviceId) => {
  const snapshot = await get(child(dbRef, deviceId));
  const snapshotVal = snapshot.val();

  const deviceValues = Object.entries(snapshotVal).reduce((prev, [, value]) => {
    return {
      ...prev,
      ...value,
    };
  }, {});

  return deviceValues;
};

appSmarthome.onQuery(async (body) => {
  const { requestId } = body;

  const payload = {
    devices: {},
  };
  functions.logger.log("Esto es una prueba onQuery");

  const queryPromises = [];
  const intent = body.inputs[0];
  for (const device of intent.payload.devices) {
    const deviceId = device.id;
    queryPromises.push(
      (async () => {
        const data = await queryFirebase(deviceId);
        payload.devices[deviceId] = data;
      })()
    );
  }
  // Wait for all promises to resolve

  await Promise.all(queryPromises);
  // functions.logger.log("Esto es una prueba onQuery 2", payload);

  return {
    requestId: requestId,
    payload: payload,
  };
});

const updateDevice = async (execution, deviceId) => {
  const { params, command } = execution;
  let state = params;

  const commandName = command.split("action.devices.commands.")[1];

  return update(dbRef, `/${deviceId}/${commands[commandName].traitName}`);
};

appSmarthome.onExecute(async (body, headers) => {
  const { requestId } = body;
  const userId = await getUserIdOrThrow(headers);

  // Execution results are grouped by status
  functions.logger.log("Esto es una prueba onExecute");
  const result = {
    ids: [],
    status: "SUCCESS",
    states: {
      online: true,
    },
  };

  const executePromises = [];
  const intent = body.inputs[0];
  for (const command of intent.payload.commands) {
    for (const device of command.devices) {
      for (const execution of command.execution) {
        executePromises.push(
          updateDevice(execution, device.id)
            .then((data) => {
              result.ids.push(device.id);
              Object.assign(result.states, data);
            })
            .catch(() => functions.logger.error("EXECUTE", device.id))
        );
      }
    }
  }

  await Promise.all(executePromises);
  return {
    agentUserId: userId,
    requestId: requestId,
    payload: {
      commands: [result],
    },
  };
});

// Configura la ruta para la función HTTP
app.post("/smarthome", (req, res) => {
  appSmarthome(req, res);
});

app.post("/requestsync", async (request, response) => {
  response.set("Access-Control-Allow-Origin", "*");
  functions.logger.info(`Request SYNC for user ${USER_ID}`);
  try {
    const res = await homegraph.devices.requestSync({
      requestBody: {
        agentUserId: USER_ID,
      },
    });
    functions.logger.info("Request sync response:", res.status, res.data);
    response.json(res.data);
  } catch (err) {
    functions.logger.error(err);
    response.status(500).send(`Error requesting sync: ${err}`);
  }
});

const initServer = async () => {
  // console.log("Init server");
  let firstCall = true;
  const devicesData = await getAllDevices();
  const deviceKeys = Object.keys(devicesData);
  console.log("Init server", deviceKeys);

  for (let index = 0; index < deviceKeys.length; index++) {
    const key = deviceKeys[index];
    const deviceRef = ref(db, key);
    // console.log("init", deviceRef);
    onValue(deviceRef, async (snapshot) => {
      if (firstCall) {
        if (deviceKeys.length === index + 1) firstCall = false;
        return;
      }

      if (!publishToMqtt) {
        publishToMqtt = true;
        return;
      }

      const data = snapshot.val();
      const deviceId = snapshot.key;

      // console.log(`snapshot ${snapshot.key}`, data);

      const deviceStatus = Object.values(data).reduce(
        (accum, curr) => ({ ...accum, ...curr }),
        {}
      );

      const requestBody = {
        requestId: "ff36a3cc" /* Any unique ID */,
        // requestId: "ff36a3ccsiddhy" /* Any unique ID */,
        agentUserId: USER_ID /* Hardcoded user ID */,
        payload: {
          devices: {
            states: {
              /* Report the current state of our light */
              // [deviceId]: { on: true },
              [deviceId]: deviceStatus,

              // [context.params.deviceId]: deviceStatus,
            },
          },
        },
      };

      // functions.logger.info("ENTRA A REPORTSTATE", {
      //   requestBody,
      //   deviceId,
      // });

      try {
        const res = await homegraph.devices.reportStateAndNotification({
          requestBody,
        });

        // console.log({ res });

        // const res = await homegraphClient.devices.reportStateAndNotification({
        //   requestBody: {
        //     agentUserId: "ff36a3cc",
        //     requestId: "PLACEHOLDER-REQUEST-ID",
        //     payload: {
        //       devices: {
        //         states: {
        //           "PLACEHOLDER-DEVICE-ID": {
        //             on: true,
        //           },
        //         },
        //       },
        //     },
        //   },
        // });
        // if (publishToMqtt) {
        console.log("SI publica EN MQTT");
        clientMqtt.publish(
          mqttTopics?.mi_topic?.name,
          JSON.stringify({ [deviceId]: deviceStatus })
          // JSON.stringify({ [deviceId]: deviceStatus })
        );
        // } else {
        //   console.log("NO publica EN MQTT");
        //   publishToMqtt = true;
        // }
      } catch (error) {
        console.log({ error });
      }

      // functions.logger.info("Report state response:", res.status, res.data);
    });
  }
};

initServer();

https
  .createServer(
    {
      cert: fs.readFileSync("certificate.pem"),
      key: fs.readFileSync("key.key"),
    },
    app
  )
  .listen(port, () => {
    console.log(`Servidor Express escuchando en https://localhost:${port}`);
  });

// Inicia el servidor en el puerto especificado
// app.listen(port, () => {
//   console.log(`Servidor Express escuchando en http://localhost:${port}`);
// });
