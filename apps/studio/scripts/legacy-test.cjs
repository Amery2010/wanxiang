"use strict";
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const suites = {
  studio35: { name: "studio-pure", report: "js-studio-pure.json" },
  scene_document: { name: "scene-document" },
  subset37: { name: "subset37-control-provenance" },
  sweep39: { name: "sweep39" },
  game410: { name: "game410", report: "js-game410.json" },
};

exports.run = function run(name) {
  const suite = suites[name];
  if (!suite) throw new Error("Unknown legacy test suite");
  const web = path.resolve(__dirname, "..");
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "wanxiang-vitest-"));
  let passed = 0;
  let failed = 1;
  try {
    const output = path.join(temporary, "results.json");
    const result = spawnSync(
      process.execPath,
      [
        path.join(
          path.dirname(require.resolve("vitest/package.json")),
          "vitest.mjs",
        ),
        "run",
        "--config",
        path.join(web, "vitest.config.mts"),
        "--project",
        "node",
        `tests/legacy/${name}.test.mjs`,
        "--reporter=json",
        "--outputFile",
        output,
      ],
      { cwd: web, encoding: "utf8", timeout: 55000 },
    );
    if (result.stdout) process.stdout.write(result.stdout);
    if (result.stderr) process.stderr.write(result.stderr);
    if (result.error) throw result.error;
    if (!fs.existsSync(output))
      throw new Error(
        "Vitest report unavailable. Install frontend dependencies with pnpm install.",
      );
    const json = JSON.parse(fs.readFileSync(output, "utf8"));
    passed = json.numPassedTests;
    failed =
      json.numFailedTests +
      (result.status !== 0 && json.numFailedTests === 0 ? 1 : 0);
    if (suite.report) {
      const directory = path.resolve(web, "../../generated/verification");
      const results = json.testResults.flatMap((file) =>
        file.assertionResults.map((test) => ({
          name: test.title,
          passed: test.status === "passed",
          ...(test.failureMessages?.length
            ? { error: test.failureMessages.join("\n") }
            : {}),
        })),
      );
      fs.mkdirSync(directory, { recursive: true });
      fs.writeFileSync(
        path.join(directory, suite.report),
        JSON.stringify({ suite: suite.name, passed, failed, results }, null, 2),
      );
    }
  } catch (error) {
    console.error(error.message);
    failed = Math.max(1, failed);
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
    console.log(JSON.stringify({ suite: suite.name, passed, failed }));
    process.exitCode = failed ? 1 : 0;
  }
};
