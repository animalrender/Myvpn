const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('api', { readClipboard: () => ipcRenderer.invoke('clipboard:read') });
