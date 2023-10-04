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
const functions = require("firebase-functions");
const { smarthome } = require("actions-on-google");
const { google } = require("googleapis");
const util = require("util");
const admin = require("firebase-admin");
const logger = require("firebase-functions/logger");
const { clientMqtt, mqttTopics } = require("./mqtt");

// const mqttTopics = {
//   mi_topic: "mi_topic",
//   mi_topic_response: "mi_topic_response",
// };
console.log(`COMIENZA LA APP`);

// const mqtt = require("mqtt");

// var options = {
//   host: "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud",
//   port: 8883,
//   protocol: "mqtts",
//   username: "fcroce",
//   password: "34023936Fc",
// };

// // initialize the MQTT client
// var clientMqtt = mqtt.connect(options);

// // setup the callbacks
// clientMqtt.on("connect", function () {
//   console.log("Connected");
// });

// clientMqtt.on("error", function (error) {
//   console.log(error);
// });

// clientMqtt.on("message", function (topic, message) {
//   // called each time a message is received
//   functions.logger.log("Received message:", topic, message.toString());
//   console.log("Received message:", topic, message.toString());
// });

// clientMqtt.subscribe("mi_topic");

///////////////////////////////////////////////////////////////////
//

///////////////////////////////////////////////////
const actionsTopics = {
  [mqttTopics.update_device]: ({ topic, message }) => {
    clientMqtt.publish(
      mqttTopics.update_device_response,
      `soy la response desde actions_topics DESDE LOCAL: ${message.toString()}`
    );
  },
};

setTimeout(() => {
  console.log("Sus");
  clientMqtt.subscribe(mqttTopics.update_device_response);
}, 1000);

clientMqtt.onResponseTopics(({ topic, message }) => {
  functions.logger.log(`onResponseTopics`, topic);

  // clientMqtt.subscribe("update_device");
  if (topic in actionsTopics) {
    actionsTopics[topic]({ topic, message });
  }
});

/////////

exports.helloWorld = functions.https.onRequest((request, response) => {
  const { text } = request.body;
  // publish message 'Hello' to topic 'my/test/topic'
  // client.publish("my/test/topic", "Hello");
  clientMqtt.publish("update_device", `Actualizo el disponsitivo ${text}`);

  response.status(200).send("ok Fede");
});

// Initialize Firebase
admin.initializeApp();
const firebaseRef = admin.database().ref("/");
const auth = new google.auth.GoogleAuth({
  scopes: "https://www.googleapis.com/auth/homegraph",
});
const homegraph = google.homegraph({
  version: "v1",
  auth: auth,
});

// Hardcoded user ID
const USER_ID = "123";

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

const filterHomeGraphConfigByTraitName = (keyParam) => {
  return Object.entries(HomeGraphConfig).reduce((accum, [key, value]) => {
    console.log({ value }, { keyParam }, value.traitName === keyParam);
    if (value.traitName === keyParam) {
      return {
        key,
        value,
      };
    }
    return accum;
  }, {});
};

exports.login = functions.https.onRequest((request, response) => {
  if (request.method === "GET") {
    functions.logger.log("Requesting login page");
    response.send(`
    <html>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <body>
        <form action="/login" method="post">
          <input type="hidden"
            name="responseurl" value="${request.query.responseurl}" />
          <button type="submit" style="font-size:14pt">
            Link this service to Google
          </button>
        </form>
      </body>
    </html>
  `);
  } else if (request.method === "POST") {
    // Here, you should validate the user account.
    // In this sample, we do not do that.
    const responseurl = decodeURIComponent(request.body.responseurl);
    functions.logger.log(`Redirect to ${responseurl}`);
    return response.redirect(responseurl);
  } else {
    // Unsupported method
    response.send(405, "Method Not Allowed");
  }
});

exports.fakeauth = functions.https.onRequest((request, response) => {
  const responseurl = util.format(
    "%s?code=%s&state=%s",
    decodeURIComponent(request.query.redirect_uri),
    "xxxxxx",
    request.query.state
  );
  functions.logger.log(`Set redirect as ${responseurl}`);
  return response.redirect(
    `/login?responseurl=${encodeURIComponent(responseurl)}`
  );
});

exports.faketoken = functions.https.onRequest((request, response) => {
  const grantType = request.query.grant_type
    ? request.query.grant_type
    : request.body.grant_type;
  const secondsInDay = 86400; // 60 * 60 * 24
  const HTTP_STATUS_OK = 200;
  functions.logger.log(`Grant type ${grantType}`);

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
  response.status(HTTP_STATUS_OK).json(obj);
});

let jwt;
try {
  jwt = require("./smart-home-key.json");
} catch (e) {
  functions.logger.warn("Service account key is not found");
  functions.logger.warn("Report state and Request sync will be unavailable");
}

const app = smarthome({
  jwt: jwt,
  debug: true,
});

let devicelist;
devicelist = require("./devices.json");
const deviceitems = JSON.parse(JSON.stringify(devicelist));

var devicecounter;

app.onSync((body) => {
  functions.logger.log("Esto es una prueba onSync 1");

  firebaseRef.once("value", (snapshot) => {
    const children = snapshot.val();
    functions.logger.log(
      "Esto es una prueba onSync firebaseRef children",
      children
    );
    for (
      devicecounter = 0;
      devicecounter < deviceitems.length;
      devicecounter++
    ) {
      const device = deviceitems[devicecounter];
      const { traits } = device;
      const deviceRef = firebaseRef.child(device.id);

      if (!children || !children[device.id]) {
        for (let indexTrait = 0; indexTrait < traits.length; indexTrait++) {
          const trait = traits[indexTrait];
          const traitName = trait.split("action.devices.traits.")[1];
          deviceRef.child(traitName).set("");
        }
      }
    }
  });

  functions.logger.log("Esto es una prueba onSync 2");

  return {
    requestId: body.requestId,
    payload: {
      agentUserId: USER_ID,
      devices: deviceitems,
    },
  };
});

const queryFirebase = async (deviceId) => {
  const snapshot = await firebaseRef.child(deviceId).once("value");
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

app.onQuery(async (body) => {
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

  const ref = firebaseRef
    .child(deviceId)
    .child(commands[commandName].traitName);

  return ref.update(state).then(() => state); // state = {[stateKey]: value} => {on: true}
};

app.onExecute(async (body) => {
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

app.onDisconnect((body, headers) => {
  // functions.logger.log("User account unlinked from Google Assistant");
  // Return empty response
  return {};
});

exports.smarthome = functions.https.onRequest(app);

exports.requestsync = functions.https.onRequest(async (request, response) => {
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

// exports.getDevicesState = functions.https.onRequest(
//   async (request, response) => {
//     const { command, devicesId } = request.body;

//     const requestBody = {
//       requestId: "ff36a3cc" /* Any unique ID */,
//       // requestId: "ff36a3ccsiddhy" /* Any unique ID */,
//       agentUserId: USER_ID /* Hardcoded user ID */,
//       payload: {
//         devices: [
//           {
//             id: "led1",
//           },
//         ],
//       },
//     };

//     functions.logger.info("ENTRA A getDevicesState", {
//       requestBody,
//       deviceId: context.params.deviceId,
//     });

//     const res = await homegraph.devices.query({
//       requestBody,
//     });

//     functions.logger.info("query state response:", res.status, res.data);

//   }
// );

// exports.getDevicesState = functions.https.onRequest(
//   async (request, response) => {
//     const { devices } = request.body;

//     functions.logger.info("ENTRA A getDevicesState", {
//       devices,
//     });
//     try {
//       const queryPromises = [];
//       for (const deviceId of devices) {
//         queryPromises.push(
//           homegraph.devices.query({
//             requestBody: {
//               agentUserId: USER_ID, // Reemplaza con el ID del usuario agente (usuario de Google)
//               inputs: [
//                 {
//                   payload: {
//                     devices: [
//                       {
//                         id: deviceId, // Reemplaza con el ID del dispositivo que quieres consultar
//                       },
//                       // Puedes agregar más dispositivos si es necesario
//                     ],
//                   },
//                 },
//               ],
//             },
//           })
//         );
//       }
//       functions.logger.info(
//         "QUERY state response queryPromises:",
//         queryPromises
//       );
//       queryPromises;
//       // Wait for all promises to resolve
//       const res = await Promise.all(queryPromises);

//       clientMqtt.subscribe("get_devices_state");

//       // await homegraph.devices.query({
//       //   requestBody: {
//       //     agentUserId: USER_ID, // Reemplaza con el ID del usuario agente (usuario de Google)
//       //     inputs: [
//       //       {
//       //         payload: {
//       //           devices: [
//       //             {
//       //               id: "led1", // Reemplaza con el ID del dispositivo que quieres consultar
//       //             },
//       //             // Puedes agregar más dispositivos si es necesario
//       //           ],
//       //         },
//       //       },
//       //     ],
//       //   },
//       // });
//       functions.logger.info("QUERY state response:", res);
//       // Manejar la respuesta de la API
//       // console.log(response.data);
//       response.status(200).send("ok");
//     } catch (error) {
//       // Manejar errores
//       functions.logger.info(
//         "Error al realizar la consulta a HomeGraph:",
//         error.message
//       );
//     }

//     // const res = await homegraph.devices.query(requestBody);

//     // functions.logger.info("query state response:", res.status, res.data);
//   }
// );

// exports.updateDeviceState = functions.https.onRequest(
//   async (request, response) => {
//     const { command, state, deviceId } = request.body;

//     const resFirebase = await updateDevice(
//       {
//         command,
//         params: state,
//       },
//       deviceId
//     );

//     functions.logger.info("Se actualiza Firebase");

//     response.status(200).send(resFirebase);
//   }
// );

/**
 * Send a REPORT STATE call to the homegraph when data for any device id
 * has been changed.
 */
exports.reportstate = functions.database
  .ref("{deviceId}")
  .onUpdate(async (change, context) => {
    // functions.logger.info("SOURCE change.after", change.after);
    // functions.logger.info("SOURCE change.before", change.before);
    // functions.logger.info("SOURCE change.after.data", change.after.data);
    // functions.logger.info("SOURCE change.after.val", change.after.val);
    // const snapshot = change.after.val();
    // // functions.logger.info("SOURCE reportstate snapshot", snapshot);
    // // functions.logger.info("SOURCE reportstate source", snapshot.source);
    // // const before = change.before.data();
    // // functions.logger.info("SOURCE reportstate source", before);
    // const deviceStatus = Object.values(snapshot).reduce(
    //   (accum, curr) => ({ ...accum, ...curr }),
    //   {}
    // );
    // const requestBody = {
    //   requestId: "ff36a3cc" /* Any unique ID */,
    //   // requestId: "ff36a3ccsiddhy" /* Any unique ID */,
    //   agentUserId: USER_ID /* Hardcoded user ID */,
    //   payload: {
    //     devices: {
    //       states: {
    //         /* Report the current state of our light */
    //         [context.params.deviceId]: deviceStatus,
    //       },
    //     },
    //   },
    // };
    // functions.logger.info("ENTRA A REPORTSTATE", {
    //   requestBody,
    //   deviceId: context.params.deviceId,
    // });
    // const res = await homegraph.devices.reportStateAndNotification({
    //   requestBody,
    // });
    // clientMqtt.publish(
    //   "mi_topic",
    //   JSON.stringify({ [context.params.deviceId]: deviceStatus })
    // );
    // functions.logger.info("Report state response:", res.status, res.data);
  });
