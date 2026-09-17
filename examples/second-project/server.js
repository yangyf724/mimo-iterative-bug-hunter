#!/usr/bin/env node
// Zero-dependency static server for the Phase 3 second acceptance project.
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "public");
const PORT = Number(process.env.PORT || 5174);

const ROUTES = {
  "/": "index.html",
  "/shop": "shop.html",
  "/contact": "contact.html",
};

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
};

function send(res, status, body, type) {
  res.writeHead(status, { "Content-Type": type || "text/plain; charset=utf-8" });
  res.end(body);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://127.0.0.1:${PORT}`);
  let pathname = url.pathname;
  if (pathname.length > 1) pathname = pathname.replace(/\/$/, "");

  const file = ROUTES[pathname];
  if (file) {
    const html = fs.readFileSync(path.join(ROOT, file), "utf8");
    return send(res, 200, html, MIME[".html"]);
  }

  const asset = path.join(ROOT, pathname.replace(/^\//, ""));
  if (asset.startsWith(ROOT) && fs.existsSync(asset) && fs.statSync(asset).isFile()) {
    const ext = path.extname(asset);
    return send(res, 200, fs.readFileSync(asset), MIME[ext] || "application/octet-stream");
  }

  send(res, 404, "Not Found");
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`second-project at http://127.0.0.1:${PORT}`);
});
