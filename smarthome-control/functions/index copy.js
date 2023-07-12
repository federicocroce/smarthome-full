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

require("firebase-functions/logger/compat");
const functions = require("firebase-functions");
const { smarthome } = require("actions-on-google");
const { google } = require("googleapis");
const util = require("util");
const admin = require("firebase-admin");
const logger = require("firebase-functions/logger");

// Initialize Firebase
admin.initializeApp();
const firebaseRef = admin.database().ref("/");
const auth = new google.auth.GoogleAuth({
  scopes: ["https://www.googleapis.com/auth/homegraph"],
});
const homegraph = google.homegraph({
  version: "v1",
  auth: auth,
});

// Hardcoded user ID
const USER_ID = "123";

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
  firebaseRef.once("value", (snapshot) => {
    // functions.logger.log("onSync children", children);
    const children = snapshot.val();
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

      // functions.logger.log("onSync device", { children });

      // functions.logger.log("onSync Complete", {
      //   children,
      //   deviceID: device.id,
      // });
      // functions.logger.log("onSync device", { device: children[device.id] });
      // if (children[device.id]) return;

      // firebaseRef.child(device.id).set("fede");
    }
  });

  // functions.logger.log("onSync childrens", { childrens });

  // functions.logger.log("onSync traits", { traits });
  // const traitsFormatted =
  //   traits &&
  //   traits.reduce((prev, curr) => {
  //     const traitName = curr.split("action.devices.traits.")[1];
  //     return {
  //       ...prev,
  //       [traitName]: null,
  //     };
  //   }, {});

  // functions.logger.log("traitsFormatted", { traitsFormatted });

  // firebaseRef.child(device.id).set(traitsFormatted);

  // if (
  //   deviceitems[devicecounter].traits.includes(
  //     "action.devices.traits.TemperatureSetting"
  //   )
  // ) {
  //   if (
  //     deviceitems[devicecounter].attributes.queryOnlyTemperatureSetting ==
  //     true
  //   ) {
  //     firebaseRef
  //       .child(deviceitems[devicecounter].id)
  //       .child("TemperatureSetting")
  //       .set({
  //         thermostatMode: "off",
  //         thermostatTemperatureAmbient: 20,
  //         thermostatHumidityAmbient: 90,
  //       });
  //   } else if (
  //     deviceitems[devicecounter].attributes.queryOnlyTemperatureSetting ==
  //     false
  //   ) {
  //     firebaseRef
  //       .child(deviceitems[devicecounter].id)
  //       .child("TemperatureSetting")
  //       .set({
  //         thermostatMode: "off",
  //         thermostatTemperatureSetpoint: 25.5,
  //         thermostatTemperatureAmbient: 20,
  //         thermostatHumidityAmbient: 90,
  //         thermostatTemperatureSetpointLow: 15,
  //         thermostatTemperatureSetpointHigh: 30,
  //       });
  //   }
  // }
  // if (
  //   deviceitems[devicecounter].traits.includes("action.devices.traits.OnOff")
  // ) {
  //   firebaseRef
  //     .child(deviceitems[devicecounter].id)
  //     .child("OnOff")
  //     .set({ on: false });
  // }
  // if (
  //   deviceitems[devicecounter].traits.includes(
  //     "action.devices.traits.Brightness"
  //   )
  // ) {
  //   firebaseRef
  //     .child(deviceitems[devicecounter].id)
  //     .child("Brightness")
  //     .set({ brightness: 10 });
  // }
  // if (
  //   deviceitems[devicecounter].traits.includes(
  //     "action.devices.traits.ColorSetting"
  //   )
  // ) {
  //   firebaseRef
  //     .child(deviceitems[devicecounter].id)
  //     .child("ColorSetting")
  //     .set({ color: { name: "deep sky blue", spectrumRGB: 49151 } });
  // }
  // if (
  //   deviceitems[devicecounter].traits.includes("action.devices.traits.Modes")
  // ) {
  //   var modename =
  //     deviceitems[devicecounter].attributes.availableModes[0].name;
  //   var modevalue =
  //     deviceitems[devicecounter].attributes.availableModes[0].settings[0]
  //       .setting_name;
  //   firebaseRef
  //     .child(deviceitems[devicecounter].id)
  //     .child("Modes")
  //     .set({ currentModeSettings: { modename: modevalue } });
  // }
  // if (
  //   deviceitems[devicecounter].traits.includes(
  //     "action.devices.traits.FanSpeed"
  //   )
  // ) {
  //   firebaseRef
  //     .child(deviceitems[devicecounter].id)
  //     .child("FanSpeed")
  //     .set({ currentFanSpeedSetting: 20.0 });
  // }

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
  let ref;

  const commands = {
    OnOff: "OnOff",
    BrightnessAbsolute: "Brightness",
    ColorAbsolute: "ColorSetting",
    SetFanSpeed: "FanSpeed",
    SetModes: "Modes",
    ThermostatTemperatureSetpoint: "TemperatureSetting",
    ThermostatSetMode: "TemperatureSetting",
    ThermostatTemperatureSetRange: "TemperatureSetting",
  };
  const commandName = command.split("action.devices.commands.")[1];
  ref = firebaseRef.child(deviceId).child(commands[commandName]);

  return ref.update(state).then(() => state);
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

exports.updateHomegraph = functions.https.onRequest(
  async (request, response) => {
    // logger.info("REQUEST", { request: request.body });
    // logger.info("Hello logs!", { structuredData: true });
    // response.send(`Hello from Postman! ${request.body.name}`);
    const syncvalue = {
      on: request.body.on,
    };

    const postData = {
      requestId: "ff36a3ccsiddhy" /* Any unique ID */,
      agentUserId: USER_ID /* Hardcoded user ID */,
      payload: {
        devices: {
          states: {
            /* Report the current state of our light */
            led1: syncvalue,
          },
        },
      },
    };

    const res = await homegraph.devices.reportStateAndNotification({
      postData,
    });
    functions.logger.info("Report state response:", res.status, res.data);
    response.status(200).send(res);
  }
);

// const updateDevice = async (execution, deviceId) => {
//   const { params, command } = execution;
//   let state = params;
//   let ref;

//   const commands = {
//     OnOff: "OnOff",
//     BrightnessAbsolute: "Brightness",
//     ColorAbsolute: "ColorSetting",
//     SetFanSpeed: "FanSpeed",
//     SetModes: "Modes",
//     ThermostatTemperatureSetpoint: "TemperatureSetting",
//     ThermostatSetMode: "TemperatureSetting",
//     ThermostatTemperatureSetRange: "TemperatureSetting",
//   };
//   const commandName = command.split("action.devices.commands.")[1];
//   ref = firebaseRef.child(deviceId).child(commands[commandName]);

//   return ref.update(state).then(() => state);
// };

exports.setLed = functions.https.onRequest(async (request, response) => {
  // logger.info("REQUEST", { request: request.body });
  // logger.info("Hello logs!", { structuredData: true });
  // response.send(`Hello from Postman! ${request.body.name}`);
  const { command, value, deviceId } = request.body;
  // const syncvalue = {
  //   [key]: value,
  // };

  const res = await updateDevice(
    {
      command,
      params: { on: value },
    },
    deviceId
  );

  functions.logger.info('firebaseRef.child("led1")', firebaseRef.child("led1"));
  functions.logger.info("Se actualiza Firebase");
  response.status(200).send(res);

  // const res = firebaseRef.child("led1").child("OnOff").set(syncvalue);

  // const postData = {
  //   requestId: "ff36a3ccsiddhy" /* Any unique ID */,
  //   agentUserId: USER_ID /* Hardcoded user ID */,
  //   payload: {
  //     devices: {
  //       states: {
  //         /* Report the current state of our light */
  //         led1: syncvalue,
  //       },
  //     },
  //   },
  // };

  // const res = await homegraph.devices.reportStateAndNotification({
  //   postData,
  // });
  // functions.logger.info("Se actualiza Firebase", res.status, res.data);
  // response.status(200).send(res);
});

/**
 * Send a REPORT STATE call to the homegraph when data for any device id
 * has been changed.
 */
exports.reportstate = functions.database
  .ref("{deviceId}")
  .onWrite(async (change, context) => {
    // functions.logger.info("Firebase write event triggered this cloud function");
    // if (!app.jwt) {
    //   // functions.logger.warn("Service account key is not configured");
    //   // functions.logger.warn("Report state is unavailable");
    //   return;
    // }
    const snapshot = change.after.val();

    var syncvalue = {};

    if (Object.prototype.hasOwnProperty.call(snapshot, "OnOff")) {
      syncvalue = Object.assign(syncvalue, { on: snapshot.OnOff.on });
    }
    if (Object.prototype.hasOwnProperty.call(snapshot, "Brightness")) {
      syncvalue = Object.assign(syncvalue, {
        brightness: snapshot.Brightness.brightness,
      });
    }
    if (Object.prototype.hasOwnProperty.call(snapshot, "ColorSetting")) {
      syncvalue = Object.assign(syncvalue, {
        color: snapshot.ColorSetting.color,
      });
    }
    if (Object.prototype.hasOwnProperty.call(snapshot, "FanSpeed")) {
      if (
        Object.prototype.hasOwnProperty.call(
          snapshot.FanSpeed,
          "currentFanSpeedSetting"
        )
      ) {
        syncvalue = Object.assign(syncvalue, {
          currentFanSpeedSetting: snapshot.FanSpeed.currentFanSpeedSetting,
        });
      }
    }
    if (Object.prototype.hasOwnProperty.call(snapshot, "Modes")) {
      if (
        Object.prototype.hasOwnProperty.call(
          snapshot.Modes,
          "currentModeSettings"
        )
      ) {
        syncvalue = Object.assign(syncvalue, {
          currentModeSettings: snapshot.Modes.currentModeSettings,
        });
      }
    }
    if (Object.prototype.hasOwnProperty.call(snapshot, "TemperatureSetting")) {
      if (
        Object.prototype.hasOwnProperty.call(
          snapshot.TemperatureSetting,
          "thermostatMode"
        )
      ) {
        syncvalue = Object.assign(syncvalue, {
          thermostatMode: snapshot.TemperatureSetting.thermostatMode,
        });
      }
      if ("thermostatTemperatureSetpoint" in snapshot) {
        syncvalue = Object.assign(syncvalue, {
          thermostatTemperatureSetpoint:
            snapshot.TemperatureSetting.thermostatTemperatureSetpoint,
        });
      }
      if ("thermostatTemperatureAmbient" in snapshot) {
        syncvalue = Object.assign(syncvalue, {
          thermostatTemperatureAmbient:
            snapshot.TemperatureSetting.thermostatTemperatureAmbient,
        });
      }
      if ("thermostatHumidityAmbient" in snapshot) {
        syncvalue = Object.assign(syncvalue, {
          thermostatHumidityAmbient:
            snapshot.TemperatureSetting.thermostatHumidityAmbient,
        });
      }
      if ("thermostatTemperatureSetpointLow" in snapshot) {
        syncvalue = Object.assign(syncvalue, {
          thermostatTemperatureSetpointLow:
            snapshot.TemperatureSetting.thermostatTemperatureSetpointLow,
        });
      }
      if ("thermostatTemperatureSetpointHigh" in snapshot) {
        syncvalue = Object.assign(syncvalue, {
          thermostatTemperatureSetpointHigh:
            snapshot.TemperatureSetting.thermostatTemperatureSetpointHigh,
        });
      }
    }

    functions.logger.info("ENTRA A REPORTSTATE", {
      syncvalue,
      deviceId: context.params.deviceId,
    });

    const postData = {
      requestId: "ff36a3ccsiddhy" /* Any unique ID */,
      agentUserId: USER_ID /* Hardcoded user ID */,
      payload: {
        devices: {
          states: {
            /* Report the current state of our light */
            [context.params.deviceId]: syncvalue,
          },
        },
      },
    };

    const res = await homegraph.devices.reportStateAndNotification({
      postData,
    });
    functions.logger.info("Report state response:", res.status, res.data);
    // const data = await app.reportState(postData);
    // functions.logger.log("Report state came back");
    // functions.logger.info(data);
  });
