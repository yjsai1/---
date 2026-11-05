import { createServer } from "node:http";
import { createReadStream, existsSync, statSync } from "node:fs";
import { resolve, join, extname } from "node:path";
import { Browser } from "./.taste-skill-cdp.mjs";
const root = resolve(".");
const MIME = { ".html": "text/html; charset=utf-8", ".png": "image/png", ".jpg": "image/jpeg", ".css": "text/css; charset=utf-8" };
const server = createServer((req, res) => {
  const f = resolve(join(root, decodeURIComponent(new URL(req.url, "http://x").pathname)));
  if (!f.startsWith(root) || !existsSync(f) || !statSync(f).isFile()) { res.writeHead(404); return res.end("no"); }
  res.writeHead(200, { "content-type": MIME[extname(f)] || "application/octet-stream" });
  createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;
const b = await Browser.launch();
for (const [file, width] of [["term-draw.html", 1180], ["term-inspect.html", 1180], ["term-install.html", 880]]) {
  const p = await b.newPage({ width, height: 800 });
  await p.goto(`${base}/shots/${file}`, { settleMs: 250 });
  const h = await p.eval(() => Math.ceil(document.querySelector(".panel").getBoundingClientRect().height));
  await p.setViewport({ width, height: Math.max(h, 200) });
  await new Promise((r) => setTimeout(r, 250));
  await p.screenshot({ path: `shots/${file.replace(".html", ".png")}`, format: "png", fullPage: true });
  console.log(file, h);
}
await b.close(); server.close();
