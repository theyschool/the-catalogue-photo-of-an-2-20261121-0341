// AQUASHELLA — catalogue photo of an impossible gadget.
// The entry image (entry.png, rendered by build_image.py with PIL) is
// committed beside this file; at grade time we simply copy it to the
// output directory the harness names.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
console.log("entry.png written to", outDir);
