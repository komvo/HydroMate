"""Collect observed build evidence, packaged resources and deterministic checks.

Run after Gradle, from any directory. This does not execute or claim Android UI tests.
"""
import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "mobile/app"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def luminance(rgb):
    def linear(v):
        v /= 255
        return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    return sum(linear(v) * c for v, c in zip(rgb, (.2126, .7152, .0722)))


def rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def contrast(a, b):
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + .05) / (lo + .05)


def main():
    build_log = ROOT / ".local/aero-validation.log"
    log = build_log.read_text("utf-16") if build_log.read_bytes().startswith(b"\xff\xfe") else build_log.read_text("utf-8-sig")
    assert "BUILD SUCCESSFUL" in log and "BUILD FAILED" not in log
    reports = []
    for path in sorted((APP / "build/test-results/testDebugUnitTest").glob("TEST-*.xml")):
        suite = ET.parse(path).getroot()
        reports.append({k: suite.get(k) for k in ("name", "tests", "failures", "errors", "skipped", "timestamp")})
    assert reports and all(int(s[k] or 0) == 0 for s in reports for k in ("failures", "errors", "skipped"))
    lint = ET.parse(APP / "build/reports/lint-results-debug.xml").getroot()
    issues = [{"id": i.get("id"), "severity": i.get("severity")} for i in lint.findall("issue")]
    assert not any(i["severity"] in ("Error", "Fatal") for i in issues)
    resources = json.loads((ROOT / "docs/recursos.json").read_text("utf-8"))
    for asset in resources["resources"]:
        assert sha(ROOT / asset["path"]) == asset["sha256"], asset["path"]
    apks = {}
    aapt = sorted((Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk/build-tools").glob("*/aapt2.exe"))[-1]
    for variant, filename in (("debug", "app-debug.apk"), ("release", "app-release-unsigned.apk")):
        path = APP / "build/outputs/apk" / variant / filename
        with ZipFile(path) as archive:
            names = archive.namelist()
            dex = b"".join(archive.read(n) for n in names if n.endswith(".dex"))
            contains_fixture = b"test-demo-aero" in dex
            assert contains_fixture == (variant == "debug")
            assert "assets/licenses/fluent-emoji-MIT.txt" in names
            # Release aapt2 shortens resource file paths; inspect the resource table.
            table = subprocess.check_output([str(aapt), "dump", "resources", str(path)], text=True, encoding="utf-8")
            packaged = dict(re.findall(r"drawable/(hm_\w+)\s+\(nodpi\) \(file\) (\S+) type=PNG", table))
            assert all(Path(asset["path"]).stem in packaged and packaged[Path(asset["path"]).stem] in names
                       for asset in resources["resources"])
        apks[variant] = {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                         "sha256": sha(path), "demo_fixture_present": contains_fixture,
                         "icons_and_license_packaged": True}
    # Native text is on opaque gradient surfaces. Sample the full gradients and
    # their white highlight, including focus/disabled colors, not only base tokens.
    checks = []
    for text_color, background in (("#163B50", "#49C9F5"), ("#163B50", "#B7E94D"),
                                   ("#4B6472", "#EEF9FF"), ("#4B6472", "#E2EBEF"),
                                   ("#8A4A00", "#FFF4DC"), ("#B3261E", "#FFF4DC"),
                                   ("#163B50", "#E0F5FC")):
        base = rgb(background)
        samples = [tuple(round(c + (255 - c) * t / 100) for c in base) for t in range(101)]
        minimum = min(contrast(rgb(text_color), b) for b in samples)
        assert minimum >= 4.5, (text_color, background, minimum)
        checks.append({"text": text_color, "surface_to_white": background, "minimum_ratio": round(minimum, 2)})
    manifests = {}
    for variant in ("debug", "release"):
        path = APP / f"build/intermediates/merged_manifests/{variant}/process{variant.title()}Manifest/AndroidManifest.xml"
        app = ET.parse(path).getroot().find("application")
        cleartext = app.get("{http://schemas.android.com/apk/res/android}usesCleartextTraffic")
        assert cleartext == ("true" if variant == "debug" else "false")
        manifests[variant] = {"cleartext": cleartext}
    evidence = {
        "local_date": "2026-10-03", "timezone": "America/Tijuana",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "build": "testDebugUnitTest lintDebug assembleDebug assembleRelease: BUILD SUCCESSFUL",
        "tests": reports, "total_tests": sum(int(s["tests"]) for s in reports), "lint": issues,
        "api_integration": "Opt-in RepositoryTest against http://127.0.0.1:8000; existing synthetic records; GET only",
        "separate_http_probe": "Invoke-RestMethod timed out after 12 seconds; cause not established",
        "assets": {"count": len(resources["resources"]), "hashes_verified": True, "revision": resources["revision"]},
        "apks": apks, "manifests": manifests, "gradient_contrast_samples": checks,
        "visual_validation": {"status": "pending", "adb_devices": [], "configured_avds": [],
                              "new_screenshots": [], "instrumentation_run": False,
                              "matrix": "320/360/412 dp × font 1.0/1.3/2.0; rotation, IME, gestures/3 buttons, TalkBack"},
        "backup": ".local/backups/android-aero-2026-10-03", "git": "No repository; local backup comparison",
    }
    path = ROOT / "docs/evidence/android-aero-2026-10-03.json"
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tests": evidence["total_tests"], "lint": issues, "apks": apks,
                      "contrast": checks, "visual": "pending"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
