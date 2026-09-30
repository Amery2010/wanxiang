import * as Guards from "./three-guards.js";
/* Shared declarative runtime: offline geometry -> scene -> actual GLB.
 * Uses whitelisted data fields, bounded repetitions and explicit socket frames.
 */
import * as T from "./three.js";
import { createContracts, type Contracts } from "./contracts.js";
import Geometry from "./geometry.js";
import Styles from "./styles.js";
import Semantic from "./semantic.js";
import Mechanics from "./mechanics.js";
import type {
  RuntimeLibraryData,
  RuntimeData,
  RuntimeSpec,
  RuntimeInstance,
  Parameters,
  Part,
  MaterialRow,
  BomEntry,
  BuildReport,
} from "./types.js";
import type { Socket } from "./contract-types.js";
import type { RigBone } from "./geometry-types.js";
const V = (a: number[] = [0, 0, 0]) => new T.Vector3(...a),
  copy = <X>(x: X): X => JSON.parse(JSON.stringify(x)),
  rad = (x: number) => (x * Math.PI) / 180;
export type BoundSocket = Omit<Socket, "node" | "id"> & {
  id: string;
  node: T.Object3D;
  position: number[];
  normal: number[];
  tangent: number[];
  interface?: string;
};
interface BuiltTree {
  root: T.Group;
  nodes: Map<string, T.Object3D>;
  sockets: Map<string, BoundSocket>;
  bom: BomEntry[];
}
export interface LibraryBuild extends BuiltTree {
  report: BuildReport;
  promises: Promise<void>[];
  spec: RuntimeSpec;
}
export interface BuildOptions {
  noTextures?: boolean;
}
interface BuildContext {
  geos: Map<string, T.BufferGeometry>;
  mats: Map<string, T.MeshStandardMaterial>;
  promises: Promise<void>[];
  nodes: number;
  noTextures: boolean;
  partCount: number;
  triangles: number;
  skeletons: T.Skeleton[];
  split: Map<string, ReturnType<typeof Geometry.split>>;
}

const safe = (x: unknown): x is string =>
  typeof x === "string" &&
  /^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$/.test(x) &&
  !x.includes("..");
function fail(m: string): never {
  throw Error("RECIPE_INVALID: " + m);
}
function vec(a: unknown, positive = false): number[] {
  if (
    !Array.isArray(a) ||
    a.length !== 3 ||
    a.some((x) => !Number.isFinite(x) || (positive && (x <= 0 || x > 100)))
  )
    fail("Invalid vector");
  return a as number[];
}
export function matrix(
  p: number[] = [0, 0, 0],
  r: number[] = [0, 0, 0],
  s: number[] = [1, 1, 1],
) {
  vec(p);
  vec(r);
  vec(s, true);
  return new T.Matrix4().compose(
    V(p),
    new T.Quaternion().setFromEuler(
      new T.Euler(rad(r[0]), rad(r[1]), rad(r[2]), "ZYX"),
    ),
    V(s),
  );
}
export function frame(
  s: Pick<Socket, "normal" | "axis" | "tangent" | "position">,
) {
  const z = V(vec(s.normal || s.axis)).normalize(),
    x = V(vec(s.tangent || [1, 0, 0]));
  x.addScaledVector(z, -x.dot(z));
  if (x.lengthSq() < 1e-12 || z.lengthSq() < 0.1)
    fail("Connector frame degeneracy");
  x.normalize();
  return new T.Matrix4()
    .makeBasis(x, V().crossVectors(z, x), z)
    .setPosition(V(vec(s.position)));
}
export function expand(
  items: RuntimeInstance[] | undefined,
): RuntimeInstance[] {
  if (!Array.isArray(items) || items.length > 2500) fail("Instance budget");
  const out: RuntimeInstance[] = [];
  for (const original of items!) {
    const it = copy(original),
      enabled = it.enabled ?? true,
      r = it.repeat;
    if (typeof enabled !== "boolean")
      fail("Instance enabled must resolve to boolean");
    if (!enabled) continue;
    delete it.enabled;
    delete it.repeat;
    if (!r) {
      out.push(it);
      continue;
    }
    if (it.attach) fail("Repeated socket mate is ambiguous");
    let coords: [number[], number[]][] = [];
    if (!r.type || r.type === "linear") {
      const n = r.count ?? 1;
      if (!Number.isInteger(n) || n < 1 || n > 512) fail("Repeat count");
      const step = vec(r.step || [1, 0, 0]);
      coords = Array.from({ length: n }, (_, i) => [
        step.map((x) => x * i),
        [0, 0, 0],
      ]);
    } else if (r.type === "grid") {
      const c = r.count || [1, 1, 1],
        s = vec(r.step || [1, 1, 1]);
      if (
        c.length !== 3 ||
        c.some((x) => !Number.isInteger(x) || x < 1 || x > 128) ||
        c.reduce((a, b) => a * b, 1) > 2048
      )
        fail("Grid budget");
      for (let y = 0; y < c[1]; y++)
        for (let z = 0; z < c[2]; z++)
          for (let x = 0; x < c[0]; x++)
            coords.push([
              [x * s[0], y * s[1], z * s[2]],
              [0, 0, 0],
            ]);
    } else if (r.type === "radial") {
      const n = r.count || 8,
        rr = r.radius ?? 1,
        start = r.start || 0;
      if (
        !Number.isInteger(n) ||
        n < 1 ||
        n > 512 ||
        !Number.isFinite(rr) ||
        rr < 0 ||
        rr > 100
      )
        fail("Radial budget");
      coords = Array.from({ length: n }, (_, i) => {
        const a = start + (i * 360) / n;
        return [
          [rr * Math.sin(rad(a)), 0, rr * Math.cos(rad(a))],
          [0, r.orient === false ? 0 : a, 0],
        ];
      });
    } else fail("Unknown repeat");
    coords.forEach(([p, r], i) =>
      out.push({
        ...copy(it),
        id: it.id + "_" + String(i).padStart(3, "0"),
        position: p.map((v, j) => v + (it.position || [0, 0, 0])[j]),
        rotation: r.map((v, j) => v + (it.rotation || [0, 0, 0])[j]),
      }),
    );
  }
  if (out.length > 2500) fail("Expanded instance budget");
  return out;
}
const imageCache = new Map<string, Promise<HTMLImageElement>>();
function image(url: string): Promise<HTMLImageElement> {
  if (!/^data:image\/(png|jpeg|webp);base64,/.test(url))
    return Promise.reject(
      Error("Only embedded offline image data is accepted"),
    );
  if (!imageCache.has(url)) {
    while (imageCache.size >= 48)
      imageCache.delete(imageCache.keys().next().value!);
    const promise = new Promise<HTMLImageElement>((ok, bad) => {
      const i = new Image();
      i.onload = () => ok(i);
      i.onerror = () => bad(Error("Offline material decode failed"));
      i.src = url;
    });
    imageCache.set(url, promise);
    promise.catch(() => imageCache.delete(url));
  }
  return imageCache.get(url)!;
}
export class Library {
  readonly contracts: Contracts;
  readonly retired: Map<string, { kind: string; id: string }>;
  readonly parts: Map<string, Part>;
  readonly templates: Map<string, RuntimeSpec>;
  readonly materials: Map<string, MaterialRow>;
  readonly motions: NonNullable<RuntimeData["motions"]>;
  constructor(data: RuntimeLibraryData) {
    this.contracts = createContracts(data.interfaces);
    this.retired = new Map(
      (data.retired?.entries || []).map((r) => [r.kind + ":" + r.id, r]),
    );
    this.parts = new Map(Object.entries(data.parts || {}));
    this.templates = new Map(Object.entries(data.assemblies || {}));
    for (const [old, id] of Object.entries(data.aliases || {}))
      if (this.templates.has(id))
        this.templates.set(old, this.templates.get(id)!);
    this.materials = new Map((data.materials || []).map((m) => [m.id, m]));
    this.motions = data.motions || {};
  }
  buildSync(
    spec: RuntimeSpec,
    { noTextures = false }: BuildOptions = {},
  ): LibraryBuild {
    if (!spec || !safe(spec.id || spec.part))
      fail("A stable safe ID is required");
    if (
      spec.max_triangles !== undefined &&
      (!Number.isFinite(spec.max_triangles) ||
        spec.max_triangles < 1 ||
        spec.max_triangles > 500000)
    )
      fail("Invalid triangle budget");
    const style = Styles.resolve(spec.style || "lowpoly").id;
    const ctx: BuildContext = {
      geos: new Map(),
      mats: new Map(),
      promises: [],
      nodes: 0,
      noTextures,
      partCount: 0,
      triangles: 0,
      skeletons: [],
      split: new Map(),
    };
    const makeMat = (id: string): T.MeshStandardMaterial => {
      if (ctx.mats.has(id)) return ctx.mats.get(id)!;
      let src = this.materials.get(id);
      if (!src && id.startsWith("mat.") && /--(toon|voxel)$/.test(id)) {
        const [raw, derived] = id.split("--"),
          base = this.materials.get(raw);
        if (base) {
          src = copy(base);
          src.id = id;
          src.record = {
            ...src.record,
            id,
            extras: {
              ...src.record.extras,
              wxStyle: derived,
              derived_from: raw,
            },
          };
          if (derived === "voxel") {
            const pixel = this.materials.get("mat.voxel_chart");
            if (!pixel) fail("Material not registered: mat.voxel_chart");
            src = {
              ...src,
              preview: pixel.preview,
              record: {
                ...src.record,
                channels: pixel.record.channels,
                sampler: pixel.record.sampler,
                kind: "stylized",
                alphaMode: "OPAQUE",
                baseColorFactor: [1, 1, 1, 1],
                roughnessFactor: 1,
                metallicFactor: 0,
              },
            };
          }
        }
      }
      if (!src) fail("Material not registered: " + id);
      const r = src.record,
        fac = r.baseColorFactor || [1, 1, 1, 1],
        m = new T.MeshStandardMaterial({
          color: new T.Color().setRGB(fac[0], fac[1], fac[2]),
          roughness: r.roughnessFactor ?? 0.8,
          metalness: r.metallicFactor ?? 0,
          emissive: new T.Color().setRGB(
            ...((r.emissiveFactor || [0, 0, 0]) as [number, number, number]),
          ),
          opacity: fac[3],
          transparent: r.alphaMode === "BLEND",
          alphaTest: r.alphaMode === "MASK" ? (r.alphaCutoff ?? 0.4) : 0,
          side: r.doubleSided ? T.DoubleSide : T.FrontSide,
        });
      m.name = id;
      m.userData = {
        source: r.source,
        limitations: r.limitations,
        wxStyle: r.extras?.wxStyle || style,
      };
      Styles.shader(m, m.userData.wxStyle);
      if (src.preview && r.kind !== "palette" && !ctx.noTextures) {
        const tex = new T.Texture();
        tex.colorSpace = T.SRGBColorSpace;
        tex.flipY = false;
        tex.wrapS =
          r.sampler?.wrapS === "REPEAT"
            ? T.RepeatWrapping
            : T.ClampToEdgeWrapping;
        tex.wrapT =
          r.sampler?.wrapT === "REPEAT"
            ? T.RepeatWrapping
            : T.ClampToEdgeWrapping;
        tex.magFilter =
          r.sampler?.magFilter === 9728 ? T.NearestFilter : T.LinearFilter;
        tex.minFilter =
          r.sampler?.minFilter === 9728
            ? T.NearestFilter
            : T.LinearMipmapLinearFilter;
        tex.generateMipmaps = tex.minFilter !== T.NearestFilter;
        m.map = tex;
        ctx.promises.push(
          image(src.preview).then((im) => {
            tex.image = im;
            tex.needsUpdate = true;
            m.needsUpdate = true;
          }),
        );
        if (src.emissive) {
          const e = new T.Texture();
          e.colorSpace = T.SRGBColorSpace;
          e.flipY = false;
          m.emissiveMap = e;
          ctx.promises.push(
            image(src.emissive).then((im) => {
              e.image = im;
              e.needsUpdate = true;
            }),
          );
        }
      }
      ctx.mats.set(id, m);
      return m;
    };
    const makePart = (
      id: string,
      style: string,
      params: Parameters = {},
      override?: string,
    ): BuiltTree => {
      if (this.retired.has("part:" + id))
        throw Error(
          "ASSET_RETIRED: " +
            id +
            "; open the migration ledger and re-author with a current part.",
        );
      const d = this.parts.get(id);
      if (!d) fail("Unknown part " + id);
      const key = JSON.stringify([id, style, params]);
      let g = ctx.geos.get(key);
      if (!g) {
        g = Geometry.part(d, style, params, this.parts, this.contracts);
        ctx.geos.set(key, g);
      }
      ctx.triangles += (g.index?.count ?? g.attributes.position.count) / 3;
      if (ctx.triangles > Math.min(500000, spec.max_triangles || 400000))
        fail("Expanded triangle budget");
      style = Styles.resolve(style).id;
      const defaultMat = d.material || "mat.matte",
        styled = style === "lowpoly" ? defaultMat : defaultMat + "--" + style;
      const mat =
        override ||
        (defaultMat.startsWith("mat.") || this.materials.has(styled)
          ? styled
          : defaultMat);
      const root = new T.Group();
      root.name = "root";
      root.userData = {
        wx_role: "part_root",
        part_id: id,
        wxLevel: d.level || 1,
        wxComponents: g.userData.anatomy?.dependencies || [],
      };
      const nodes = new Map<string, T.Object3D>([["root", root]]),
        rig = (g.userData.rig || []) as RigBone[];
      let skeleton: T.Skeleton | null = null;
      if (rig.length) {
        const by = new Map<string, T.Bone>();
        for (const b of rig) {
          const bone = new T.Bone();
          bone.name = "rig." + b.name;
          bone.userData = { wx_role: "bone", part_id: id };
          by.set(b.name, bone);
          nodes.set(bone.name, bone);
        }
        for (const b of rig) {
          const bone = by.get(b.name)!;
          bone.position.fromArray(b.position);
          if (b.parent) {
            bone.position.sub(
              V(rig.find((x) => x.name === b.parent)!.position),
            );
            by.get(b.parent)!.add(bone);
          } else root.add(bone);
        }
        skeleton = new T.Skeleton(rig.map((b) => by.get(b.name)!));
        ctx.skeletons.push(skeleton);
      }
      if (!ctx.split) ctx.split = new Map();
      let pieces = ctx.split.get(key);
      if (!pieces) {
        pieces = Geometry.split(g);
        ctx.split.set(key, pieces);
        pieces.forEach((p, i) => {
          if (p.geometry !== g) ctx.geos.set(key + "|" + i, p.geometry);
        });
      }
      for (const [i, piece] of pieces.entries()) {
        let materialId = override || piece.role || mat;
        if (
          !override &&
          style !== "lowpoly" &&
          !/--(toon|voxel)$/.test(materialId) &&
          (materialId.startsWith("mat.") ||
            this.materials.has(materialId + "--" + style))
        )
          materialId += "--" + style;
        const material = makeMat(materialId);
        material.vertexColors = !!piece.geometry.attributes.color;
        const mesh = skeleton
          ? new T.SkinnedMesh(piece.geometry, material)
          : new T.Mesh(piece.geometry, material);
        if (skeleton && Guards.isSkinnedMesh(mesh)) mesh.skeleton = skeleton;
        mesh.name = i === 0 ? "surface" : "surface_" + i;
        mesh.userData = {
          wx_role: d.category + "_part",
          part_id: id,
          materialRole: piece.role || "default",
          wxAnatomy: g.userData.anatomy,
        };
        root.add(mesh);
        nodes.set(mesh.name, mesh);
      }
      g.computeBoundingBox();
      const b = g.boundingBox!,
        mid = b.getCenter(new T.Vector3());
      const con = (
        id: string,
        pos: number[],
        normal = [0, 1, 0],
        tangent = [1, 0, 0],
      ): Socket => ({
        id,
        position: pos,
        normal,
        tangent,
        interface: "surface",
      });
      let sockets = [
        con("mount", [0, 0, 0], [0, -1, 0]),
        con("top", [mid.x, b.max.y, mid.z]),
        con("bottom", [mid.x, b.min.y, mid.z], [0, -1, 0]),
        con("left", [b.min.x, mid.y, mid.z], [-1, 0, 0], [0, 1, 0]),
        con("right", [b.max.x, mid.y, mid.z], [1, 0, 0], [0, 1, 0]),
        con("front", [mid.x, mid.y, b.max.z], [0, 0, 1]),
        con("back", [mid.x, mid.y, b.min.z], [0, 0, -1]),
      ];
      for (const s of g.userData.anatomy?.connectors || []) {
        sockets = sockets.filter((x) => x.id !== s.id);
        sockets.push(copy(s));
      }
      const sm = new Map<string, BoundSocket>();
      for (const s of sockets) {
        frame(s);
        sm.set(s.id!, { ...s, id: s.id!, node: root });
      }
      for (const b of rig)
        sm.set("joint." + b.name, {
          id: "joint." + b.name,
          node: nodes.get("rig." + b.name)!,
          position: [0, 0, 0],
          normal: [0, 1, 0],
          tangent: [1, 0, 0],
          interface: "joint",
        });
      ctx.partCount++;
      if (ctx.partCount > 3500) fail("Part instance budget");
      return {
        root,
        sockets: sm,
        bom: [
          {
            instance: "root",
            part: id,
            name: d.name,
            material: mat,
            params,
            style,
            level: d.level || 1,
            components: g.userData.anatomy?.dependencies || [],
          },
        ],
        nodes,
      };
    };
    const surfaceParams = (m?: RuntimeSpec["metadata"]): Parameters =>
      Object.fromEntries(
        Object.entries(m || {}).filter(([k]) =>
          ["roundness", "voxel_resolution", "seed"].includes(k),
        ),
      );
    const make = (
      input: RuntimeSpec,
      sty: string,
      stack: string[] = [],
      parentSurface?: Parameters,
    ): BuiltTree => {
      input = Semantic.assembly(input);
      this.contracts.validateRuntime(input.metadata?.runtime);
      if (stack.length > 12 || stack.includes(input.id || ""))
        fail("Nested assembly cycle/depth");
      if (input.schema === "wx.part-build/1.0")
        return makePart(
          input.part!,
          input.style || sty,
          input.params || {},
          input.material,
        );
      if (input.schema !== "wx.assembly/1.0") fail("Unknown schema");
      if (
        Object.keys(input).some(
          (k) =>
            ![
              "schema",
              "id",
              "name",
              "version",
              "category",
              "tags",
              "description",
              "instances",
              "exports",
              "style",
              "max_triangles",
              "metadata",
              "internal",
            ].includes(k),
        )
      )
        fail("Unknown assembly field");
      if (input.internal !== undefined && typeof input.internal !== "boolean")
        fail("Assembly internal flag must be boolean");
      const items = expand(input.instances);
      if (!items.length) fail("Empty assembly");
      const root = new T.Group();
      root.name = "root";
      root.userData.wx_role = "assembly_root";
      const out: BuiltTree = {
          root,
          nodes: new Map([["root", root]]),
          sockets: new Map(),
          bom: [],
        },
        by = new Map<string, RuntimeInstance>();
      for (const it of items) {
        const allowed = [
          "id",
          "part",
          "assembly",
          "position",
          "rotation",
          "scale",
          "params",
          "material",
          "style",
          "parent",
          "attach",
          "joint",
          "angle",
          "role",
          "pivot",
          "collision",
        ];
        if (Object.keys(it).some((k) => !allowed.includes(k)))
          fail("Unknown instance field");
        if (!safe(it.id) || it.id === "root" || by.has(it.id))
          fail("Duplicate/reserved instance ID");
        if (!!it.part === !!it.assembly) fail("One source per instance");
        by.set(it.id, it);
      }
      const seen = new Set<string>(),
        visiting = new Set<string>(),
        ordered: string[] = [];
      const owner = (path: string) =>
        [...by.keys()]
          .filter((x) => path === x || path.startsWith(x + "."))
          .sort((a, b) => b.length - a.length)[0];
      function visit(id: string) {
        if (seen.has(id)) return;
        if (visiting.has(id)) fail("Parent/attachment cycle");
        visiting.add(id);
        const it = by.get(id)!;
        for (const p of [it.parent, it.attach?.target].filter(
          (p): p is string => Boolean(p),
        )) {
          const o = owner(p);
          if (!o) fail("Unknown parent " + p);
          visit(o);
        }
        visiting.delete(id);
        seen.add(id);
        ordered.push(id);
      }
      for (const id of by.keys()) visit(id);
      for (const id of ordered) {
        const it = by.get(id)!,
          st = it.style || sty;
        let sub;
        if (it.part)
          sub = makePart(
            it.part,
            st,
            {
              ...surfaceParams(input.metadata),
              ...(parentSurface || {}),
              ...(it.params || {}),
            },
            it.material,
          );
        else {
          if (this.retired.has("assembly:" + it.assembly))
            throw Error(
              "ASSET_RETIRED: " +
                it.assembly +
                "; explicit migration required.",
            );
          const child = this.templates.get(it.assembly!);
          if (!child) fail("Unknown template " + it.assembly);
          const childSpec = copy(child);
          if (it.params)
            childSpec.metadata = {
              ...childSpec.metadata,
              parameters: { ...childSpec.metadata?.parameters, ...it.params },
            };
          sub = make(childSpec, st, [...stack, input.id!], {
            ...surfaceParams(input.metadata),
            ...(parentSurface || {}),
          });
        }
        if (it.collision !== undefined) {
          if (!it.part) fail("Collision override belongs to a part instance");
          this.contracts.validateRuntime({
            schema: "wx.runtime-metadata/1.0",
            units: "m",
            up: "+Y",
            forward: "+Z",
            collision: it.collision,
          });
          sub.bom[0].collision_override = copy(it.collision);
        }
        if (it.pivot !== undefined) {
          const pivot = vec(it.pivot);
          if (pivot.some((v) => Math.abs(v) > 1e4)) fail("Invalid local pivot");
          if (it.attach)
            fail("Explicit pivot and socket attachment are mutually exclusive");
          const content = sub.root,
            holder = new T.Group(),
            scale = vec(it.scale || [1, 1, 1]);
          matrix([0, 0, 0], [0, 0, 0], scale);
          content.position.fromArray(pivot.map((v, i) => -v * scale[i]));
          content.scale.fromArray(scale);
          content.updateMatrix();
          holder.add(content);
          sub.nodes.set("__content", content);
          sub.nodes.set("root", holder);
          sub.root = holder;
          holder.userData.authoredPivot = pivot;
          holder.userData.contentNode = "__content";
        }
        const parent = out.nodes.get(it.parent || "root");
        if (!parent) fail("Parent node not found");
        for (const [n, o] of sub.nodes) {
          const nn = n === "root" ? id : id + "." + n;
          o.name = nn;
          o.userData.wxSourceName = nn;
          if (o.userData.contentNode)
            o.userData.contentNode = id + "." + o.userData.contentNode;
          if (o.userData.kit_instance)
            o.userData.kit_instance = id + "." + o.userData.kit_instance;
          out.nodes.set(nn, o);
        }
        sub.root.userData.wx_role =
          it.role || (it.part ? "part_instance" : "subassembly_instance");
        sub.root.userData.kit_instance = id;
        parent.add(sub.root);
        const tr = matrix(
          it.position,
          it.rotation,
          it.pivot !== undefined ? [1, 1, 1] : it.scale,
        );
        tr.decompose(sub.root.position, sub.root.quaternion, sub.root.scale);
        sub.root.updateMatrix();
        for (const [sid, s] of sub.sockets)
          out.sockets.set(id + "." + sid, { ...s, id: id + "." + sid });
        out.bom.push(
          ...sub.bom.map((e) => ({
            ...e,
            instance: e.instance === "root" ? id : id + "." + e.instance,
          })),
        );
        ctx.nodes += sub.nodes.size;
        if (ctx.nodes > 14000) fail("Node budget");
        if (it.attach) {
          const a = it.attach;
          if (
            ["position", "rotation", "scale"].some(
              (k) =>
                JSON.stringify(
                  it[k] || (k === "scale" ? [1, 1, 1] : [0, 0, 0]),
                ) !== JSON.stringify(k === "scale" ? [1, 1, 1] : [0, 0, 0]),
            )
          )
            fail("Attached instances must not also use TRS");
          const target = out.sockets.get(a.target + "." + (a.socket || "top")),
            own = out.sockets.get(id + "." + (a.own || "mount"));
          if (!target || !own) fail("Socket missing");
          root.updateMatrixWorld(true);
          {
            const decision = this.contracts.compatible(
              this.contracts.world(target, target.node.matrixWorld),
              this.contracts.world(own, own.node.matrixWorld),
            );
            if (!decision.compatible && !a.allow_interface_mismatch)
              fail(decision.reason);
          }
          const tf = target.node.matrixWorld.clone().multiply(frame(target)),
            of = sub.root.matrixWorld
              .clone()
              .invert()
              .multiply(own.node.matrixWorld)
              .multiply(frame(own));
          const flip = new T.Matrix4();
          if (!a.mode || a.mode === "opposed") flip.makeRotationX(Math.PI);
          else if (a.mode !== "coincident") fail("Mate mode");
          const desired = tf
            .multiply(matrix(a.offset || [0, 0, 0], [0, 0, a.twist || 0]))
            .multiply(flip)
            .multiply(of.invert());
          parent.updateWorldMatrix(true, false);
          const local = parent.matrixWorld.clone().invert().multiply(desired);
          local.decompose(
            sub.root.position,
            sub.root.quaternion,
            sub.root.scale,
          );
          sub.root.updateMatrix();
        }
        if (it.joint) {
          const axis = V(vec(it.joint.axis || [0, 1, 0]));
          if (axis.lengthSq() < 1e-8) fail("Joint axis");
          const lim = it.joint.limits || [-180, 180],
            angle = it.angle || 0;
          if (
            !Number.isFinite(angle) ||
            !Array.isArray(lim) ||
            lim.length !== 2 ||
            !lim.every(Number.isFinite) ||
            angle < lim[0] ||
            angle > lim[1]
          )
            fail("Joint limits");
          sub.root.quaternion.multiply(
            new T.Quaternion().setFromAxisAngle(axis.normalize(), rad(angle)),
          );
          sub.root.userData.joint = { ...it.joint, angle };
          sub.root.updateMatrix();
        }
      }
      Mechanics.apply(root, input);
      root.updateMatrixWorld(true);
      const exportedIDs = new Set();
      for (const e of input.exports || []) {
        if (typeof e.id !== "string" || exportedIDs.has(e.id))
          fail("Duplicate or invalid exported socket");
        exportedIDs.add(e.id);
        if (e.position !== undefined) {
          if (e.node !== undefined || e.socket !== undefined)
            fail("Direct socket cannot also reference a node");
          frame(e);
          this.contracts.validate(e);
          const frameNode = out.nodes.get(e.frame_node || "root");
          if (!frameNode) fail("Unknown exported frame node");
          out.sockets.set(e.id, { ...copy(e), id: e.id, node: frameNode });
          continue;
        }
        const s = out.sockets.get(e.node + "." + e.socket);
        if (!s) fail("Export socket missing");
        const f = s.node.matrixWorld.clone().multiply(frame(s)),
          p = V(),
          q = new T.Quaternion(),
          sc = V();
        f.decompose(p, q, sc);
        out.sockets.set(e.id, {
          ...this.contracts.world(s, s.node.matrixWorld),
          id: e.id,
          node: root,
          position: p.toArray(),
          normal: V([0, 0, 1]).applyQuaternion(q).toArray(),
          tangent: V([1, 0, 0]).applyQuaternion(q).toArray(),
          interface: s.interface,
        });
      }
      if (!out.sockets.has("mount"))
        out.sockets.set("mount", {
          id: "mount",
          node: root,
          position: [0, 0, 0],
          normal: [0, -1, 0],
          tangent: [1, 0, 0],
          interface: "surface",
        });
      return out;
    };
    let out: BuiltTree;
    try {
      out = make(spec, style);
      out.root.updateMatrixWorld(true);
      out.root.traverse((o) => {
        if (Guards.isSkinnedMesh(o)) {
          o.bind(o.skeleton);
          o.normalizeSkinWeights();
          o.skeleton.update();
        }
      });
      const report = {
        triangles: 0,
        vertices: 0,
        nodes: 0,
        meshes: 0,
        materials: ctx.mats.size,
        textures: [...ctx.mats.values()].filter((m) => m.map).length,
        mesh_stats: [] as {
          node: string;
          material: string;
          triangles: number;
        }[],
        evidence: { runtime_generation: true },
        skins: 0,
        bones: 0,
        sockets: [] as Record<string, unknown>[],
        unique_gltf_meshes: 0,
      };
      const gset = new Set();
      out.root.traverse((o) => {
        report.nodes++;
        if (Guards.isSkinnedMesh(o)) report.skins++;
        if (Guards.isBone(o)) report.bones++;
        o.userData.wxSourceName = o.name;
        if (Guards.isMesh(o)) {
          const n =
            o.geometry.index?.count ?? o.geometry.attributes.position.count;
          report.triangles += n / 3;
          report.vertices += o.geometry.attributes.position.count;
          report.meshes++;
          gset.add(o.geometry);
          report.mesh_stats.push({
            node: o.name,
            material: Array.isArray(o.material)
              ? o.material.map((m) => m.name).join(",")
              : o.material.name,
            triangles: n / 3,
          });
        }
      });
      if (report.triangles > Math.min(500000, spec.max_triangles || 400000))
        fail("Triangle budget");
      report.unique_gltf_meshes = gset.size;
      for (const [id, s] of out.sockets)
        report.sockets.push({
          ...Object.fromEntries(
            Object.entries(s).filter(([k]) => k !== "node"),
          ),
          id,
          node: s.node.name,
          position: s.position,
          axis: s.normal,
          tangent: s.tangent,
          interface: s.interface,
        });
      out.root.userData.wxRuntime = copy(
        spec.schema === "wx.part-build/1.0"
          ? this.parts.get(spec.part!)?.runtime || {}
          : spec.metadata?.runtime || {},
      );
      out.root.userData.wx = {
        schema: "wx.live/2.0",
        spec: copy(spec),
        sockets: report.sockets,
      };
      out.root.userData.wx_provenance = Object.fromEntries(
        out.bom.map((e) => [e.part, this.parts.get(e.part)!.source]),
      );
      return { ...out, report, promises: ctx.promises, spec: copy(spec) };
    } catch (error) {
      ctx.geos.forEach((g) => g.dispose());
      ctx.skeletons.forEach((s) => s.dispose());
      ctx.mats.forEach((m) => {
        Object.values(m).forEach((t) => {
          if (Guards.isTexture(t)) t.dispose();
        });
        m.dispose();
      });
      Promise.allSettled(ctx.promises);
      throw error;
    }
  }
  async build(spec: RuntimeSpec, options: BuildOptions = {}) {
    const out = this.buildSync(spec, options);
    try {
      await Promise.all(out.promises);
      return out;
    } catch (error) {
      const geos = new Set<T.BufferGeometry>(),
        mats = new Set<T.Material>();
      out.root.traverse((o) => {
        if (Guards.isMesh(o)) {
          geos.add(o.geometry);
          for (const m of Array.isArray(o.material) ? o.material : [o.material])
            mats.add(m);
        }
        if (Guards.isSkinnedMesh(o)) o.skeleton.dispose();
      });
      geos.forEach((g) => g.dispose());
      mats.forEach((m) => {
        Object.values(m).forEach((t) => {
          if (Guards.isTexture(t)) t.dispose();
        });
        m.dispose();
      });
      throw error;
    }
  }
  clips(root: T.Object3D, id: string | undefined) {
    const clips: NonNullable<
        NonNullable<RuntimeData["motions"]>[string]["clips"]
      > = [],
      by = new Map<string, T.Object3D>();
    root.traverse((o) => by.set(o.name, o));
    const visit = (
      ident: string,
      prefix = "",
      stack: string[] = [],
      current: RuntimeSpec | null = null,
      params: Parameters | null = null,
    ) => {
      if (stack.includes(ident) || stack.length > 12)
        throw Error("MOTION_INVALID: cycle/depth");
      for (const original of this.motions[ident]?.clips || []) {
        const c = copy(original);
        c.name = prefix + c.name;
        for (const t of c.tracks) t.node = prefix + t.node;
        clips.push(c);
      }
      let spec = copy(current || this.templates.get(ident) || {});
      if (params) {
        spec.metadata = spec.metadata || {};
        spec.metadata.parameters = { ...spec.metadata.parameters, ...params };
      }
      spec = Semantic.assembly(spec);
      for (const i of spec.instances || [])
        if (i.enabled !== false && i.assembly)
          visit(
            i.assembly,
            prefix + i.id + ".",
            [...stack, ident],
            null,
            i.params,
          );
    };
    visit(id || "", "", [], root.userData.wx?.spec);
    return clips.map((c) => {
      const tracks = [];
      if (!Number.isFinite(c.duration) || c.duration <= 0 || c.duration > 120)
        throw Error("MOTION_INVALID: duration");
      for (const t of c.tracks) {
        const o = by.get(t.node);
        if (!o) throw Error("MOTION_INVALID: missing node " + t.node);
        const rotation = Array.isArray(t.degrees),
          translation = Array.isArray(t.translations);
        if (rotation === translation)
          throw Error("MOTION_INVALID: specify one channel");
        const keys = (rotation ? t.degrees : t.translations)!;
        if (
          keys.length < 2 ||
          keys.length > 4096 ||
          keys.some((v) => !Number.isFinite(v))
        )
          throw Error("MOTION_INVALID: keys");
        if (
          !Array.isArray(t.axis) ||
          t.axis.length !== 3 ||
          t.axis.some((v) => !Number.isFinite(v))
        )
          throw Error("MOTION_INVALID: axis");
        const axis = V(t.axis);
        if (axis.lengthSq() < 1e-12) throw Error("MOTION_INVALID: axis");
        axis.normalize();
        const values = [],
          times = keys.map((_, i) => (i / (keys.length - 1)) * c.duration);
        for (const v of keys) {
          if (rotation)
            values.push(
              ...o.quaternion
                .clone()
                .multiply(new T.Quaternion().setFromAxisAngle(axis, rad(v)))
                .toArray(),
            );
          else
            values.push(
              ...o.position
                .clone()
                .add(
                  axis
                    .clone()
                    .multiply(o.scale)
                    .applyQuaternion(o.quaternion)
                    .multiplyScalar(v),
                )
                .toArray(),
            );
        }
        tracks.push(
          rotation
            ? new T.QuaternionKeyframeTrack(
                o.uuid + ".quaternion",
                times,
                values,
              )
            : new T.VectorKeyframeTrack(o.uuid + ".position", times, values),
        );
      }
      return new T.AnimationClip(c.name, c.duration, tracks);
    });
  }
}
export default { Library, expand, matrix, frame, version: "3.0.0" };
