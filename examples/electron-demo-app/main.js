const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const { readClipboard } = require('./lib/clipboard');
ipcMain.handle('clipboard:read', () => readClipboard());
function createWindow() {
  const win = new BrowserWindow({ width: 900, height: 700, webPreferences: { preload: path.join(__dirname, 'preload.js') } });
  win.loadFile('index.html');
}
app.whenReady().then(createWindow);
