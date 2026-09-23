import { useState } from "react";
import { useStore } from "zustand";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { download, type Session } from "./session";
import type { ParameterSchema, Parameters } from "../runtime/types";
import {
  SemanticParameterFields,
  type InspectorParameters,
} from "./inspector-utils";
export function ReviewParameters({ session }: { session: Session }) {
  const s = useStore(session.store),
    asset = s.current,
    [params, setParams] = useState<Parameters>({}),
    [seed, setSeed] = useState(Number(asset?.spec?.seed || 0)),
    [style, setStyle] = useState(String(asset?.spec?.style || "natural")),
    [profile, setProfile] = useState(
      String(asset?.spec?.profile || "standard"),
    );
  if (!asset) return null;
  if (asset.family === "imported" || !asset.recipe || !asset.spec)
    return <p>此模型没有可重建的组件配方。保留实际查看与导出。</p>;
  const recipe = asset.recipe as {
      parameter_schema?: ParameterSchema;
      defaults?: Parameters;
      presets?: Record<string, Parameters>;
    },
    schema = (recipe.parameter_schema?.properties || {}) as InspectorParameters,
    values = {
      ...recipe.defaults,
      ...recipe.presets?.[String(asset.spec.preset)],
      ...asset.spec.params,
      ...params,
    },
    job = () => ({
      ...asset.spec,
      id: String(asset.spec?.id || asset.id).slice(0, 65) + "-variant",
      params: { ...asset.spec?.params, ...params },
      seed,
      style,
      profile,
    });
  return (
    <>
      <h4>源参数 · 下次构建</h4>
      <SemanticParameterFields
        properties={schema}
        values={values}
        idPrefix="param"
        onCommit={(key, value) =>
          setParams((old) => ({ ...old, [key]: value }))
        }
      />
      <label>
        随机种子
        <Input
          id="seedInput"
          type="number"
          min={0}
          max={4294967295}
          value={seed}
          onChange={(e) =>
            setSeed(
              Math.max(
                0,
                Math.min(4294967295, Math.floor(e.target.valueAsNumber || 0)),
              ),
            )
          }
        />
      </label>
      <label>
        构建精度
        <select
          id="profileInput"
          value={profile}
          onChange={(e) => setProfile(e.target.value)}
        >
          <option value="draft">草模</option>
          <option value="standard">标准</option>
          <option value="hero">高精度</option>
        </select>
      </label>
      <div className="styles">
        {[
          ["natural", "自然"],
          ["storybook", "绘本"],
          ["industrial", "工业"],
        ].map(([id, label]) => (
          <Button
            key={id}
            aria-pressed={style === id}
            data-style={id}
            onClick={() => setStyle(id)}
          >
            {label}
          </Button>
        ))}
      </div>
      <p>这里修改下一次构建的参数。静态页面不会执行本地 Python。</p>
      <Button
        id="jobBtn"
        onClick={() =>
          download(JSON.stringify(job(), null, 2), asset.id + ".build.json")
        }
      >
        导出构建任务 JSON
      </Button>
      <Button
        id="copyCmd"
        onClick={() => {
          const value = job(),
            command = `./wx build --recipe ${String(asset.spec?.recipe)} --id ${value.id} --seed ${seed} --style ${style} --profile ${profile} --params '${JSON.stringify(value.params)}'`;
          void navigator.clipboard
            ?.writeText(command)
            .then(() => s.notify("CLI 命令已复制"))
            .catch(() => s.notify(command));
        }}
      >
        复制 CLI 构建命令
      </Button>
    </>
  );
}
