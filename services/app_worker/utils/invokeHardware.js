const invoke = window.__TAURI__.core.invoke;

export const getGraphicsName  = async (_) => (await invoke('plugin:swift|graphics', { payload: {} })).value;