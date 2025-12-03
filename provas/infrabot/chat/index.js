var app = require('express')();
var http = require('http');
var server = http.Server(app)
var io = require('socket.io')(server);
var port = process.env.PORT || 3000;

const URL_ROBO = "http://localhost:7000";
const URL_ROBO_RESPOSTA = `${URL_ROBO}/resposta`;

const CONFIANCA_MINIMA = 0.50;

getResposta = (mensagem, socket) => {
  let retorno = "";

  http.get(`${URL_ROBO_RESPOSTA}/${mensagem}`, (stream) => {
    stream.on("data", (pedaco) => {
      retorno += pedaco;
    });
    stream.on("end", () => {
      retorno = JSON.parse(retorno);

      if (retorno.confianca >= CONFIANCA_MINIMA) {
        socket.emit("chat message", `🤖 ${retorno.resposta}`)
      } else {
        socket.emit("chat message", `🤖 Desculpe, não entendi o comando. Tente algo como "status cpu" ou "reiniciar nginx".`)
      }
    });
  });
}

app.get('/', function (req, res) {
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', function (socket) {
  socket.on('chat message', function (msg) {
    // Removed echo: io.emit('chat message', `👤 ${msg}`);
    getResposta(msg, socket);
  });
});

server.listen(port, function () {
  console.log('atendendo na porta *:' + port);
});
