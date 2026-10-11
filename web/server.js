// Optional local launcher. No packages, installation, or remote service required.
import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(fileURLToPath(new URL('../', import.meta.url)));
const types = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.jpg':'image/jpeg','.png':'image/png','.ttf':'font/ttf','.mp4':'video/mp4','.mp3':'audio/mpeg'};
const server = http.createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    const file = path.resolve(root, '.' + (pathname === '/' ? '/web/index.html' : pathname.endsWith('/') ? pathname + 'index.html' : pathname));
    if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
    const info = await stat(file);
    if (!info.isFile()) { res.writeHead(404).end(); return; }
    const data = await readFile(file);
    const match = /^bytes=(\d+)-(\d*)$/.exec(req.headers.range || '');
    const headers = {'Content-Type': types[path.extname(file)] || 'application/octet-stream', 'Accept-Ranges':'bytes','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'};
    if (match) {
      const start = Number(match[1]); const end = Math.min(match[2] ? Number(match[2]) : data.length - 1, data.length - 1);
      if (start > end || start >= data.length) { res.writeHead(416, {'Content-Range':`bytes */${data.length}`}).end(); return; }
      res.writeHead(206, {...headers, 'Content-Range':`bytes ${start}-${end}/${data.length}`, 'Content-Length':end-start+1});
      res.end(req.method === 'HEAD' ? undefined : data.subarray(start,end+1));
    } else { res.writeHead(200, {...headers,'Content-Length':data.length}); res.end(req.method === 'HEAD' ? undefined : data); }
  } catch { res.writeHead(404).end('Not found'); }
});
server.listen(Number(process.env.PORT || 8765), '127.0.0.1', () => console.log(`Experiment: http://127.0.0.1:${server.address().port}/web/`));
