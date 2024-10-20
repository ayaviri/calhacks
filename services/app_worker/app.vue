<script setup lang="js">
import { Stomp } from 'stompjs';
// worker: a box falls into their thing, a gear spins, then its wrapped into a present background turns light green
// client: sends a rocket, and then gets dropped a box every time

// const WebSocket = window.__TAURI__.websocket;

// const socket = new WebSocket('ws://localhost:15674/ws'); // Use RabbitMQ's WebSocket URL
// const client = Stomp.over(socket);

// const REQUEST_ENDPOINT = 'amqp://localhost';

// STATES: "inactive", "loading", "active"
const isWorker = useState("isWorker", () => "inactive");
const requestToBeWorker = async (_) => {
  isWorker.value = "loading";
  // 1) Request the core server to add this phone to the network
  // response = null
  // rabbitmqUrl = (await response.json()).rabbitmq_url
  // amqp.connect(rabbitmqUrl, function(error0, connection) {
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
}
</script>

<template>
  <div
    :class="isWorker === 'active' ? 'bg-gr' : 'bg-dark-green'"
    class="w-full h-screen grid place-items-center"
  >
    <div class="w-full flex flex-col items-center">
      <p class="text-white text-2xl font-mono px-10 text-center">
        {{
          isWorker === "active"
            ? "Let's not make your phone go to waste."
            : isWorker === "loading"
            ? "Getting ready..."
            : "Let's get processing!"
        }}
      </p>

      <div class="relative mt-10">
        <div
          v-if="isWorker === 'loading'"
          class="absolute rounded-full border-2 border-yellow-400 border-red w-full h-full animate-ping"
        />
        <button class="rounded-full bg-white p-3" @click="requestToBeWorker">
          <svg
            class="w-24 h-24"
            xmlns="http://www.w3.org/2000/svg"
            height="32px"
            viewBox="0 -960 960 960"
            width="32px"
            :fill="
              isWorker === 'inactive'
                ? '#dc2626'
                : isWorker === 'loading'
                ? '#eab308'
                : '#16a34a'
            "
          >
            <path
              d="M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-84 31.5-156.5T197-763l56 56q-44 44-68.5 102T160-480q0 134 93 227t227 93q134 0 227-93t93-227q0-67-24.5-125T707-707l56-56q54 54 85.5 126.5T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm-40-360v-440h80v440h-80Z"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
