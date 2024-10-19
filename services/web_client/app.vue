<script setup lang="js">
import axios from 'axios';

const model = useState('model', () => null);
const dataset = useState('dataset', () => null);

function modelChange(e) {
  model.value = e.target.files[0];
}
function datasetChange(e) {
  dataset.value = e.target.files[0];
}

const submitForm = async () => {
  const form = new FormData();
  form.append('model', model.value); 
  form.append('dataset', dataset.value); 

  const response = await axios.post('https://example.com/api/upload', form, {
    headers: {
      'Content-Type': 'multipart/form-data', 
    },
  });
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
