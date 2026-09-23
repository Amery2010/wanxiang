import type { Mesh, SkinnedMesh, Bone, Texture } from "three";

// Three's structural markers also work when a consumer has its own module instance.
function marked(value: unknown, key: string): boolean {
  return (
    value !== null &&
    typeof value === "object" &&
    key in value &&
    (value as Record<string, unknown>)[key] === true
  );
}
export const isMesh = (value: unknown): value is Mesh =>
  marked(value, "isMesh");
export const isSkinnedMesh = (value: unknown): value is SkinnedMesh =>
  marked(value, "isSkinnedMesh");
export const isBone = (value: unknown): value is Bone =>
  marked(value, "isBone");
export const isTexture = (value: unknown): value is Texture =>
  marked(value, "isTexture");
