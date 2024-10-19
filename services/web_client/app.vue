<script setup lang="js">
import axios from 'axios';

const model = useState('model', () => null);
const dataset = useState('dataset', () => null);
const UPLOAD_FILES_ENDPOINT = "https://example.com/api/upload";
const DOWNLOAD_MODEL_ENDPOINT = (taskId) => `http://localhost:8000/job/${taskId}`;

function modelChange(e) {
  model.value = e.target.files[0];
}
function datasetChange(e) {
  dataset.value = e.target.files[0];
}

const submitForm = async () => {
  // form the body
  const form = new FormData();
  form.append('model', model.value); 
  form.append('dataset', dataset.value); 

  // get task
  const taskResponse = await axios.post(UPLOAD_FILES_ENDPOINT, form, {
    headers: {
      'Content-Type': 'multipart/form-data', 
    },
  });
  const taskId = (await response.json())["task_id"]

  // listen for the download URL, and download it once received
  const listenSource = new EventSource(DOWNLOAD_MODEL_ENDPOINT(taskId))
  listenSource.onmessage = (event) => {
    const url = JSON.parse(event.data).url;

    // auto download
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = "new-model.pt";
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);

    listenSource.close()
  }
};
</script>

<template>
  <div>
    <form @submit.prevent="submitForm">
      <label for="model">Choose a model pt file: </label>
      <input type="file" id="model" name="model" @change="modelChange" /><br>

      <label for="dataset">Choose a dataset json file: </label>
      <input type="file" id="dataset" name="dataset" @change="datasetChange" /><br>

      <input type="submit" value="Submit">
    </form>
  </div>
</template>
