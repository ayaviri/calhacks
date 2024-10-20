<script setup lang="js">
import amqp from 'amqplib/callback_api';

const isWorker = useState("isWorker", () => false);
const requestToBeWorker = async (_) => {
  isWorker.value = true;
}

</script>

<template>
  <div>
    <button @click="requestToBeWorker">Click me!</button>
    <p>{{ isWorker ? "not worker" : "worker" }}</p>
  </div>
</template>
