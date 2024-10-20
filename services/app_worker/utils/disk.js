const invoke = window.__TAURI__.core.invoke;

const { readTextFile, writeTextFile, readFile, writeFile, BaseDirectory } = window.__TAURI__.fs;

export const storeKerasModel = (fileName, jsonContent) => writeTextFile(`${fileName}.json`, jsonContent, { baseDir: BaseDirectory.Document });
export const readKerasModel = (fileName) => readTextFile(`${fileName}.json`, { baseDir: BaseDirectory.Document });
export const storeTrainedModel = (fileName, binArray) => writeFile(`${fileName}.bin`, binArray, { baseDir: BaseDirectory.Document });
export const readTrainedModel = (fileName) => readFile(`${fileName}.bin`, { baseDir: BaseDirectory.Document });
