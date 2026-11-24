import fs from 'node:fs/promises';
import path from 'node:path';

const SRC = path.resolve('docs/diagrams/src');
const OUT = path.resolve('docs/diagrams');
await fs.mkdir(OUT, { recursive: true });

const files = (await fs.readdir(SRC)).filter((f) => f.endsWith('.puml')).sort();
const only = process.argv.slice(2);
const targets = only.length ? files.filter((f) => only.some((o) => f.includes(o))) : files;

for (const file of targets) {
  const src = await fs.readFile(path.join(SRC, file), 'utf8');
  const base = file.replace(/\.puml$/, '');
  for (const format of ['svg', 'png']) {
    const res = await fetch(`https://kroki.io/plantuml/${format}`, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: src
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(`${file} -> ${format}: HTTP ${res.status}\n${detail}`);
    }
    const buf = Buffer.from(await res.arrayBuffer());
    const dest = path.join(OUT, `${base}.${format}`);
    await fs.writeFile(dest, buf);
    console.log(`OK  ${path.relative(process.cwd(), dest)}  ${(buf.length / 1024).toFixed(1)} KB`);
  }
}
