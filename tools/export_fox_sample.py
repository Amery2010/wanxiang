"""Export the authored fox sample and a comparable view of the current catalog fox.

This uses an isolated resource overlay because the full-library author rebuild has
unrelated pending source/bounds changes. No generated library file is modified.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages/kit/src"))
FOX_PARTS = (
    "w.fauna.fox.torso",
    "w.fauna.fox.tail",
    "w.fauna.fox.body",
    "w.fauna.fox.foreleg",
    "w.fauna.fox.hindleg",
    "w.fauna.fox.paw",
)


def export_worker(resource_root: Path, output: Path) -> None:
    from wanxiang.glb import export_glb
    from wanxiang.kit_assembly import Assembler, get_template, materials_for
    from wanxiang.live_geometry import stop
    from wanxiang.rigid_motion import tracks_for

    try:
        asset = Assembler("lowpoly").assemble(get_template("world-fox"))
        export_glb(
            asset,
            materials_for(asset),
            output,
            animations=tracks_for(asset, "world-fox"),
        )
    finally:
        stop()


def overlay(resource_root: Path) -> None:
    library = resource_root / "library"
    library.mkdir()
    source = ROOT / "library"
    (resource_root / "authoring").symlink_to(ROOT / "authoring", target_is_directory=True)
    for path in source.iterdir():
        if path.name not in ("parts", "assemblies"):
            (library / path.name).symlink_to(path, target_is_directory=path.is_dir())

    sys.path.insert(0, str(ROOT / "tools"))
    from author_foundation import generate

    # L1/L2 author data is intentionally outside this sample. The existing fox
    # head already has the later repair39 sculpt, so it remains from the catalog.
    authored = generate(include_l2=False)
    for kind, changed in (("parts", FOX_PARTS), ("assemblies", ("world-fox",))):
        target_dir = library / kind
        target_dir.mkdir()
        for existing in (source / kind).glob("*.json"):
            if existing.stem not in changed:
                (target_dir / existing.name).symlink_to(existing)
        for ident in changed:
            target = target_dir / f"{ident}.json"
            target.write_text(
                json.dumps(authored[kind][ident], ensure_ascii=False, sort_keys=True, indent=2)
                + "\n",
                encoding="utf-8",
            )


def export_from(resource_root: Path, output: Path) -> None:
    env = os.environ.copy()
    env["WX_RESOURCE_ROOT"] = str(resource_root)
    env["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "packages/kit/src"), str(ROOT / "tools"), env.get("PYTHONPATH", ""))
    )
    subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker", str(resource_root), str(output)],
        cwd=ROOT,
        env=env,
        check=True,
    )


def render_comparison(output: Path) -> None:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    from wanxiang.render import camera_basis, prepare, render_prepared

    data = {name: prepare(output / f"{name}.glb") for name in ("before", "after")}
    vertices = np.concatenate([data[name]["vertices"] for name in data])
    target = (vertices.min(axis=0) + vertices.max(axis=0)) / 2
    size = 720
    views = {"iso": (36, 24), "side": (90, 12), "front": (0, 12), "rear": (180, 12)}
    for label, (azimuth, elevation) in views.items():
        projected = (vertices - target) @ camera_basis(azimuth, elevation)
        span = max(float(np.ptp(projected[:, :2], axis=0).max()) * 1.18, 0.025)
        for name in data:
            image, _ = render_prepared(
                data[name], size, azimuth, elevation, target=target, fixed_scale=span
            )
            image.save(output / f"{name}-{label}.png")

    sheet = Image.new("RGB", (size * 2, size * 2 + 64), "#F1EEE9")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 27)
    except OSError:
        font = ImageFont.load_default()
    draw.text((30, 15), "BEFORE", font=font, fill="#34322E")
    draw.text((size + 30, 15), "FOX SAMPLE", font=font, fill="#34322E")
    for row, label in enumerate(("iso", "side")):
        for column, name in enumerate(("before", "after")):
            image = Image.open(output / f"{name}-{label}.png").convert("RGBA")
            sheet.paste(image, (column * size, 64 + row * size), image)
    sheet.save(output / "comparison.png")
    (output / "comparison.json").write_text(
        json.dumps(
            {
                "asset": "world-fox",
                "source": "exported GLB, CPU diagnostic renderer",
                "renderer_limitations": "No IBL or shadow map; geometry comparison only",
                "camera": "identical target and scale for each before/after view",
                "triangles": {name: len(data[name]["faces"]) for name in data},
                "bounds": {
                    name: [data[name]["vertices"].min(axis=0).tolist(), data[name]["vertices"].max(axis=0).tolist()]
                    for name in data
                },
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        export_worker(Path(sys.argv[2]), Path(sys.argv[3]))
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "generated/fox-sample")
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    export_from(ROOT, output / "before.glb")
    with tempfile.TemporaryDirectory(prefix="wx-fox-sample-") as folder:
        resource_root = Path(folder)
        overlay(resource_root)
        export_from(resource_root, output / "after.glb")
    render_comparison(output)
    print(output / "comparison.png")
    print(output / "after.glb")


if __name__ == "__main__":
    main()
