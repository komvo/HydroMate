"""Fetch the selected offline artwork from Microsoft's official repository.

No project data is uploaded. Pin the upstream revision in the resulting manifest.
"""
import hashlib
import json
import struct
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = {
    "hm_droplet": ("Droplet", "droplet"),
    "hm_seedling": ("Seedling", "seedling"),
    "hm_sun": ("Sun", "sun"),
    "hm_thermometer": ("Thermometer", "thermometer"),
    "hm_test_tube": ("Test tube", "test_tube"),
    "hm_gear": ("Gear", "gear"),
    "hm_bar_chart": ("Bar chart", "bar_chart"),
    "hm_home": ("House with garden", "house_with_garden"),
    "hm_control": ("Control knobs", "control_knobs"),
}


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "HydroMate-asset-builder"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main():
    manifest_path = ROOT / "docs/recursos.json"
    previous = json.loads(manifest_path.read_text("utf-8")) if manifest_path.exists() else None
    revision = previous["revision"] if previous else json.loads(fetch(
        "https://api.github.com/repos/microsoft/fluentui-emoji/commits/main"))["sha"]
    base = f"https://raw.githubusercontent.com/microsoft/fluentui-emoji/{revision}"
    folder = ROOT / "mobile/app/src/main/res/drawable-nodpi"
    folder.mkdir(parents=True, exist_ok=True)
    resources = []
    for local, (group, name) in ICONS.items():
        url = f"{base}/assets/{urllib.parse.quote(group)}/3D/{name}_3d.png"
        data = fetch(url)
        assert data[:8] == b"\x89PNG\r\n\x1a\n", f"Not PNG: {local}"
        dimensions = struct.unpack(">II", data[16:24])
        assert dimensions == (256, 256), dimensions
        path = folder / f"{local}.png"
        path.write_bytes(data)
        resources.append({"path": path.relative_to(ROOT).as_posix(), "source": url,
                          "author": "Microsoft Corporation", "license": "MIT",
                          "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                          "dimensions": list(dimensions), "modifications": "None; sized by ImageView"})
    license_text = fetch(f"{base}/LICENSE").decode("utf-8")
    license_folder = ROOT / "mobile/app/src/main/assets/licenses"
    license_folder.mkdir(parents=True, exist_ok=True)
    (license_folder / "fluent-emoji-MIT.txt").write_text(license_text, encoding="utf-8")
    manifest_path.write_text(json.dumps({"provider": "Microsoft Fluent Emoji 3D",
        "revision": revision, "resources": resources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "THIRD_PARTY_NOTICES").write_text(
        "HydroMate Aero — third-party artwork\n\n"
        "Microsoft Fluent Emoji, 3D PNG collection\n"
        "Source: https://github.com/microsoft/fluentui-emoji\n"
        f"Revision: {revision}\n"
        "Files, source URLs and SHA-256: docs/recursos.json\n"
        "Original PNG files, no pixel modifications. Sized by native ImageView.\n"
        "Full license is also bundled offline in the APK and shown in Settings.\n\n"
        + license_text + "\n\n"
        "Sky, waves, glass, buttons, navigation and tower: original native HydroMate artwork.\n"
        "Typeface: Android system sans-serif; no font redistributed.\n"
        "No third-party photos, wallpaper, logos or additional icon families are included.\n",
        encoding="utf-8")
    print(json.dumps({"revision": revision, "icons": len(resources),
                      "total_bytes": sum(r["bytes"] for r in resources)}))


if __name__ == "__main__":
    main()
