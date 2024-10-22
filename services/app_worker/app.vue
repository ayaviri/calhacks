<script setup lang="js">
import { Base64 } from 'js-base64';
// import { storeKerasModel, readKerasModel, storeTrainedModel, readTrainedModel } from "./utils/disk";
import axios from 'axios';
import { getGraphicsName } from "./utils/invokeHardware"
import { demonstrate } from './utils/ml';
// worker: a box falls into their thing, a gear spins, then its wrapped into a present background turns light green
// client: sends a rocket, and then gets dropped a box every time

// const invoke = window.__TAURI__.core.invoke;

// STATES: "inactive", "loading", "active"
const isWorker = useState("isWorker", () => "inactive");
const runningInterval = useState("runningInterval", () => null);
const graphicsName = useState("graphicsName", () => "");
const currentEpoch = useState("currentEpoch", () => "");

onMounted(async () => {
  graphicsName.value = await getGraphicsName();
});

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

const trainPartialModel = async (_) => {
  if (isWorker.value === "inactive") {
    isWorker.value = "loading";
  }
  else {
    isWorker.value = "inactive";
    clearInterval(runningInterval.value);
    runningInterval.value = null;
    console.log("HELLO");
    return;
  }

      // Utility function to log messages to the page
      function log(message) {
        console.log(message);
    }


  // Function to generate dummy data
  function generateDummyData(numSamples, inputDim, numClasses) {
            // Generate random input features
            const xs = tf.randomNormal([numSamples, inputDim]);

            // Generate random labels (integers from 0 to numClasses-1)
            const labels = tf.floor(tf.randomUniform([numSamples], 0, numClasses));

            return { xs, labels };
        }

        // Function to create a simple sequential model
        function createModel(inputDim, numClasses) {
            const model = tf.sequential();

            // Input layer
            model.add(tf.layers.dense({
                inputShape: [inputDim],
                units: 16,
                activation: 'relu'
            }));

            // Hidden layer
            model.add(tf.layers.dense({
                units: 16,
                activation: 'relu'
            }));

            // Output layer
            model.add(tf.layers.dense({
                units: numClasses,
                activation: 'softmax'
            }));

            return model;
        }

        // Function to train the model
        async function trainModel(model, xs, ys, epochs, batchSize) {
            // Compile the model with optimizer, loss, and metrics
            model.compile({
                optimizer: 'adam',
                loss: 'sparseCategoricalCrossentropy',
                metrics: ['accuracy'],
            });

            log('Starting training...\n');

            // Train the model
            const history = await model.fit(xs, ys, {
                epochs: epochs,
                batchSize: batchSize,
                shuffle: true,
                callbacks: {
                    onEpochEnd: (epoch, logs) => {
                        currentEpoch.value = `Epoch ${epoch+1} with Loss: ${logs.loss.toFixed(4)}`;
                        log(`Epoch ${epoch + 1} / ${epochs}`);
                        log(` - loss: ${logs.loss.toFixed(4)} - accuracy: ${(logs.acc * 100).toFixed(2)}%`);
                        log(''); // Add an empty line for readability
                    }
                }
            });

            log('Training complete!\n');
        }

        // Function to make and display predictions
        async function makePredictions(model, xs, numClasses) {
            log('Making predictions on new data...\n');

            // Predict probabilities
            const preds = model.predict(xs);

            // Convert predictions to class labels
            const predictedLabels = preds.argMax(-1).dataSync();

            // Log some predictions
            const numPredictionsToShow = Math.min(10, predictedLabels.length);
            for (let i = 0; i < numPredictionsToShow; i++) {
                log(`Sample ${i + 1}: Predicted Class = ${predictedLabels[i]}`);
            }

            // Clean up tensors
            preds.dispose();
        }

        // Main function to orchestrate data generation, model training, and prediction
        async function main() {
            // Parameters
            const numSamples = 1000;
            const inputDim = 20;      // Number of input features
            const numClasses = 3;     // Number of classes for classification
            const epochs = 10;
            const batchSize = 32;

            log(`Generating ${numSamples} samples with ${inputDim} features each for ${numClasses} classes...\n`);

            // Generate dummy data
            const { xs, labels } = generateDummyData(numSamples, inputDim, numClasses);

            log('Dummy data generated.\n');

            // Split data into training and testing sets (80% train, 20% test)
            const splitIndex = Math.floor(numSamples * 0.8);
            const xTrain = xs.slice(0, splitIndex);
            const yTrain = labels.slice(0, splitIndex);
            const xTest = xs.slice(splitIndex);
            const yTest = labels.slice(splitIndex);

            log(`Training set: ${xTrain.shape[0]} samples`);
            log(`Testing set: ${xTest.shape[0]} samples\n`);

            // Create the model
            const model = createModel(inputDim, numClasses);
            log('Model architecture created.\n');

            // Train the model
            await trainModel(model, xTrain, yTrain, epochs, batchSize);

            // Evaluate the model on test data
            log('Evaluating model on test data...\n');
            const evalResult = model.evaluate(xTest, yTest);
            const testLoss = (await evalResult[0].data())[0];
            const testAcc = (await evalResult[1].data())[0];
            log(`Test Loss: ${testLoss.toFixed(4)}`);
            log(`Test Accuracy: ${(testAcc * 100).toFixed(2)}%\n`);

            // Make predictions on test data
            await makePredictions(model, xTest, numClasses);

            // Dispose tensors to free memory
            xs.dispose();
            labels.dispose();
            xTrain.dispose();
            yTrain.dispose();
            xTest.dispose();
            yTest.dispose();
            model.dispose();

            await new Promise(r => setTimeout(r, 2000));
            currentEpoch.value = "All set!";
            isWorker.value = "active";

        }

  // Run the main function
  main().catch(err => log(`Error: ${err.message}`));
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
    class="relative w-full h-screen grid place-items-center"
  >
    <div  class="absolute flex flex-row top-3 left-3 w-fit justify-left items-center gap-3">
      <div class="text-white font-mono italic">{{ currentEpoch }}</div>
      <svg v-if="isWorker === 'loading'"
        class="w-6 h-6 text-gray-300 animate-spin"
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
      >
        <path
          d="M32 3C35.8083 3 39.5794 3.75011 43.0978 5.20749C46.6163 6.66488 49.8132 8.80101 52.5061 11.4939C55.199 14.1868 57.3351 17.3837 58.7925 20.9022C60.2499 24.4206 61 28.1917 61 32C61 35.8083 60.2499 39.5794 58.7925 43.0978C57.3351 46.6163 55.199 49.8132 52.5061 52.5061C49.8132 55.199 46.6163 57.3351 43.0978 58.7925C39.5794 60.2499 35.8083 61 32 61C28.1917 61 24.4206 60.2499 20.9022 58.7925C17.3837 57.3351 14.1868 55.199 11.4939 52.5061C8.801 49.8132 6.66487 46.6163 5.20749 43.0978C3.7501 39.5794 3 35.8083 3 32C3 28.1917 3.75011 24.4206 5.2075 20.9022C6.66489 17.3837 8.80101 14.1868 11.4939 11.4939C14.1868 8.80099 17.3838 6.66487 20.9022 5.20749C24.4206 3.7501 28.1917 3 32 3L32 3Z"
          stroke="currentColor"
          stroke-width="5"
          stroke-linecap="round"
          stroke-linejoin="round"
        ></path>
        <path
          d="M32 3C36.5778 3 41.0906 4.08374 45.1692 6.16256C49.2477 8.24138 52.7762 11.2562 55.466 14.9605C58.1558 18.6647 59.9304 22.9531 60.6448 27.4748C61.3591 31.9965 60.9928 36.6232 59.5759 40.9762"
          stroke="currentColor"
          stroke-width="5"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="text-gray-900"
        ></path>
      </svg>
    </div>
    <div class="w-full flex flex-col items-center">
      <p class="text-slate-300 text-xl">Running on {{ graphicsName }}</p>
      <p class="text-white text-2xl font-mono px-10 text-center">
        {{
          isWorker === "inactive"
            ? "Let's not make your phone go to waste."
            : isWorker === "loading"
            ? "Now processing..."
            : "...and done!"
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
