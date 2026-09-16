#!/usr/bin/env node
/**
 * Zero-dependency static server for acceptance demo.
 * Routes: GET / and GET /about (also /about/).
 */
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "public");
const PORT = Number(process.env.PORT || 5173);
const HOST = process.env.HOST || "127.0.0.1";

const PAGES = {
  "/": "index.html",
  "/about": "about.html",
  "/about/": "about.html",
};

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
};

function send(res, status, body, type) {
  res.writeHead(status, {
    "Content-Type": type || "text/plain; charset=utf-8",
    "Cache-Control": "no-store",
  });
  res.end(body);
}

const server = http.createServer((req, res) => {
  const url = (req.url || "/").split("?")[0];
  if (PAGES[url]) {
    const file = path.join(ROOT, PAGES[url]);
    fs.readFile(file, (err, data) => {
      if (err) {
        send(res, 500, "missing page: " + PAGES[url]);
        return;
      }
      send(res, 200, data, TYPES[".html"]);
    });
    return;
  }
  if (url.startsWith("/assets/")) {
    const file = path.join(ROOT, url);
    fs.readFile(file, (err, data) => {
      if (err) {
        send(res, 404, "not found");
        return;
      }
      send(res, 200, data, TYPES[path.extname(file)] || "application/octet-stream");
    });
    return;
  }
  send(res, 404, "not found: " + url);
});

server.listen(PORT, HOST, () => {
  console.log(`acceptance-demo listening on http://${HOST}:${PORT}`);
});
