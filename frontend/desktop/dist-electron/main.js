import { BrowserWindow as e, Menu as t, app as n } from "electron";
import r from "node:path";
//#region electron/main.ts
var i = import.meta.dirname;
process.env.DIST = r.join(i, "../dist"), process.env.VITE_PUBLIC = n.isPackaged ? process.env.DIST : r.join(process.env.DIST, "../public");
var a;
function o() {
	a = new e({
		icon: r.join(process.env.VITE_PUBLIC, "electron-vite.svg"),
		webPreferences: { preload: r.join(i, "preload.mjs") },
		width: 1200,
		height: 800
	}), a.webContents.on("did-finish-load", () => {
		a?.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
	}), process.env.VITE_DEV_SERVER_URL ? a.loadURL(process.env.VITE_DEV_SERVER_URL) : a.loadFile(r.join(process.env.DIST, "index.html"));
}
n.on("window-all-closed", () => {
	process.platform !== "darwin" && (n.quit(), a = null);
}), n.on("activate", () => {
	e.getAllWindows().length === 0 && o();
}), n.whenReady().then(() => {
	o(), t.setApplicationMenu(null);
});
//#endregion
export {};
