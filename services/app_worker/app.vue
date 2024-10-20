<script setup lang="js">
import { Stomp } from 'stompjs';

const WebSocket = window.__TAURI__.websocket;

const socket = new WebSocket('ws://localhost:15674/ws'); // Use RabbitMQ's WebSocket URL
// const client = Stomp.over(socket);

// const REQUEST_ENDPOINT = 'amqp://localhost';

// const isWorker = useState("isWorker", () => false);
// const requestToBeWorker = async (_) => {
//   isWorker.value = true;
//   // 1) Request the core server to add this phone to the network
//   response = null
//   rabbitmqUrl = (await response.json()).rabbitmq_url
//   amqp.connect(rabbitmqUrl, function(error0, connection) {
//   if (error0) {
//     throw error0;
//   }
//   connection.createChannel(function(error1, channel) {
//     if (error1) {
//       throw error1;
//     }
//     var queue = 'subtask';

//     channel.assertQueue(queue, {
//       durable: false
//     });
//   });
//   channel.consume(queue, function(msg) {
//   console.log(" [x] Received %s", msg.content.toString());
//   }, {
//     noAck: true
//   });
// });
// }
</script>

<template>
  <div>
    <p>Hello</p>
    <button @click="requestToBeWorker">Click me!</button>
    <p>{{ isWorker ? "not worker" : "worker!" }}</p>
  </div>
</template>
