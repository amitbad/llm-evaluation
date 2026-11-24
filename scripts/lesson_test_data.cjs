const {existsSync, readFileSync} = require("node:fs");
const {resolve} = require("node:path");

const root = resolve(__dirname, "..");
const curriculum = readFileSync(resolve(root, "MASTER_CURRICULUM.md"), "utf8");

// Keep curriculum order and include only topics with an authored source.
const authoredLessonIds = [...curriculum.matchAll(/^##### (M\d{2}-T\d{2}) — /gm)]
  .map(([, id]) => id)
  .filter(id => existsSync(resolve(root, "docs/lessons", id.toLowerCase() + ".md")));

module.exports = {authoredLessonIds};
