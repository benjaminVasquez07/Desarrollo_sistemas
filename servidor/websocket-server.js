import { WebSocketServer } from "ws";

// Crear un servidor WebSocket en el puerto 8080
const server = new WebSocketServer({ port: 8080 });
console.log("Servidor WebSocket ejecutándose en ws://localhost:8080");

// Manejar nuevas conexiones
server.on("connection", (socket) => {
  console.log("Cliente conectado.");

  // Enviar un mensaje de bienvenida al cliente
  socket.send("¡Bienvenido al servidor WebSocket!");

  // Escuchar mensajes del cliente
  socket.on("message", (message) => {
    console.log(`Mensaje recibido del cliente: ${message}`);
    // Responder al cliente con un eco del mensaje
    socket.send(`Servidor recibió: ${message}`);
  });

  // Manejar el cierre de la conexión
  socket.on("close", () => {
    console.log("Cliente desconectado.");
  });
});
