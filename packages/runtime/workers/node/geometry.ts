#!/usr/bin/env node
// Offline CPU geometry worker. Input JSON on stdin; one JSON response on stdout.
import * as THREE from "../../src/three.js";
import { GLTFExporter } from "../../src/three.js";
import fs from "node:fs";
interface Request {
  op: string;
  export_path?: string;
  params?: {
    outline?: [number, number][];
    holes?: [number, number][][];
    depth?: number;
    bevel?: number;
    segments?: number;
    profile?: [number, number][];
    points?: [number, number, number][];
    samples?: number;
    radius?: number;
    tube?: number;
    radial?: number;
  };
}
class NodeFileReader {
  result: ArrayBuffer | string | null = null;
  onloadend?: () => void;
  onload?: () => void;
  onerror?: (error: unknown) => void;

  readAsArrayBuffer(blob: Blob) {
    blob
      .arrayBuffer()
      .then((x) => {
        this.result = x;
        this.onloadend?.();
        this.onload?.();
      })
      .catch((e) => this.onerror?.(e));
  }
  readAsDataURL(blob: Blob) {
    blob
      .arrayBuffer()
      .then((x) => {
        this.result = `data:${blob.type};base64,${Buffer.from(x).toString("base64")}`;
        this.onloadend?.();
        this.onload?.();
      })
      .catch((e) => this.onerror?.(e));
  }
}
Object.defineProperty(globalThis, "FileReader", {
  value: globalThis.FileReader || NodeFileReader,
  configurable: true,
  writable: true,
});
try {
  const text = fs.readFileSync(0, "utf8");
  if (text.length > 4000000) throw Error("Input too large");
  const q = JSON.parse(text) as Request;
  const p = q.params || {};
  let g: THREE.BufferGeometry;
  if (q.op === "extrude") {
    const shape = new THREE.Shape();
    const points = p.outline || [
      [-1, 0],
      [1, 0],
      [1, 2],
      [-1, 2],
    ];
    shape.moveTo(...points[0]);
    points.slice(1).forEach((x) => shape.lineTo(...x));
    shape.closePath();
    for (const ring of p.holes || []) {
      const hole = new THREE.Path();
      hole.moveTo(...ring[0]);
      ring.slice(1).forEach((x) => hole.lineTo(...x));
      hole.closePath();
      shape.holes.push(hole);
    }
    g = new THREE.ExtrudeGeometry(shape, {
      depth: p.depth ?? 0.3,
      steps: 1,
      bevelEnabled: !!p.bevel,
      bevelSize: p.bevel ?? 0,
      bevelThickness: p.bevel ?? 0,
      bevelSegments: 2,
      curveSegments: Math.min(48, p.segments ?? 16),
    });
  } else if (q.op === "lathe") {
    if (!p.profile) throw Error("Lathe profile is required");
    g = new THREE.LatheGeometry(
      p.profile.map((x) => new THREE.Vector2(...x)),
      Math.min(256, p.segments ?? 32),
    );
  } else if (q.op === "tube") {
    if (!p.points) throw Error("Tube points are required");
    g = new THREE.TubeGeometry(
      new THREE.CatmullRomCurve3(p.points.map((x) => new THREE.Vector3(...x))),
      Math.min(256, p.samples ?? 32),
      p.radius ?? 0.1,
      Math.min(64, p.segments ?? 10),
      false,
    );
  } else if (q.op === "torus")
    g = new THREE.TorusGeometry(
      p.radius ?? 1,
      p.tube ?? 0.12,
      Math.min(32, p.radial ?? 12),
      Math.min(128, p.segments ?? 48),
    );
  else throw Error("Unsupported worker operator");
  g.computeVertexNormals();
  if (g.getAttribute("position").count > 1000000)
    throw Error("Vertex budget exceeded");
  const out: {
    status: string;
    version: string;
    positions: number[];
    normals: number[];
    uv: number[];
    indices: number[];
    exported?: string;
  } = {
    status: "ok",
    version: THREE.REVISION,
    positions: Array.from(g.attributes.position.array),
    normals: Array.from(g.attributes.normal.array),
    uv: Array.from(g.attributes.uv.array),
    indices: g.index
      ? Array.from(g.index.array)
      : Array.from({ length: g.attributes.position.count }, (_, i) => i),
  };
  if (q.export_path) {
    const scene = new THREE.Scene();
    const mesh = new THREE.Mesh(
      g,
      new THREE.MeshStandardMaterial({ color: 0x9da68d, roughness: 0.7 }),
    );
    mesh.name = "node_worker_geometry";
    scene.add(mesh);
    const data = await new GLTFExporter().parseAsync(scene, { binary: true });
    fs.writeFileSync(q.export_path, Buffer.from(data as ArrayBuffer));
    out.exported = q.export_path;
  }
  process.stdout.write(JSON.stringify(out));
} catch (e) {
  process.stdout.write(
    JSON.stringify({
      status: "failed",
      error: String(e instanceof Error ? e.stack || e.message : e),
    }),
  );
  process.exitCode = 5;
}
