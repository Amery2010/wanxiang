"use strict";
// Resolve public package exports in a source ZIP without requiring node_modules.
const { createRequire } = require("node:module");
const { resolve } = require("node:path");
module.exports = createRequire(resolve(__dirname, "../packages/runtime/dist/compat/package.json"));
