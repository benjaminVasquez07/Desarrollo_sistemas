import WebSocket from "ws";

// Conectar al servidor WebSocket
const client = new WebSocket("ws://localhost:8080");

// Escuchar mensajes del servidor
client.on("message", (message) => {
  console.log(`Mensaje recibido del servidor: ${message}`);
});

// Enviar un mensaje al servidor una vez conectado
client.on("open", () => {
  console.log("Conectado al servidor WebSocket.");
  client.send("¡Hola desde el cliente!");
});

// Manejar el cierre de la conexión
client.on("close", () => {
  console.log("Conexión cerrada.");
});

