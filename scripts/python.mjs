import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { delimiter, resolve } from "node:path";

export const root = resolve(import.meta.dirname, "..");

export function pythonExecutable() {
  const local = resolve(root, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
  if (process.env.WX_PYTHON) return process.env.WX_PYTHON;
  if (existsSync(local)) return local;
  return process.platform === "win32" ? "python" : "python3";
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(import.meta.filename)) {
  const child = spawn(pythonExecutable(), process.argv.slice(2), {
    cwd: root,
    stdio: "inherit",
    env: {
      ...process.env,
      PYTHONDONTWRITEBYTECODE: "1",
      PYTHONPATH: [resolve(root, "packages/kit/src"), process.env.PYTHONPATH].filter(Boolean).join(delimiter),
    },
  });
  for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => child.kill(signal));
  child.on("error", (error) => { console.error(error.message); process.exitCode = 1; });
  child.on("exit", (code, signal) => { process.exitCode = code ?? (signal ? 1 : 0); });
}
