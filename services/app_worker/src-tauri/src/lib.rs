// use tensorflow::{Graph, Operation, Session, SessionOptions, SessionRunArgs, Tensor};

// #[tauri::command]
// fn my_custom_command() {
//   run_model();
// }

// fn run_model() -> Result<(), Box<dyn std::error::Error>> {
//     // Step 1: Build the computation graph.
//     let mut graph = Graph::new();

//     // Create a placeholder for the input.
//     let x = {
//         let dtype = tensorflow::DataType::Float;
//         let shape = &tensorflow::Shape::from(None); // Scalar input
//         graph
//             .new_operation("Placeholder", "x")?
//             .set_attr_type("dtype", dtype)?
//             .set_attr_shape("shape", shape)?
//             .finish()?
//     };

//     // Create a constant value for the slope (2.0 in y = 2x).
//     let weight = graph
//         .new_operation("Const", "weight")?
//         .set_attr_tensor("value", Tensor::new(&[]).with_values(&[2.0f32])?)?
//         .set_attr_type("dtype", tensorflow::DataType::Float)?
//         .finish()?;

//     // Multiply input and weight (y = weight * x).
//     let y = graph
//         .new_operation("Mul", "y")?
//         .add_input(x)
//         .add_input(weight)
//         .finish()?;

//     // Step 2: Create a session to execute the graph.
//     let session = Session::new(&SessionOptions::new(), &graph)?;

//     // Step 3: Prepare the input data.
//     let input_data = Tensor::new(&[]).with_values(&[3.0f32])?; // Input: x = 3.0

//     // Step 4: Run the session with the input and get the output.
//     let mut args = SessionRunArgs::new();
//     args.add_feed(&x, 0, &input_data);
//     let output_token = args.request_fetch(&y, 0);

//     // Execute the session.
//     session.run(&mut args)?;

//     // Step 5: Extract and print the output.
//     let output: Tensor<f32> = args.fetch(output_token)?;
//     println!("Output: y = {}", output[0]);

//     Ok(())
// }

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .plugin(tauri_plugin_swift::init())
    // .invoke_handler(tauri::generate_handler![my_custom_command])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
