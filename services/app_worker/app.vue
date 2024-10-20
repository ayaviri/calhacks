<script setup lang="js">
import { Base64 } from 'js-base64';
import { storeKerasModel, readKerasModel, storeTrainedModel, readTrainedModel } from "./utils/disk";
import axios from 'axios';
// worker: a box falls into their thing, a gear spins, then its wrapped into a present background turns light green
// client: sends a rocket, and then gets dropped a box every time

// const invoke = window.__TAURI__.core.invoke;

// STATES: "inactive", "loading", "active"
const isWorker = useState("isWorker", () => "inactive");
const requestToBeWorker = async (_) => {
  isWorker.value = "loading";

  // await storeKeras("test", new Uint8Array([72, 101, 108, 108, 111]));
  // const res = await readKeras("test");
  // console.log(res);


  // await invoke("connect_and_consume");
  // console.log("FInISH");

  // const WebSocket = window.__TAURI__.websocket;
  // const socket = new WebSocket(websocketUrl);
  // const client = Stomp.over(socket);

  // const REQUEST_ENDPOINT = 'amqp://localhost';

  // client.connect('guest', 'guest', function (frame) {
  //   console.log('Connected: ' + frame);

  //   // Subscribe to a queue
  //   client.subscribe('/queue/test', function (message) {
  //     console.log("Received message: " + message.body);
  //   });

  //   // Send a message
  //   client.send('/queue/test', {}, 'Hello, RabbitMQ!');
  // });

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

function concatUint8Arrays(arrays) {
    let totalLength = arrays.reduce((acc, value) => acc + value.length, 0);
    let result = new Uint8Array(totalLength);

    let offset = 0;
    arrays.forEach((array) => {
        result.set(array, offset);
        offset += array.length;
    });

    return result;
}

const trainPartialModel = (_) => {
  async function pollAPI() {
    const interval = setInterval(async () => {
      try {
        // AXIOS 
        // TODO: How are we going to get task ID
        const response = await axios.get(`http://localhost:8000/subtask`);

        if (response.status === 200) {
          if (response.data.dataset_name === 'fashion_mnist') {
            console.log('Received dataset: fashion_mnist');

            // Train the model and return it as a byte array
            const modelByteArray = await trainAndReturnModelAsByteArray();

            console.log('Model saved as byte array:', modelByteArray);
            clearInterval(interval);

            // TODO: send byte array to server
            const resultStr = Base64.encode(modelByteArray);
            await axios.post("http://localhost:8000/host/result", { 
              encoded_model_shard_file_contents: resultStr,
              task_num: response.data.task_num,
              task_id: response.data.task_id,
              subtask_count: response.data.subtask_count,
            },)
          }
        }
      } catch (error) {
        console.error('Error polling API:', error);
      }
    }, 2000); // Poll every 2 seconds
  }

  /**
   * Preprocesses the images.
   */
  function preprocessImages(images) {
    return images
      .reshape([images.shape[0], 28, 28, 1]) // Expand dimensions
      .resizeBilinear([224, 224]) // Resize to 224x224
      .div(255.0); // Normalize
  }

  /**
   * Trains the model and returns it as a byte array.
   */
  async function trainAndReturnModelAsByteArray() {
    const { images: xTrain, labels: yTrain } = tf.data.fashionMnist().train;
    const { images: xTest, labels: yTest } = tf.data.fashionMnist().test;

    const xTrainPreprocessed = preprocessImages(xTrain);
    const xTestPreprocessed = preprocessImages(xTest);

    // Define the model
    const model = tf.sequential();
    model.add(
      tf.layers.conv2d({
        inputShape: [224, 224, 1],
        filters: 32,
        kernelSize: 3,
        activation: 'relu',
      })
    );
    model.add(tf.layers.maxPooling2d({ poolSize: [2, 2] }));
    model.add(tf.layers.flatten());
    model.add(tf.layers.dense({ units: 10, activation: 'softmax' }));

    // Compile the model
    model.compile({
      optimizer: 'adam',
      loss: 'sparseCategoricalCrossentropy',
      metrics: ['accuracy'],
    });

    // Train the model
    await model.fit(xTrainPreprocessed, yTrain, {
      epochs: 10,
      batchSize: 32,
      validationData: [xTestPreprocessed, yTest],
    });

    // Evaluate the model
    const [testLoss, testAcc] = await model.evaluate(xTestPreprocessed, yTest);
    console.log(`Test accuracy: ${testAcc}`);

    // Save the model to memory as JSON and weights in binary format
    const saveResult = await model.save(tf.io.withSaveHandler(async (artifacts) => {
      // Convert the model artifacts to byte arrays
      const encoder = new TextEncoder();
      const jsonBytes = encoder.encode(artifacts.modelTopology); // Convert string to Uint8Array
      const weightBytes = artifacts.weightData; // Assuming weightData is already a Uint8Array

      // Combine the JSON and weight data into a single byte array
      const byteArray = concatUint8Arrays([jsonBytes, weightBytes]);

      console.log('Model saved to byte array successfully.');
      return byteArray;
    }));


    return saveResult; // Return the byte array containing the model
  }

  // Start polling the API
  pollAPI();
}



    // polling
  // while loop:
  //  time.sleep(2)
  //  keep hitting "/foo"
  //  if 200 status code, then read response

  // JSON object
  /**
   * encorded-model_file_contewnts: str (basic 64 encoded string)
   * 2. dsecode into array of types
   * 3. write to disk
   * 4. import the model from the .keras file created from the disk
   *
   * 1. dataset_name
   * 2. tf.load_dataset(name here)
   *
   * 1. RUN TRAINING FOR EPOCHS USING BOTH then do .export()
   * 2. POST req "/result"
   * 3/ request body json
   * encorded-model_file_contewnts (4 -> 3 -> 2)
   *
   * 1. task_id
   * 2. task_num
   * 3. subtask_count
   */

// async function trainModel() {
//         // Step 1: Create a simple sequential model
//         const model = tf.sequential();
//         model.add(tf.layers.dense({ units: 1, inputShape: [1] }));

//         // Step 2: Compile the model with loss function and optimizer
//         model.compile({
//           loss: 'meanSquaredError',
//           optimizer: 'sgd',
//         });

//         // Step 3: Generate dummy training data
//         const xs = tf.tensor2d([1, 2, 3, 4], [4, 1]); // Input: [1, 2, 3, 4]
//         const ys = tf.tensor2d([1, 3, 5, 7], [4, 1]); // Output: [1, 3, 5, 7] (y = 2x - 1)

//         // Step 4: Train the model
//         await model.fit(xs, ys, { epochs: 100 });

//         // Step 5: Make a prediction for a new input
//         const output = model.predict(tf.tensor2d([5], [1, 1]));
//         output.print(); // Prints the prediction to the console

//         // Display prediction on the webpage
//         document.getElementById('output').innerText =
//           'Model Output: ' + output.dataSync();
//       }
</script>

<template>
  <div
    :class="isWorker === 'active' ? 'bg-gr' : 'bg-dark-green'"
    class="w-full h-screen grid place-items-center"
  >
    <div class="w-full flex flex-col items-center">
      <p class="text-white text-2xl font-mono px-10 text-center">
        {{
          isWorker === "inactive"
            ? "Let's not make your phone go to waste."
            : isWorker === "loading"
            ? "Getting ready..."
            : "Now processing!"
        }}
      </p>

      <div class="relative mt-10">
        <div
          v-if="isWorker === 'loading'"
          class="absolute rounded-full border-2 border-yellow-400 border-red w-full h-full animate-ping"
        />
        <button class="rounded-full bg-white p-3" @click="trainPartialModel">
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
