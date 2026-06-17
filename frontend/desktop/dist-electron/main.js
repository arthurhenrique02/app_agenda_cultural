import { BrowserWindow, Menu, app } from "electron";
import path from "node:path";
//#region electron/main.ts
var __dirname = import.meta.dirname;
process.env.DIST = path.join(__dirname, "../dist");
process.env.VITE_PUBLIC = app.isPackaged ? process.env.DIST : path.join(process.env.DIST, "../public");
var win;
function createWindow() {
	win = new BrowserWindow({
		icon: path.join(process.env.VITE_PUBLIC, "electron-vite.svg"),
		webPreferences: { preload: path.join(__dirname, "preload.mjs") },
		width: 1200,
		height: 800
	});
	win.webContents.on("did-finish-load", () => {
		win?.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
	});
	if (process.env.VITE_DEV_SERVER_URL) win.loadURL(process.env.VITE_DEV_SERVER_URL);
	else win.loadFile(path.join(process.env.DIST, "index.html"));
}
app.on("window-all-closed", () => {
	if (process.platform !== "darwin") {
		app.quit();
		win = null;
	}
});
app.on("activate", () => {
	if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
app.whenReady().then(() => {
	createWindow();
	Menu.setApplicationMenu(null);
});
//#endregion
export {};
