let electron = require("electron");
//#region electron/preload.ts
electron.contextBridge.exposeInMainWorld("ipcRenderer", {
	on(...args) {
		const [channel, listener] = args;
		return electron.ipcRenderer.on(channel, (event, ...args) => listener(event, ...args));
	},
	off(...args) {
		const [channel, ...rest] = args;
		return electron.ipcRenderer.off(channel, ...rest);
	},
	send(...args) {
		const [channel, ...rest] = args;
		return electron.ipcRenderer.send(channel, ...rest);
	},
	invoke(...args) {
		const [channel, ...rest] = args;
		return electron.ipcRenderer.invoke(channel, ...rest);
	}
});
//#endregion
