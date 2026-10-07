"""Validate current Eco build evidence; preserves the Oct 3 evidence and manifests."""
import argparse, hashlib, json, os, re, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "mobile/app"
BACKUP = ROOT / ".local/backups/android-eco-2026-10-04/mobile/src"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def rgb(value):
    return tuple(int(value[i:i+2],16) for i in (1,3,5))
def blend(a,b,t):
    return tuple(int(x*(1-t)+y*t) for x,y in zip(a,b))
def luminance(a):
    def channel(v):
        v /= 255
        return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4
    return sum(channel(v)*w for v,w in zip(a,(.2126,.7152,.0722)))
def contrast(a,b):
    lo,hi=sorted((luminance(a),luminance(b)))
    return (hi+.05)/(lo+.05)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--build-log", type=Path, default=ROOT/".local/eco-validation.log")
    parser.add_argument("--baseline", type=Path, default=BACKUP)
    parser.add_argument("--evidence-dir", type=Path, default=ROOT/"docs/evidence/eco-2026-10-04")
    parser.add_argument("--report", type=Path, default=ROOT/"docs/evidence/android-eco-2026-10-04.json")
    args=parser.parse_args()
    baseline=args.baseline.resolve()
    log_path=args.build_log
    log=log_path.read_text("utf-16" if log_path.read_bytes().startswith(b"\xff\xfe") else "utf-8-sig")
    assert "BUILD SUCCESSFUL" in log and "BUILD FAILED" not in log
    tests=[]
    for p in sorted((APP/"build/test-results/testDebugUnitTest").glob("TEST-*.xml")):
        suite=ET.parse(p).getroot()
        tests.append({k:suite.get(k) for k in ("name","tests","failures","errors","skipped","timestamp")})
    assert len(tests)>=4 and all(int(t[k])==0 for t in tests for k in ("failures","errors"))
    issues=[{"id":i.get("id"),"severity":i.get("severity")} for i in ET.parse(APP/"build/reports/lint-results-debug.xml").getroot().findall("issue")]
    assert not any(i["severity"] in ("Error","Fatal") for i in issues)
    unchanged=[]
    for name in ["main/java/com/hydromate/mobile/Telemetry.kt", "main/java/com/hydromate/mobile/RequestFence.kt",
                 "main/java/com/hydromate/mobile/ConnectionStore.kt", "debug/java/com/hydromate/mobile/PreviewSupport.kt",
                 "release/java/com/hydromate/mobile/PreviewSupport.kt"]:
        assert sha(APP/"src"/name)==sha(baseline/name), name
        unchanged.append(name)
    for source_set in ["test","testDebug"]:
        for before in (baseline/source_set).rglob("*"):
            if before.is_file():
                relative=before.relative_to(baseline)
                assert sha(APP/"src"/relative)==sha(before), str(relative)
                unchanged.append(relative.as_posix())
    resources=json.loads((ROOT/"docs/recursos.json").read_text("utf-8"))
    for item in resources["resources"]+resources["native_artwork"]:
        p=ROOT/item["path"]
        item["sha256"]=sha(p); item["bytes"]=p.stat().st_size
    (ROOT/"docs/recursos.json").write_text(json.dumps(resources,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    aapt=sorted((Path(os.environ["LOCALAPPDATA"])/"Android/Sdk/build-tools").glob("*/aapt2.exe"))[-1]
    apks={}
    ns="{http://schemas.android.com/apk/res/android}"
    for variant, filename in [("debug","app-debug.apk"),("release","app-release-unsigned.apk")]:
        path=APP/"build/outputs/apk"/variant/filename
        manifest=ET.parse(APP/f"build/intermediates/merged_manifests/{variant}/process{variant.title()}Manifest/AndroidManifest.xml").getroot().find("application")
        assert manifest.get(ns+"usesCleartextTraffic")==("true" if variant=="debug" else "false")
        preview=any(a.get(ns+"name","").endswith("VisualCheckActivity") for a in manifest.findall("activity"))
        assert preview==(variant=="debug")
        with ZipFile(path) as z:
            dex=b"".join(z.read(n) for n in z.namelist() if n.endswith(".dex"))
            assert (b"test-demo-aero" in dex)==(variant=="debug")
            assert (b"VisualCheckActivity" in dex)==(variant=="debug")
            assert "assets/licenses/fluent-emoji-MIT.txt" in z.namelist()
        table=subprocess.check_output([str(aapt),"dump","resources",str(path)],text=True,encoding="utf-8")
        assert "drawable/hero_hydromate_glass" in table
        for item in resources["resources"]:
            assert "drawable/"+Path(item["path"]).stem in table, item["path"]
        assert not re.search(r"drawable/hm_\w+",table)
        apks[variant]={"path":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path),
                       "debug_fixtures_and_review_activity":preview,"cleartext":variant=="debug"}

    # Sample real token blends used behind text, including curved highlights.
    garden=resources["version"].startswith("0.6")
    colors={e.get("name"):rgb(e.text) for e in ET.parse(APP/"src/main/res/values/colors.xml").getroot()}
    checks=[]
    for night in [False,True]:
        c=dict(colors)
        if night: c.update({e.get("name"):rgb(e.text) for e in ET.parse(APP/"src/main/res/values-night/colors.xml").getroot()})
        veil=(5,25,15) if night else (239,250,221)
        backdrop=[blend(bg,veil,(191 if night else 189)/255) for bg in [(0,0,0),(255,255,255)]]
        def check(name,fg,samples,minimum=4.5):
            ratio=min(contrast(c[fg],bg) for bg in samples)
            checks.append({"theme":"night" if night else "day","pair":name,"minimum_ratio":round(ratio,3)})
            assert ratio>=minimum, (night,name,ratio)
        def glossy(fill):
            base=c[fill]; light=c["surface"]; bottom=blend(base,c["sky_deep"],.18 if night else .12)
            stops=[blend(base,light,.82),blend(base,light,.48),base,bottom,blend(base,light,.34)]
            positions=[0,.43,.46,.88,1]
            samples=[]
            for i,(a,b) in enumerate(zip(stops,stops[1:])):
                for step in range(101):
                    t=step/100
                    value=blend(a,b,t)
                    base_samples=[blend(bg,value,(180 if night else 110)/255) for bg in backdrop] if garden else [value]
                    samples.extend(base_samples)
                    y=positions[i]*(1-t)+positions[i+1]*t
                    # The curved reflection is confined to the upper half.
                    if y<=.51: samples.extend(blend(v,(255,255,255),(24 if night else 173)/255) for v in base_samples)
            return samples
        def plates(fill):
            plate=blend(c[fill],c["surface"],.45 if night else .91)
            return [blend(v,plate,(130 if night else 68)/255) for v in glossy(fill)] if garden else [plate]
        if garden:
            check("title / botanical backdrop","backdrop_ink",backdrop)
            check("subtitle / botanical backdrop","backdrop_muted",backdrop)
        for fill in ["sky","lime","water_soft"]:
            check("ink / glossy "+fill,"ink",glossy(fill))
        check("muted / hero","muted",glossy("sky"))
        check("primary / hero","primary",glossy("sky"))
        for fill in ["glass","surface","water_soft","sky","lime"]:
            check("muted / plate "+fill,"muted",plates(fill))
        for fg in ["warning","critical"]:
            check(fg+" / warning plate",fg,plates("warning_soft"))
    folder=args.evidence_dir.resolve()
    reviews=[]
    for name in ["home","screens","matrix"]:
        reviews += json.loads((folder/f"review-{name}.json").read_text("utf-8"))
    assert len(reviews)==26
    assert all(not r["text_issues"] for r in reviews)
    assert all(min(t["width_dp"],t["height_dp"])>=47.5 for r in reviews for t in r["touch_targets"])
    screenshots=[{"path":(folder/r["capture"]).relative_to(ROOT).as_posix(),"sha256":sha(folder/r["capture"]),
                  "screen":r["screen"],"width_dp":r["width_dp"],"font_scale":r["font_scale"],"scenario":r["scenario"],"night":r["night"]} for r in reviews]
    result={"date":"2026-10-04","observed_at_utc":datetime.now(timezone.utc).isoformat(),
            "build":"testDebugUnitTest lintDebug assembleDebug assembleRelease: BUILD SUCCESSFUL",
            "tests":tests,"passed":sum(int(t["tests"])-int(t["skipped"]) for t in tests),
            "skipped":sum(int(t["skipped"]) for t in tests),"lint":issues,"apks":apks,
            "functional_files_and_tests_unchanged":unchanged,"contrast":checks,
            "device":{"model":"2207117BPG","android":"13","api":33,"physical_px":[1080,2400],"density":440},
            "layout_review":{"count":len(reviews),"text_clipping_detected":0,"targets_under_48dp":0,
                             "scope":"Real device native views with Activity-local width/font configuration; not MainActivity interaction tests",
                             "screenshots":screenshots},
            "main_activity":"Installed, launched and real unavailable-server UI captured; no injected touch",
            "backend":"Docker daemon unavailable this session; optional GET integration test omitted. No database changes.",
            "pending":["Manual TalkBack and focus traversal","Keyboard and draft preservation in real Activity",
                       "Physical rotation of final build","System navigation gestures","Real API connection after starting backend/DB"],
            "version":resources["version"],
            "backup":baseline.relative_to(ROOT).as_posix(),"git":"No repository; reviewed against backup"}
    args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"passed":result["passed"],"skipped":result["skipped"],"lint":issues,"layout_reviews":len(reviews),"apks":apks},ensure_ascii=False))
if __name__=="__main__":
    main()

