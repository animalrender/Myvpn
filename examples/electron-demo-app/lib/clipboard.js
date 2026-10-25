const { clipboard } = require('electron');
function readClipboard() { return { text: clipboard.readText(), html: clipboard.readHTML() }; }
module.exports = { readClipboard };
