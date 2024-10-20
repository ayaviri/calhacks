// Function to run the model
const runModel = async () => {
    // Step 1: Create a simple sequential model
    const model = tf.sequential();
    model.add(tf.layers.dense({ units: 1, inputShape: [1] }));

    // Step 2: Compile the model with loss function and optimizer
    model.compile({
      loss: 'meanSquaredError',
      optimizer: 'sgd',
    });

    // Step 3: Generate dummy training data
    const xs = tf.tensor2d([1, 2, 3, 4], [4, 1]); // Input: [1, 2, 3, 4]
    const ys = tf.tensor2d([1, 3, 5, 7], [4, 1]); // Output: [1, 3, 5, 7] (y = 2x - 1)

    // Step 4: Train the model
    await model.fit(xs, ys, { epochs: 100 });

    // Step 5: Make a prediction for a new input
    const output = model.predict(tf.tensor2d([5], [1, 1]));
    output.print(); // Prints the prediction to the console
    out.value = JSON.stringify(output);
    console.log("HELLO")

    // Display prediction on the webpage
    // document.getElementById('output').innerText =
    //   'Model Output: ' + output.dataSync();
};

// Load TensorFlow.js when the component is mounted
// onMounted(async () => {
//     await loadTensorFlow();
// });