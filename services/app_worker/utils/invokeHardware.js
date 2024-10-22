const invoke = window.__TAURI__.core.invoke;

export const getGraphicsName  = async () => (await invoke('plugin:swift|graphics', { payload: {} })).value;