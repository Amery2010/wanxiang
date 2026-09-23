import { useEffect, useState } from "react";
import { Input } from "../ui/input";
import type { RuntimeAsset, RuntimeSpec } from "../runtime/types";

export interface InspectorParameter {
  type?: string;
  title?: string;
  default?: unknown;
  enum?: unknown[];
  enumNames?: unknown[];
  minimum?: number;
  maximum?: number;
  step?: number;
  unit?: string;
}

export type InspectorParameters = Record<string, InspectorParameter>;

export function parameterLabel(key: string, parameter: InspectorParameter) {
  return parameter.title || key;
}

export function parameterOptionLabel(
  parameter: InspectorParameter,
  value: unknown,
  index: number,
) {
  return String(parameter.enumNames?.[index] ?? value);
}

export function parameterNumber(parameter: InspectorParameter, value: unknown) {
  const fallback = parameter.default;
  const number = Number(value ?? fallback ?? parameter.minimum ?? 0);
  return Number.isFinite(number) ? number : 0;
}

export function formatParameterValue(
  parameter: InspectorParameter,
  value: unknown,
) {
  const number = parameterNumber(parameter, value);
  const decimals = parameter.type === "integer" ? 0 : 2;
  const text = number.toFixed(decimals).replace(/\.00$/, "");
  return parameter.unit ? `${text} ${parameter.unit}` : text;
}

interface SemanticParameterFieldsProps {
  properties: InspectorParameters;
  values: Record<string, unknown>;
  disabled?: boolean;
  idPrefix?: string;
  onCommit(key: string, value: unknown): void;
}

/**
 * The source parameter contract uses a range for numeric controls.  Draft
 * slider values stay local until the pointer/key interaction ends, so a
 * drag only schedules one build transaction instead of one transaction per
 * pixel. The adjacent number input remains available for precise values.
 */
export function SemanticParameterFields({
  properties,
  values,
  disabled = false,
  idPrefix = "semantic",
  onCommit,
}: SemanticParameterFieldsProps) {
  const [draft, setDraft] = useState<Record<string, unknown>>({});
  const valuesKey = JSON.stringify(values);

  useEffect(() => {
    setDraft({});
  }, [valuesKey]);

  const update = (key: string, value: unknown) =>
    setDraft((current) => ({ ...current, [key]: value }));

  const commit = (key: string, parameter: InspectorParameter) => {
    const source = values[key] ?? parameter.default;
    const value = draft[key] ?? source;
    if (value === undefined) return;
    const normalized =
      parameter.type === "number" || parameter.type === "integer"
        ? Number(value)
        : value;
    if (
      normalized === undefined ||
      (typeof normalized === "number" && !Number.isFinite(normalized)) ||
      normalized === source
    ) {
      return;
    }
    onCommit(key, normalized);
  };

  return (
    <>
      {Object.entries(properties).map(([key, parameter]) => {
        const value = draft[key] ?? values[key] ?? parameter.default;
        const label = parameterLabel(key, parameter);
        if (parameter.enum) {
          return (
            <label className="semantic-field" key={key}>
              {label}
              <select
                id={`${idPrefix}-${key}`}
                data-semantic={key}
                value={String(value ?? "")}
                disabled={disabled}
                onChange={(event) => {
                  const index = parameter.enum!.findIndex(
                    (item) => String(item) === event.target.value,
                  );
                  const option = parameter.enum![index];
                  const normalized =
                    parameter.type === "number" || parameter.type === "integer"
                      ? Number(option)
                      : option;
                  onCommit(key, normalized);
                }}
              >
                {parameter.enum.map((option, index) => (
                  <option key={String(option)} value={String(option)}>
                    {parameterOptionLabel(parameter, option, index)}
                  </option>
                ))}
              </select>
            </label>
          );
        }
        if (parameter.type === "boolean") {
          return (
            <label className="semantic-field" key={key}>
              <Input
                id={`${idPrefix}-${key}`}
                type="checkbox"
                data-semantic={key}
                checked={Boolean(value)}
                disabled={disabled}
                onChange={(event) => onCommit(key, event.target.checked)}
              />
              {label}
            </label>
          );
        }

        if (parameter.type !== "number" && parameter.type !== "integer") {
          return (
            <label className="semantic-field" key={key}>
              {label}
              <Input
                id={`${idPrefix}-${key}`}
                type="text"
                data-semantic={key}
                value={String(value ?? "")}
                disabled={disabled}
                onChange={(event) => update(key, event.target.value)}
                onBlur={() => commit(key, parameter)}
              />
            </label>
          );
        }

        const number = parameterNumber(parameter, value);
        const rangeId = `${idPrefix}-${key}`;
        const numberId = `${rangeId}-value`;
        return (
          <div className="semantic-field" key={key}>
            <label htmlFor={rangeId}>
              {label}
              <output data-semantic-value={key}>
                {formatParameterValue(parameter, number)}
              </output>
            </label>
            <Input
              id={rangeId}
              type="range"
              data-semantic={key}
              min={parameter.minimum}
              max={parameter.maximum}
              step={parameter.step ?? (parameter.type === "integer" ? 1 : 0.01)}
              value={number}
              disabled={disabled}
              aria-label={label}
              onChange={(event) => update(key, event.target.valueAsNumber)}
              onMouseUp={() => commit(key, parameter)}
              onTouchEnd={() => commit(key, parameter)}
              onKeyUp={() => commit(key, parameter)}
            />
            <Input
              id={numberId}
              type="number"
              data-semantic-input={key}
              min={parameter.minimum}
              max={parameter.maximum}
              step={parameter.step ?? (parameter.type === "integer" ? 1 : 0.01)}
              value={number}
              disabled={disabled}
              aria-label={`${label} 数值`}
              onChange={(event) => update(key, event.target.valueAsNumber)}
              onBlur={() => commit(key, parameter)}
            />
          </div>
        );
      })}
    </>
  );
}

export interface SourcePartTreeProps {
  rootIds: string[];
  parts: Record<string, RuntimeSpec>;
  assets: RuntimeAsset[];
  onSelect(asset: RuntimeAsset): void;
}

export interface SourcePartNode {
  id: string;
  name: string;
  level: number;
  depth: number;
}

export function sourcePartNodes(
  rootIds: string[],
  parts: Record<string, RuntimeSpec>,
): SourcePartNode[] {
  const seen = new Set<string>();
  const nodes: SourcePartNode[] = [];
  const walk = (id: string, depth: number) => {
    if (depth > 8 || seen.has(id)) return;
    const definition = parts[id];
    if (!definition) return;
    seen.add(id);
    nodes.push({
      id,
      name: String(definition.name || id),
      level: Number(definition.level || definition.metadata?.level || 1),
      depth,
    });
    const shapeParams = definition.shape_params;
    const components =
      shapeParams && typeof shapeParams === "object"
        ? (shapeParams as { components?: unknown }).components
        : undefined;
    if (!Array.isArray(components)) return;
    for (const component of components) {
      if (!component || typeof component !== "object") continue;
      const part = (component as { part?: unknown }).part;
      if (typeof part === "string") walk(part, depth + 1);
    }
  };
  rootIds.forEach((id) => walk(id, 0));
  return nodes;
}

export function sourceAsset(
  id: string,
  parts: Record<string, RuntimeSpec>,
  assets: RuntimeAsset[],
): RuntimeAsset | null {
  const existing = assets.find((asset) => asset.id === id);
  if (existing) return existing;
  const definition = parts[id];
  if (!definition) return null;
  return {
    ...definition,
    id,
    name: String(definition.name || id),
    level: Number(definition.level || definition.metadata?.level || 1),
    dynamic: true,
    kit: {
      schema: "wx.part-build/1.0",
      id,
      part: id,
      params: {},
      style: "lowpoly",
    },
  } as RuntimeAsset;
}

export function componentRootIds(asset: RuntimeAsset, spec: RuntimeSpec | null) {
  const bom = Array.isArray(asset.bom) ? asset.bom : [];
  const fromBom = bom
    .map((entry) => entry.part)
    .filter((part): part is string => typeof part === "string");
  if (fromBom.length) return fromBom;
  if (typeof spec?.part === "string") return [spec.part];
  return [];
}

export function runtimeLevels(
  asset: RuntimeAsset,
  spec: RuntimeSpec | null,
): Record<string, unknown>[] {
  const runtime = (asset.runtime || spec?.metadata?.runtime || {}) as Record<
    string,
    unknown
  >;
  const levels = runtime.lod_levels;
  if (Array.isArray(levels)) return levels as Record<string, unknown>[];
  const lod = runtime.lod;
  if (lod && typeof lod === "object") {
    const nested = (lod as { levels?: unknown }).levels;
    if (Array.isArray(nested)) return nested as Record<string, unknown>[];
  }
  return [];
}

export function reportSocketPorts(asset: RuntimeAsset): Record<string, unknown>[] {
  const sockets = asset.report?.sockets;
  return Array.isArray(sockets)
    ? sockets.filter(
        (port): port is Record<string, unknown> =>
          Boolean(port && typeof port === "object"),
      )
    : [];
}

export function resolvedCandidatePorts(
  spec: RuntimeSpec | null,
  parts: Record<string, RuntimeSpec>,
): Record<string, unknown>[] {
  const semantic = (
    globalThis as unknown as {
      WXSemantic?: {
        part(
          definition: RuntimeSpec,
          params: Record<string, unknown>,
          definitions: Record<string, RuntimeSpec>,
        ): Record<string, unknown>;
        assembly(specification: RuntimeSpec): Record<string, unknown>;
      };
    }
  ).WXSemantic;
  if (!semantic || !spec) return [];
  try {
    const candidate = spec as Record<string, unknown>;
    const resolved =
      candidate.part && typeof candidate.part === "string"
        ? semantic.part(parts[candidate.part], {}, parts)
        : semantic.assembly(spec);
    const ports = candidate.part ? resolved.connectors : resolved.exports;
    return Array.isArray(ports)
      ? ports.filter(
          (port): port is Record<string, unknown> =>
            Boolean(
              port &&
                typeof port === "object" &&
                (candidate.part || Array.isArray((port as Record<string, unknown>).position)),
            ),
        )
      : [];
  } catch {
    return [];
  }
}

export function runtimeCapability(
  asset: RuntimeAsset,
  spec: RuntimeSpec | null,
): Record<string, unknown> {
  const fromAsset = asset.runtime;
  if (fromAsset && typeof fromAsset === "object") return fromAsset;
  const fromSpec = spec?.metadata?.runtime;
  return fromSpec && typeof fromSpec === "object" ? fromSpec : {};
}
