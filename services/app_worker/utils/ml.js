export function demonstrate() {
  // Initialize training loss and accuracy metrics
  const trainLoss = tf.metrics.mean("train_loss");
  const trainAccuracy = tf.metrics.sparseCategoricalAccuracy("train_accuracy");

  // Define the first part of the model
  const modelPart1 = tf.sequential();
  modelPart1.add(
    tf.layers.dense({
      units: 4,
      inputShape: [1],
      activation: "relu",
    })
  );

  // Define the second part of the model
  const modelPart2 = tf.sequential();
  modelPart2.add(
    tf.layers.dense({
      units: 1,
      activation: "linear",
    })
  );

  // Combine both parts into a single model
  const fullModel = tf.sequential();
  fullModel.add(modelPart1);
  fullModel.add(modelPart2);

  // Compile the full model
  fullModel.compile({
    optimizer: "sgd",
    loss: "meanSquaredError",
  });

  // Sample training data
  const xs = tf.tensor2d([1, 2, 3, 4], [4, 1]);
  const ys = tf.tensor2d([3, 5, 7, 9], [4, 1]); // y = 2x + 1

  // Function to train the model
  async function trainModel() {
    for (let epoch = 0; epoch < 3; epoch++) {
      // Reset training metrics
      trainLoss.resetStates();
      trainAccuracy.resetStates();

      console.log(`Epoch ${epoch + 1}/3`);

      const history = await fullModel.fit(xs, ys, {
        epochs: 1, // Train for 1 epoch at a time
        callbacks: {
          onEpochEnd: (epoch, logs) => {
            console.log(`Epoch ${epoch + 1}: loss = ${logs.loss.toFixed(4)}`);
          },
        },
      });
    }
  }

  // Function to test the model
  async function testModel() {
    const testInput = tf.tensor2d([5], [1, 1]);
    const prediction = fullModel.predict(testInput);
    prediction.print();
  }

  // Train and test the model
  (async () => {
    await trainModel(); // Train the model
    console.log("Training complete");
    await testModel(); // Test the model
  })();

  // Using the model parts separately
  function useModelParts() {
    // Get the output from the first part
    const intermediateOutput = modelPart1.predict(xs);
    // Use the intermediate output as input to the second part
    const finalOutput = modelPart2.predict(intermediateOutput);

    // Print the outputs
    intermediateOutput.print();
    finalOutput.print();
  }

  // Call the function to demonstrate using parts separately
  useModelParts();

  // Print the number of layers in modelPart1 and modelPart2
  console.log("Number of layers in modelPart1:", modelPart1.layers.length);
  console.log("Number of layers in modelPart2:", modelPart2.layers.length);

  // Function to merge models
  function mergeModels(modelPart1, modelPart2) {
    const fullInput = modelPart1.input;
    const intermediateOutput = modelPart1.output;
    const fullOutput = modelPart2.apply(intermediateOutput);

    return tf.model({ inputs: fullInput, outputs: fullOutput });
  }

  // Merge the models
  const mergedModel = mergeModels(modelPart1, modelPart2);

  // Example of generating sample data for testing intermediate outputs
  const sampleData = tf.randomUniform([2, 224, 224, 3]);
  const intermediateOutput = modelPart1.apply(sampleData);
  console.log("Intermediate output shape:", intermediateOutput.shape);
  const finalOutput = modelPart2.apply(intermediateOutput);
  console.log("Final output shape:", finalOutput.shape);
}
