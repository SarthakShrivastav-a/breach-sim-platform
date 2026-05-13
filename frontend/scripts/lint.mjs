import fs from "node:fs";
import path from "node:path";

const srcDir = path.resolve("src");
const files = fs.readdirSync(srcDir).filter((file) => /\.(js|jsx)$/.test(file));
const failures = [];

for (const file of files) {
  const content = fs.readFileSync(path.join(srcDir, file), "utf8");
  if (content.includes("console.log(")) {
    failures.push(`${file}: console.log is not allowed`);
  }
  if (content.includes("TODO")) {
    failures.push(`${file}: TODO markers must be resolved`);
  }
}

if (failures.length > 0) {
  process.stderr.write(`${failures.join("\n")}\n`);
  process.exit(1);
}

process.stdout.write(`Linted ${files.length} frontend source files\n`);

