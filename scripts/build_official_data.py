"""Download and validate three official Malaysian datasets. Python 3.10+, stdlib only.
Creates a new immutable run folder. Does NOT generate tourism exposure, AI scores,
vacancies or individual income losses. No synthetic data and no silent fallback.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import tempfile
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

PILOTS = {
    ("Terengganu", "Besut"), ("Terengganu", "Kuala Nerus"),
    ("Terengganu", "Marang"), ("Pahang", "Rompin")
}
SOURCES = {
    "lfs": ("https://storage.dosm.gov.my/labour/lfs_district.csv",
            "https://data.gov.my/data-catalogue/lfs_district",
            ["state", "district", "date", "lf", "lf_employed", "u_rate"]),
    "income": ("https://storage.dosm.gov.my/hies/hh_income_district.csv",
               "https://data.gov.my/data-catalogue/hh_income_district",
               ["state", "district", "date", "income_mean", "income_median"]),
    "fish": ("https://storage.data.gov.my/agriculture/fish_landings.csv",
             "https://data.gov.my/data-catalogue/fish_landings",
             ["date", "coast", "state", "landings"]),
}

def number(value, label):
    try:
        n = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Missing/non-numeric {label}: {value!r}") from exc
    if not math.isfinite(n) or n < 0:
        raise ValueError(f"Invalid {label}: {value!r}")
    return n

def write_csv(path, rows, fields):
    with path.open("x", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def read_source(key, raw_dir, as_of):
    url, landing, required = SOURCES[key]
    request = urllib.request.Request(url, headers={"User-Agent": "MonsunBridge-OfficialData/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = response.read()
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    if not set(required).issubset(reader.fieldnames or []):
        raise ValueError(f"{key}: schema drift: expected {required}, got {reader.fieldnames}")
    rows = list(reader)
    if not rows:
        raise ValueError(f"{key}: empty official CSV")
    for row in rows:
        row_date = date.fromisoformat(row["date"])
        if row_date > as_of:
            raise ValueError(f"{key}: observation after study cutoff: {row_date}")
    with (raw_dir / (key + ".csv")).open("xb") as f:
        f.write(payload)
    return rows, {
        "dataset": key, "url": url, "landing_page": landing, "license": "CC BY 4.0",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(payload).hexdigest(), "row_count": len(rows),
        "observation_min": min(r["date"] for r in rows),
        "observation_max": max(r["date"] for r in rows),
        "columns": reader.fieldnames
    }

def latest_common_pilots(rows):
    by_district = defaultdict(dict)
    for r in rows:
        key = (r["state"], r["district"])
        if key in PILOTS:
            if r["date"] in by_district[key]:
                raise ValueError(f"Duplicate district-date: {key} {r['date']}")
            by_district[key][r["date"]] = r
    if set(by_district) != PILOTS:
        raise ValueError(f"Missing pilot districts: {PILOTS - set(by_district)}")
    shared = set.intersection(*(set(by_district[k]) for k in PILOTS))
    if not shared:
        raise ValueError("No common publication year across all pilot districts")
    chosen = max(shared)
    return [by_district[k][chosen] for k in sorted(PILOTS)]

def build(output, as_of):
    output.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="official_", dir=output))
    raw_dir, processed = run / "raw", run / "processed"
    raw_dir.mkdir()
    processed.mkdir()
    manifest = []
    try:
        data = {}
        for key in SOURCES:
            data[key], record = read_source(key, raw_dir, as_of)
            manifest.append(record)
        labour = []
        for r in latest_common_pilots(data["lfs"]):
            lf = number(r["lf"], "lf")
            employed = number(r["lf_employed"], "lf_employed")
            rate = number(r["u_rate"], "u_rate")
            if employed > lf + 0.2 or rate > 100:
                raise ValueError("Labour bounds inconsistent beyond rounding tolerance")
            labour.append({
                "state": r["state"], "district": r["district"], "date": r["date"],
                "labour_force_thousands": lf, "employed_thousands": employed,
                "unemployment_rate_pct": rate, "evidence_level": "OBSERVED",
                "source_url": SOURCES["lfs"][1]
            })
        write_csv(processed / "official_lfs.csv", labour, list(labour[0]))
        income = []
        for r in latest_common_pilots(data["income"]):
            income.append({
                "state": r["state"], "district": r["district"], "date": r["date"],
                "income_mean_rm": number(r["income_mean"], "income_mean"),
                "income_median_rm": number(r["income_median"], "income_median"),
                "evidence_level": "OBSERVED", "source_url": SOURCES["income"][1]
            })
        write_csv(processed / "official_income.csv", income, list(income[0]))
        fish_by_state = defaultdict(dict)
        for r in data["fish"]:
            if r["state"] in {"Terengganu", "Pahang"} and r["coast"] == "east":
                d = date.fromisoformat(r["date"])
                if d in fish_by_state[r["state"]]:
                    raise ValueError(f"Duplicate state-month-coast fish row: {r}")
                fish_by_state[r["state"]][d] = number(r["landings"], "landings")
        complete = {}
        for state in ("Terengganu", "Pahang"):
            grouped = defaultdict(set)
            for d in fish_by_state[state]:
                grouped[d.year].add(d.month)
            complete[state] = {y for y, months in grouped.items() if months == set(range(1, 13))}
        years = complete["Terengganu"] & complete["Pahang"]
        if not years:
            raise ValueError("No common complete 12-month fish year. Do not interpolate.")
        fish_year = max(years)
        fish_rows = []
        for state in ("Terengganu", "Pahang"):
            for d, value in sorted(fish_by_state[state].items()):
                if d.year == fish_year:
                    fish_rows.append({
                        "state": state, "date": d.isoformat(), "month": d.month,
                        "landings_mt": value, "evidence_level": "OBSERVED",
                        "source_url": SOURCES["fish"][1]
                    })
        write_csv(processed / "official_fish.csv", fish_rows, list(fish_rows[0]))
        status = {
            "download_and_validation": "PASSED", "submission_ready": False,
            "study_cutoff": as_of.isoformat(), "sources": manifest,
            "labour_snapshot": labour[0]["date"], "income_snapshot": income[0]["date"],
            "fish_complete_year": fish_year,
            "blockers": [
                "National quarterly tourism observations and source-level citations not integrated",
                "Tourism dependency and occupation allocation not validated",
                "Target-specific official occupational text and AI pipeline not validated",
                "No observed vacancies or employer-confirmed training/placement capacity",
                "Power BI Desktop refresh/render/offline tests pending"
            ]
        }
        (run / "BUILD_STATUS.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
        (run / "POWER_BI_FOLDER.txt").write_text(str(processed.resolve()), encoding="utf-8")
        print("Official inputs validated. Set OfficialDataFolder to:")
        print(processed.resolve())
        print("This is an official-data foundation, NOT a submission-ready full model.")
        return run
    except Exception as exc:
        (run / "BUILD_FAILED.txt").write_text(str(exc), encoding="utf-8")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/official_runs"))
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    build(args.output, args.as_of)
