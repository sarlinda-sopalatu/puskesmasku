import fs from 'node:fs/promises';
const DOC = 'docs/MAKALAH_PuskesmasKu.md';
let doc = await fs.readFile(DOC, 'utf8');
const s4 = (await fs.readFile('docs/_section4.md', 'utf8')).trimEnd();
const s5 = (await fs.readFile('docs/_section5.md', 'utf8')).trimEnd();
const s6 = (await fs.readFile('docs/_section6.md', 'utf8')).trimEnd();
const before = doc.length;
let n = 0;
doc = doc.replace(/### 4\.2 Use Case Diagram \(Tekstual\)[\s\S]*?(?=## 5\. ACTIVITY DIAGRAM)/, () => { n++; return s4 + '\n\n'; });
doc = doc.replace(/## 5\. ACTIVITY DIAGRAM[\s\S]*?(?=## 6\. ENTITY RELATIONSHIP DIAGRAM \(ERD\))/, () => { n++; return s5 + '\n\n'; });
doc = doc.replace(/### 6\.3 ERD Diagram \(Tekstual\)[\s\S]*?(?=## 7\. PERENCANAAN SPRINT 1.4)/, () => { n++; return s6 + '\n\n'; });
if (n !== 3) throw new Error('Jumlah penggantian tidak sesuai: ' + n);
for (const marker of ['Gambar 4.1', 'Gambar 5.1', 'Gambar 6.1']) {
  if (!doc.includes(marker)) throw new Error('Sisipan gagal: ' + marker);
}
await fs.writeFile(DOC, doc, 'utf8');
console.log(`Selesai. ${before} -> ${doc.length} karakter, ${n} bagian diganti`);
