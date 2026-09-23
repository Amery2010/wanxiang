import type * as Three from "../src/three.js";
import type Styles from "../src/styles.js";
import type Surfaces from "../src/surfaces.js";
import type Contracts from "../src/contracts.js";
import type Semantic from "../src/semantic.js";
import type Primitives from "../src/primitives.js";
import type Seams from "../src/seams.js";
import type Facets from "../src/facets.js";
import type Geometry from "../src/geometry.js";
import type Mechanics from "../src/mechanics.js";
import type Runtime from "../src/runtime.js";
import type Pipeline from "../src/pipeline.js";
import type RuntimePack from "../src/runtime-pack.js";
import type CpuShadows from "../src/cpu-shadows.js";
import type BuildCache from "../src/build-cache.js";
import type BuildTasks from "../src/build-tasks.js";
import type BuildExport from "../src/build-export.js";
import type StudioCore from "../src/studio-core.js";
import type SceneDocument from "../src/scene-document.js";

/** Installed only by the browser/studio compatibility entries. */
export interface CompatibilityGlobals {
  THREE: typeof Three;
  WXStyles: typeof Styles;
  WXSurfaces: typeof Surfaces;
  WXContracts: typeof Contracts;
  WXSemantic: typeof Semantic;
  WXPrimitives: typeof Primitives;
  WXSeams: typeof Seams;
  WXFacets: typeof Facets;
  WXGeometry: typeof Geometry;
  WXMechanics: typeof Mechanics;
  WXRuntime: typeof Runtime;
  WXPipeline: typeof Pipeline;
  WXRuntimePack: typeof RuntimePack;
  WXCPUShadows: typeof CpuShadows;
  prepareCPUShadows: typeof CpuShadows.prepareCPUShadows;
  cpuShadowVisibility: typeof CpuShadows.cpuShadowVisibility;
  WXBuildCache: typeof BuildCache;
  WXBuildTasks: typeof BuildTasks;
  WXBuildExport: typeof BuildExport;
  WXStudioCore: typeof StudioCore;
  WXSceneDocument: typeof SceneDocument;
  WX_WORKER_SOURCE?: string;
}
