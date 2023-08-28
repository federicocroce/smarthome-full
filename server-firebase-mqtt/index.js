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
const { onValueUpdated } = require("firebase-functions/v2/database");

const express = require("express");
const { clientMqtt, mqttTopics } = require("./mqtt");
// Import the functions you need from the SDKs you need
const { initializeApp } = require("firebase/app");
const bodyParser = require("body-parser");
const { getDatabase, ref, update, child, get } = require("firebase/database");
const { google } = require("googleapis");

const fs = require("fs");
const https = require("https");

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

const auth = new google.auth.GoogleAuth({
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

// Hardcoded user ID
const USER_ID = "123";

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
app.get("/getAllDevices", async (req, res) => {
  console.log(req.body);
  // const { devicesId } = req.body;

  const snapshot = await get(child(dbRef, "/"));

  console.log(snapshot.val());

  res.status(200).send(snapshot.val());
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

////////////////////////////////////////////////////
//

app.get("/login", (req, res) => {
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

app.use((req, res) => {
  res.status(405).send("Method Not Allowed");
});

///

app.get("/fakeauth", (req, res) => {
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

appSmarthome.onSync(async (body) => {
  const snapshot = await get(child(dbRef, "/"));

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
  // });
});

const queryFirebase = async (deviceId) => {
  const snapshot = await get(child(dbRef, deviceId));
  // const snapshot = await firebaseRef.child(deviceId).once("value");
  const snapshotVal = snapshot.val();

  // var asyncvalue = {};

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

  // const ref = firebaseRef
  //   .child(deviceId)
  //   .child(commands[commandName].traitName);

  // return ref.update(state).then(() => state); // state = {[stateKey]: value} => {on: true}
};

appSmarthome.onExecute(async (body) => {
  const { requestId } = body;
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

onValueUpdated("{deviceId}", (event) => {
  console.log("onValueUpdated", event.data.val());
  // …
});

// exports.reportstate = functions.database
//   .ref("{deviceId}")
//   .onUpdate(async (change, context) => {
//     // functions.logger.info("SOURCE change.after", change.after);
//     // functions.logger.info("SOURCE change.before", change.before);
//     // functions.logger.info("SOURCE change.after.data", change.after.data);
//     // functions.logger.info("SOURCE change.after.val", change.after.val);
//     const snapshot = change.after.val();
//     // functions.logger.info("SOURCE reportstate snapshot", snapshot);
//     // functions.logger.info("SOURCE reportstate source", snapshot.source);

//     // const before = change.before.data();
//     // functions.logger.info("SOURCE reportstate source", before);

//     const deviceStatus = Object.values(snapshot).reduce(
//       (accum, curr) => ({ ...accum, ...curr }),
//       {}
//     );

//     const requestBody = {
//       requestId: "ff36a3cc" /* Any unique ID */,
//       // requestId: "ff36a3ccsiddhy" /* Any unique ID */,
//       agentUserId: USER_ID /* Hardcoded user ID */,
//       payload: {
//         devices: {
//           states: {
//             /* Report the current state of our light */
//             [context.params.deviceId]: deviceStatus,
//           },
//         },
//       },
//     };

//     functions.logger.info("ENTRA A REPORTSTATE", {
//       requestBody,
//       deviceId: context.params.deviceId,
//     });

//     const res = await homegraph.devices.reportStateAndNotification({
//       requestBody,
//     });

//     clientMqtt.publish(
//       "mi_topic",
//       JSON.stringify({ [context.params.deviceId]: deviceStatus })
//     );

//     functions.logger.info("Report state response:", res.status, res.data);
//   });

///////////////////////////////////////////////////

///////////////////////////////////////////////////

// onRequest(app)

https
  .createServer(
    {
      cert: fs.readFileSync("certificate.pem"),
      key: fs.readFileSync("key.key"),
    },
    app
  )
  .listen(port, () => {
    console.log(`Servidor Express escuchando en http://localhost:${port}`);
  });

// Inicia el servidor en el puerto especificado
// app.listen(port, () => {
//   console.log(`Servidor Express escuchando en http://localhost:${port}`);
// });
