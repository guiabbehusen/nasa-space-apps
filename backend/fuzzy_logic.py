#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse, re
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union

import numpy as np
import pandas as pd

"""
Purpose (EN): Simple fuzzy classification (Good → Hazardous) for 1°×1° gridded emissions (SRES B2MESSAGE),
using scikit-fuzzy. For each gas (CO, NMVOC, NOx, CH4), we:
  1) convert cell totals to emission density (kg/km²·yr),
  2) compute dataset quantiles (Q10, Q35, Q65, Q85, Q97),
  3) build trapezoidal membership functions directly on these quantiles,
  4) pick the per-gas class by max membership (ties -> more severe),
  5) final label = worst class among gases present (precautionary rule).

Folder layout (default):
  backend/
    fuzzy_logic.py
    dataset/reactive-gases-grids/   <-- your .txt files

CLI example:
  python backend/fuzzy_logic.py --year 2030 --out backend/fuzzy_labels_2030.csv
"""


try:
    import skfuzzy as fuzz
except ImportError as e:
    raise SystemExit("scikit-fuzzy not installed. Install with: pip install scikit-fuzzy") from e

# -----------------------------
# Paths (robust defaults)
# -----------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_ROOT = (SCRIPT_DIR / "dataset" / "reactive-gases-grids").resolve()

# -----------------------------
# Parsing helpers
# -----------------------------
DATA_LINE = re.compile(
    r"^\s*([+-]?\d+(?:\.\d*)?)\s*,\s*([+-]?\d+(?:\.\d*)?)\s*,\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$"
)

UNIT_SCALE_KG = {"MT": 1e9, "TG": 1e9, "GG": 1e6, "KT": 1e6, "T": 1e3, "KG": 1.0}
GAS_CANON = {"CO":"CO","NOx":"NOx","NOX":"NOx","NO2":"NOx","NMVOC":"NMVOC","CH4":"CH4","CH_4":"CH4"}

CLASSES = ["Good","Moderate","USG","Unhealthy","Very Unhealthy","Hazardous"]
SEVERITY = {c:i for i,c in enumerate(CLASSES, start=1)}  # Good=1 ... Hazardous=6

EARTH_R_KM = 6371.0
DEG2RAD = np.pi/180.0

def norm_gas(g: str) -> str:
    return GAS_CANON.get(g.strip(), g.strip())

def unit_scale_from_units(units_line: str) -> float:
    if not units_line: return 1.0
    m = re.search(r"Units\s*:\s*([A-Za-z]+)", units_line, flags=re.I)
    if not m: return 1.0
    token = m.group(1)
    for k in ["MT","TG","GG","KT"]:
        if token.upper().startswith(k): return UNIT_SCALE_KG[k]
    if token.upper().startswith("KG"): return UNIT_SCALE_KG["KG"]
    if token.upper().startswith("T"):  return UNIT_SCALE_KG["T"]   # tonelada
    return 1.0

def parse_sres_file(fp: Path) -> pd.DataFrame:
    year, gas, units = None, None, None
    rows: List[Tuple[float,float,float]] = []
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if s.lower().startswith("year:"):
                m = re.search(r"Year\s*:\s*(\d{4})", s, flags=re.I)
                if m: year = int(m.group(1)); continue
            if s.lower().startswith("gas:"):
                m = re.search(r"Gas\s*:\s*([A-Za-z0-9_]+)", s, flags=re.I)
                if m: gas = norm_gas(m.group(1)); continue
            if s.lower().startswith("units:"):
                units = s; continue
            m = DATA_LINE.match(s)
            if m:
                lon, lat, val = float(m.group(1)), float(m.group(2)), float(m.group(3))
                rows.append((lon, lat, val))
    if not rows or year is None or gas is None:
        return pd.DataFrame(columns=["lon","lat","value","year","gas","unit_scale"])
    df = pd.DataFrame(rows, columns=["lon","lat","value"])
    df["year"] = year
    df["gas"] = gas
    df["unit_scale"] = unit_scale_from_units(units)
    return df

def load_folder(root: Path) -> pd.DataFrame:
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(f"Data folder not found: {root} (resolved: {root.resolve()})")
    patterns = ["*.txt","*.dat","*.csv","*.asc","*.TXT","*.DAT","*.CSV","*.ASC"]
    parts = []
    files = []
    for ext in patterns:
        files += list(root.rglob(ext))
    if not files:
        files = list(root.rglob("*"))
    for fp in files:
        try:
            df = parse_sres_file(fp)
            if not df.empty:
                parts.append(df)
        except Exception:
            pass
    if not parts:
        raise FileNotFoundError(f"No SRES-like data parsed under: {root} (resolved: {root.resolve()})")
    print(f"[info] Parsed {len(parts)} files from {root.resolve()}")
    return pd.concat(parts, ignore_index=True)

def cell_area_km2(lat_ll: np.ndarray, lon_ll: np.ndarray) -> np.ndarray:
    lat1 = np.clip(lat_ll, -90.0, 90.0); lat2 = np.clip(lat_ll+1.0, -90.0, 90.0)
    phi1, phi2 = lat1*DEG2RAD, lat2*DEG2RAD
    lam1, lam2 = lon_ll*DEG2RAD, (lon_ll+1.0)*DEG2RAD
    return (EARTH_R_KM**2) * np.abs(np.sin(phi2)-np.sin(phi1)) * np.abs(lam2-lam1)

# -----------------------------
# Fuzzy helpers (skfuzzy)
# -----------------------------
def _mk_trap(a,b,c,d):
    """Ensure strictly increasing trapezoid params."""
    eps = 1e-12
    b = max(b, a + eps)
    c = max(c, b + eps)
    d = max(d, c + eps)
    return [a,b,c,d]

def build_traps_from_quantiles(minv, q10, q35, q65, q85, q97, maxv, smooth_frac=0.05):
    """Return trapezoid params for the 6 classes based on quantiles."""
    # Smoothing deltas
    width = max(maxv - minv, 1e-12)
    d = smooth_frac * width

    traps = {
        "Good":          _mk_trap(minv, minv, q10, q10 + d),
        "Moderate":      _mk_trap(q10 - d, q10, q35, q35 + d),
        "USG":           _mk_trap(q35 - d, q35, q65, q65 + d),
        "Unhealthy":     _mk_trap(q65 - d, q65, q85, q85 + d),
        "Very Unhealthy":_mk_trap(q85 - d, q85, q97, q97 + d),
        "Hazardous":     _mk_trap(q97 - d, q97, maxv, maxv),
    }
    # Clamp to [minv, maxv]
    for k, arr in traps.items():
        arr[0] = max(arr[0], minv)
        arr[1] = max(arr[1], minv)
        arr[2] = min(arr[2], maxv)
        arr[3] = min(arr[3], maxv + 1e-9)
        traps[k] = _mk_trap(*arr)
    return traps

def memberships_matrix(x: np.ndarray, traps: Dict[str, List[float]]) -> np.ndarray:
    """Return (n_samples, 6) matrix of memberships in CLASSES order."""
    mats = []
    for cls in CLASSES:
        a,b,c,d = traps[cls]
        mats.append(fuzz.trapmf(x, [a,b,c,d]))
    return np.vstack(mats).T  # shape (n,6)

# -----------------------------
# Core pipeline
# -----------------------------
def run(
    *,
    root: Optional[Union[str, Path]] = None,
    out: Optional[Union[str, Path]] = None,
    min_year: int = 2000,
    max_year: int = 2030,
    year: Optional[int] = None,
    smooth: float = 0.05,  # fraction of (max-min) for trapezoid shoulders
):
    root = Path(root) if root else DEFAULT_DATA_ROOT
    out = Path(out) if out else (SCRIPT_DIR / "fuzzy_labels.csv")
    print(f"[info] Using data root: {root.resolve()}")
    print(f"[info] Output file    : {out.resolve()}")

    df = load_folder(root)
    df = df[(df["year"]>=min_year) & (df["year"]<=max_year)].copy()
    df["gas"] = df["gas"].map(lambda g: GAS_CANON.get(g, g))
    df = df[df["gas"].isin(["CO","NMVOC","NOx","CH4"])].copy()
    if year is not None:
        df = df[df["year"]==year].copy()
        if df.empty:
            raise RuntimeError(f"No data for year {year} in range [{min_year},{max_year}].")

    # Emission density (kg/km²·yr)
    vals_kg = df["value"].astype(float) * df["unit_scale"].astype(float)
    area = cell_area_km2(df["lat"].to_numpy(), df["lon"].to_numpy())
    area = np.where(area<=0, 1e-9, area)
    df["dens_kgkm2"] = vals_kg / area

    out_blocks = []
    for g, gdf in df.groupby("gas", sort=False):
        x = gdf["dens_kgkm2"].to_numpy()

        # Quantiles for this gas (global over selected years)
        q = np.quantile(x, [0.10, 0.35, 0.65, 0.85, 0.97])
        q10, q35, q65, q85, q97 = q
        minv, maxv = float(np.min(x)), float(np.max(x))
        # handle degenerate spreads
        if not np.isfinite(minv) or not np.isfinite(maxv) or np.isclose(minv, maxv):
            minv, maxv = minv, minv + 1.0

        traps = build_traps_from_quantiles(minv, q10, q35, q65, q85, q97, maxv, smooth_frac=smooth)
        mus = memberships_matrix(x, traps)  # (n,6) in CLASSES order

        # Per-row label = max membership (ties -> most severe)
        idx_max = np.argmax(mus, axis=1)
        labels = []
        for i, row in enumerate(mus):
            mx = row[idx_max[i]]
            ties = np.where(np.abs(row - mx) < 1e-12)[0]
            labels.append(CLASSES[int(np.max(ties))])  # more severe on tie

        gdf = gdf.assign(**{f"{g}_label": labels})
        out_blocks.append(gdf[["lon","lat","year",f"{g}_label"]])

    # Merge labels from all gases
    out_df = None
    for block in out_blocks:
        if out_df is None:
            out_df = block.copy()
        else:
            out_df = out_df.merge(block, on=["lon","lat","year"], how="outer")

    # Final decision = worst class among gases present
    def worst_class(row):
        sev = []
        for g in ["CO","NMVOC","NOx","CH4"]:
            lab = row.get(f"{g}_label")
            if isinstance(lab, str) and lab in SEVERITY:
                sev.append(SEVERITY[lab])
        if not sev: return "Good"
        worst = max(sev)
        # map back
        for cls, s in SEVERITY.items():
            if s == worst:
                return cls
        return "Good"

    out_df["final_label"] = out_df.apply(worst_class, axis=1)
    out_df = out_df.sort_values(["year","lat","lon"]).reset_index(drop=True)

    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out, index=False)
    print(f"[OK] Saved: {out.resolve()}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_DATA_ROOT),
                    help="Data folder (default: backend/dataset/reactive-gases-grids relative to this file).")
    ap.add_argument("--out",  default=str(SCRIPT_DIR / "fuzzy_labels.csv"), help="Output CSV path.")
    ap.add_argument("--min-year", type=int, default=2000)
    ap.add_argument("--max-year", type=int, default=2030)
    ap.add_argument("--year", type=int, default=None, help="If set, classify only this year.")
    ap.add_argument("--smooth", type=float, default=0.05, help="Shoulder width as fraction of (max-min).")
    args = ap.parse_args()

    run(root=args.root, out=args.out, min_year=args.min_year, max_year=args.max_year,
        year=args.year, smooth=args.smooth)

if __name__ == "__main__":
    main()
