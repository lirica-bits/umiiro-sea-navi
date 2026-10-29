"""Build data.json for GitHub Pages from an ArtifactData export of 海況ナビ.

Usage: python3 -I tools/build_data.py <export_dir> <out.json>
<export_dir> holds trips/<id>.json and trips/<id>/data/<key>.json as saved by
ArtifactData list(out_dir=...). Personal fields (移動・メモ) are left out.
"""
import json, os, sys

PUBLIC_TRIP = ["name", "place", "lat", "lon", "start", "end", "shop", "shopUrl", "mode", "modeReason", "lastRunAt", "status"]
SKIP_DATA = {"areaRules"}

def body(path):
    d = json.load(open(path, encoding="utf-8"))
    return d.get("data", d) if isinstance(d, dict) and "version" in d else d

def main(src, out):
    tdir = os.path.join(src, "trips")
    trips, data = [], {}
    for f in sorted(os.listdir(tdir)):
        if not f.endswith(".json"):
            continue
        tid = f[:-5]
        t = body(os.path.join(tdir, f))
        pub = {k: t[k] for k in PUBLIC_TRIP if k in t}
        pub["id"] = tid
        pub["schedule"] = [{"date": s.get("date"), "kind": s.get("kind")} for s in t.get("schedule", [])]
        trips.append(pub)
        ddir = os.path.join(tdir, tid, "data")
        data[tid] = {}
        if os.path.isdir(ddir):
            for g in sorted(os.listdir(ddir)):
                key = g[:-5]
                if g.endswith(".json") and key not in SKIP_DATA:
                    data[tid][key] = body(os.path.join(ddir, g))
        # replace the "plan" text (built from personal memos) with a generic label
        kinds = {s.get("date"): s.get("kind") for s in t.get("schedule", [])}
        n = 0
        for row in data[tid].get("days", {}).get("rows", []):
            k = kinds.get(row.get("date"))
            if k in ("dive", "movedive"):
                n += 1
            row["plan"] = {"dive": "ダイビング%d日目" % n, "movedive": "移動＋ダイビング%d日目" % n, "move": "移動日", "free": "観光・休み"}.get(k, "")
    with open(out, "w", encoding="utf-8") as fp:
        json.dump({"trips": trips, "data": data}, fp, ensure_ascii=False, separators=(",", ":"))
    print(out, len(trips), "trips")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
