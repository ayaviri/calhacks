<script setup lang="js">
import axios from 'axios';

const model = useState('model', () => null);
const dataset = useState('dataset', () => null);
const UPLOAD_FILES_ENDPOINT = "http://localhost:8000/task";
const DOWNLOAD_MODEL_ENDPOINT = (taskId) => `http://localhost:8000/task/${taskId}`;

function modelChange(e) {
  model.value = e.target.files[0];
}
function datasetChange(e) {
  dataset.value = e.target.value;
}

const submitForm = async () => {
  // form the body
  const form = new FormData();
  form.append('model', model.value); 
  form.append('dataset_name', dataset.value);
  
  // get task
  const taskResponse = await axios.post(UPLOAD_FILES_ENDPOINT, form, {
    headers: {
      'Content-Type': 'multipart/form-data', 
    },
  });
  console.log(taskResponse)
  const taskId = taskResponse.data.task_id

  // // listen for the download URL, and download it once received
  const listenSource = new EventSource(DOWNLOAD_MODEL_ENDPOINT(taskId))
  listenSource.onmessage = (event) => {
    const url = JSON.parse(event.data).url;
    alert(url);
    // auto download
    // const anchor = document.createElement('a');
    // anchor.href = url;
    // anchor.download = "new-model.keras";
    // document.body.appendChild(anchor);
    // anchor.click();
    // document.body.removeChild(anchor);

    listenSource.close()
  }
};
</script>

<template>
  <div>
    <form @submit.prevent="submitForm">
      <label for="model">Choose a model Keras file: </label>
      <input type="file" id="model" name="model" @change="modelChange" /><br>

      <label for="dataset_name">Type a dataset name: </label>
      <input type="text" id="dataset_name" name="dataset_name" @change="datasetChange" /><br>

      <input type="submit" value="Submit">
    </form>
  </div>
</template>
