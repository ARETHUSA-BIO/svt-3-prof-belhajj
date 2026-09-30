import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const types = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8", ".webmanifest": "application/manifest+json; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg" };
const server = createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
    const target = path.resolve(root, `.${pathname}`);
    if (target !== root && !target.startsWith(root + path.sep)) throw new Error("Path outside project");
    const info = await stat(target);
    const file = info.isDirectory() ? path.join(target, "index.html") : target;
    const body = await readFile(file);
    res.writeHead(200, { "Content-Type": types[path.extname(file)] || "application/octet-stream", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" });
    res.end(body);
  } catch {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Not found");
  }
});
const port = Number(process.env.PORT || 4173);
server.listen(port, "0.0.0.0", () => console.log(`SVT 3 prêt sur http://localhost:${port}`));
