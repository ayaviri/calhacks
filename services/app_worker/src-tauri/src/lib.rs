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

// use lapin::{options::*, types::FieldTable, Connection, ConnectionProperties, Channel, Consumer};
// use futures_lite::stream::StreamExt;
// use tauri::{async_runtime::spawn, AppHandle, Manager};
// use tokio;

use amqprs::{
    callbacks::{DefaultChannelCallback, DefaultConnectionCallback},
    channel::{
        BasicConsumeArguments, BasicPublishArguments, QueueBindArguments, QueueDeclareArguments,
    },
    connection::{Connection, OpenConnectionArguments},
    consumer::DefaultConsumer,
    BasicProperties,
};
use tauri::AppHandle;
use tokio::time;

#[tauri::command]
async fn connect_and_consume(app_handle: AppHandle) {
    // open a connection to RabbitMQ server
    let connection = Connection::open(&OpenConnectionArguments::new(
        "localhost",
        5672,
        "guest",
        "guest",
    ))
    .await
    .unwrap();
    connection
        .register_callback(DefaultConnectionCallback)
        .await
        .unwrap();

    println!("HELLO I AM CONNECTING");
    println!("{}", connection);

    // open a channel on the connection
    let channel = connection.open_channel(None).await.unwrap();
    channel
        .register_callback(DefaultChannelCallback)
        .await
        .unwrap();

    // declare a durable queue
    let (queue_name, _, _) = channel
        .queue_declare(QueueDeclareArguments::durable_client_named(
            "amqprs.examples.basic",
        ))
        .await
        .unwrap()
        .unwrap();

    // bind the queue to exchange
    let routing_key = "amqprs.example";
    let exchange_name = "amq.topic";
    channel
        .queue_bind(QueueBindArguments::new(
            &queue_name,
            exchange_name,
            routing_key,
        ))
        .await
        .unwrap();

    //////////////////////////////////////////////////////////////////////////////
    // start consumer with given name
    let args = BasicConsumeArguments::new(&queue_name, "example_basic_pub_sub");

    channel
        .basic_consume(DefaultConsumer::new(args.no_ack), args)
        .await
        .unwrap();

    //////////////////////////////////////////////////////////////////////////////
    // publish message
    let content = String::from(
        r#"
            {
                "publisher": "example"
                "data": "Hello, amqprs!"
            }
        "#,
    )
    .into_bytes();

    // create arguments for basic_publish
    let args = BasicPublishArguments::new(exchange_name, routing_key);

    channel
        .basic_publish(BasicProperties::default(), content, args)
        .await
        .unwrap();

    // keep the `channel` and `connection` object from dropping before pub/sub is done.
    // channel/connection will be closed when drop.
    time::sleep(time::Duration::from_secs(100)).await;
    // explicitly close

    channel.close().await.unwrap();
    connection.close().await.unwrap();
}
//     // Replace with your RabbitMQ address
//     let addr = "amqp://guest:guest@192.168.1.100:5672/%2f";

//     // Connect to RabbitMQ
//     let connection = Connection::connect(&addr, ConnectionProperties::default()).await
//         .map_err(|e| format!("Failed to connect: {}", e))?;

//     // Open a channel
//     let channel = connection.create_channel().await
//         .map_err(|e| format!("Failed to create channel: {}", e))?;

//     // Declare a queue (if not already created)
//     channel.queue_declare(
//         &queue_name,
//         QueueDeclareOptions::default(),
//         FieldTable::default()
//     ).await.map_err(|e| format!("Failed to declare queue: {}", e))?;

//     // Start consuming messages
//     let consumer = channel.basic_consume(
//         &queue_name,
//         "my_consumer",
//         BasicConsumeOptions::default(),
//         FieldTable::default()
//     ).await.map_err(|e| format!("Failed to consume: {}", e))?;

//     // Handle incoming messages asynchronously
//     spawn(async move {
//         println!("Waiting for messages...");
//         consumer.for_each(|delivery| async {
//             if let Ok(delivery) = delivery {
//                 let message = String::from_utf8_lossy(&delivery.data);
//                 println!("Received message: {}", message);

//                 // Emit message to Tauri frontend
//                 app_handle.emit_all("rabbitmq_message", message.to_string()).unwrap();

//                 // Acknowledge message
//                 delivery.ack(BasicAckOptions::default()).await.unwrap();
//             }
//         }).await;
//     });
// spawn(async move {
//     consumer.for_each_concurrent(None, move |delivery| {
//         let sender = sender.clone();
//         async move {
//             if let Ok(delivery) = delivery {
//                 let message = String::from_utf8_lossy(&delivery.data).to_string();
//                 println!("Received message: {}", message);

//                 // Send the message to the frontend via the channel
//                 if let Err(err) = sender.send(message) {
//                     eprintln!("Error sending message to channel: {}", err);
//                 }

//                 // Acknowledge the message
//                 if let Err(err) = delivery.ack(BasicAckOptions::default()).await {
//                     eprintln!("Error acknowledging message: {}", err);
//                 }
//             }0

//         }
//     }).await;
// });

//     Ok("Connected and subscribed to queue".into())
// }

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_websocket::init())
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
        .invoke_handler(tauri::generate_handler![connect_and_consume])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
