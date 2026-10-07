"""Capture native debug visual reviews without changing device settings or injecting input.
The fixture activity has no repository/preferences/commands. This is layout evidence,
not a test of MainActivity networking, touch, TalkBack, rotation or keyboard behavior.
"""
import argparse
import json
import subprocess
import struct
import time
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb", required=True)
    parser.add_argument("--serial", required=True)
    parser.add_argument("--set", choices=["home", "screens", "matrix"], default="home")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "docs/evidence/eco-2026-10-04")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    def adb(*parts):
        result = subprocess.run([args.adb, "-s", args.serial, *parts],
                                capture_output=True, text=True, encoding="utf-8", timeout=25)
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        return result.stdout

    if args.set == "home":
        cases = [("home-demo-393", "HOME", 393, 1, 1, False, False)]
    elif args.set == "screens":
        cases = [(name.lower()+"-393", name, 393, 1, 1, False, False)
                 for name in ["HISTORY", "CULTIVATION", "CONTROL", "SETTINGS"]]
        cases += [("home-bottom-393", "HOME", 393, 1, 1, False, True),
                  ("history-bottom-393", "HISTORY", 393, 1, 1, False, True),
                  ("settings-bottom-393", "SETTINGS", 393, 1, 1, False, True)]
    else:
        cases = [(f"home-{width}-font{font}", "HOME", width, font, 1, False, False)
                 for width in [320, 360, 412] for font in [1, 1.3, 2]]
        cases += [(f"home-state{state}-360", "HOME", 360, 1, state, False, False) for state in [2,3,4,5,6,7]]
        cases += [("home-night-393", "HOME", 393, 1, 1, True, False),
                  ("settings-font2-320", "SETTINGS", 320, 2, 1, False, False),
                  ("control-font2-320", "CONTROL", 320, 2, 1, False, False)]
    reports = []
    for name, screen, width, font, scenario, night, bottom in cases:
        adb("shell", "am", "start", "-W", "-f", "0x10008000",
            "-n", "com.hydromate.mobile/.VisualCheckActivity",
            "--es", "screen", screen, "--ei", "width_dp", str(width),
            "--ef", "font_scale", str(font), "--ei", "scenario", str(scenario),
            "--ez", "night", str(night).lower(), "--ez", "bottom", str(bottom).lower())
        time.sleep(.4)
        power = adb("shell", "dumpsys", "power")
        if "mWakefulness=Asleep" in power or "mWakefulness=Dozing" in power:
            raise RuntimeError("Phone screen is off. Unlock the phone before recording visual evidence.")
        adb("shell", "screencap", "-p", "/sdcard/hydromate-eco-review.png")
        adb("pull", "/sdcard/hydromate-eco-review.png", str(out / (name+".png")))
        width_px, height_px = struct.unpack(">II", (out / (name+".png")).read_bytes()[16:24])
        assert height_px > width_px, "Portrait fixture captured in landscape; do not count as portrait evidence"
        adb("pull", "/sdcard/Android/data/com.hydromate.mobile/files/visual-check.json", str(out / (name+".json")))
        report = json.loads((out / (name+".json")).read_text(encoding="utf-8"))
        report["capture"] = name+".png"
        assert report["screen"] == screen and report["scenario"] == scenario, "Stale audit"
        reports.append(report)
        print(json.dumps({"capture": name, "width_dp": report["width_dp"],
                          "font_scale": report["font_scale"],
                          "text_issues": report["text_issues"],
                          "small_targets": [t for t in report["touch_targets"]
                                            if min(t["width_dp"], t["height_dp"]) < 47.5]}, ensure_ascii=False),
              flush=True)
    (out / ("review-"+args.set+".json")).write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    main()

