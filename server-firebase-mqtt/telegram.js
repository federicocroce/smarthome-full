const { Telegraf } = require("telegraf");

// Reemplaza 'YOUR_BOT_TOKEN' con el token de tu bot.
const bot = new Telegraf("6460944738:AAEhsvU5MLRPr3qlAu4j8HeWgBJIgDYivU4");

// Reemplaza 'YOUR_CHAT_ID' con el ID de chat al que quieras enviar el mensaje.
const chatId = "5034504728";

function sendTelegramMessage(mensaje) {
  //   const mensaje =
  //     "¡Este es un mensaje de prueba enviado desde Node.js con Telegraf!";

  console.log({ mensaje });

  bot.telegram
    .sendMessage(chatId, mensaje)
    .then(() => {
      console.log("Mensaje enviado con éxito");
    })
    .catch((error) => {
      console.error("Error al enviar el mensaje:", error);
    });
}

// bot.command("deviceStatus", (ctx) => {
//   ctx.reply("deviceStatus");
// });

// Manejar el comando /test
bot.command("test", (ctx) => {
  ctx.reply("test");
});

// Enviar un mensaje cada minuto (60,000 ms).
// setInterval(sendTelegramMessage, 60000);

bot.launch();

exports.bot = bot;
exports.sendTelegramMessage = sendTelegramMessage;

// Done! Congratulations on your new bot. You will find it at t.me/smarthome_fc_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

// Use this token to access the HTTP API:
// 6460944738:AAEhsvU5MLRPr3qlAu4j8HeWgBJIgDYivU4
// Keep your token secure and store it safely, it can be used by anyone to control your bot.

// For a description of the Bot API, see this page: https://core.telegram.org/bots/api
