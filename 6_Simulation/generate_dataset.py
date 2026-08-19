#!/usr/bin/env python3
"""
STC Radar Simulation Verification Dataset Generator

Batch-runs multi-scenario simulations (range/velocity/azimuth sweeps,
multi-target and noise variants), extracts detection metrics and writes:

  dataset/scenarios/scene_XXX.json   per-scene metrics
  dataset/summary.csv                aggregated results
  dataset/manifest.json              dataset metadata

Usage:
  python generate_dataset.py [--limit N] [--seed 42] [--out dataset]
"""

import argparse
import csv
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stc_simulation import (  # noqa: E402
    array_factor_2d,
    generate_lfm_signal,
    pulse_compression,
    range_doppler_processing,
    simulate_target_echo,
)

# System parameters (kept in sync with stc_simulation.main)
C = 3e8
F0 = 10.5e9
BANDWIDTH = 100e6
PULSE_WIDTH = 10e-6
FS = 200e6
PRF = 10e3
N_PULSES = 64
RANGE_RES = C / (2 * BANDWIDTH)          # ~1.5 m
SPEED_RES = C / (2 * F0) * PRF / N_PULSES  # ~2.23 m/s
MAX_SPEED = C / (2 * F0) * PRF / 2       # unambiguous velocity ~71 m/s


def build_scenarios():
    """Return the full scenario list (>=40 scenes)."""
    scenarios = []
    for rng in [100, 200, 300, 500, 700, 1000]:
        for vel in [-50, -20, 0, 10, 20, 50, 60]:
            scenarios.append({
                "id": len(scenarios), "type": "grid",
                "range": rng, "velocity": vel, "azimuth": 30, "elevation": 0,
                "targets": [(rng, vel)], "snr_db": None,
            })
    for az in [-60, -30, 0, 60]:
        scenarios.append({
            "id": len(scenarios), "type": "azimuth",
            "range": 500, "velocity": 10, "azimuth": az, "elevation": 0,
            "targets": [(500, 10)], "snr_db": None,
        })
    scenarios.append({
        "id": len(scenarios), "type": "multi2",
        "range": None, "velocity": None, "azimuth": 30, "elevation": 0,
        "targets": [(500, 10), (800, -15)], "snr_db": None,
    })
    scenarios.append({
        "id": len(scenarios), "type": "multi3",
        "range": None, "velocity": None, "azimuth": 30, "elevation": 0,
        "targets": [(300, 20), (600, -5), (900, 35)], "snr_db": None,
    })
    for snr in [5, 10, 20]:
        for rng in [300, 700]:
            scenarios.append({
                "id": len(scenarios), "type": "noise",
                "range": rng, "velocity": 10, "azimuth": 30, "elevation": 0,
                "targets": [(rng, 10)], "snr_db": snr,
            })
    return scenarios


def add_noise(echo, snr_db, rng):
    """Add complex AWGN at the given SNR (dB); no-op if snr_db is None."""
    if snr_db is None:
        return echo
    active = echo[echo != 0]
    sig_pow = float(np.mean(np.abs(active) ** 2)) if active.size else 1.0
    noise_std = np.sqrt(sig_pow / 10 ** (snr_db / 10))
    noise = (rng.standard_normal(echo.shape)
             + 1j * rng.standard_normal(echo.shape)) / np.sqrt(2) * noise_std
    return echo + noise


def build_echo(lfm_signal, targets, rng=None):
    """Superpose echoes from all targets, optionally with noise.

    Non-coherent single-pulse model: Doppler phase applied within the
    pulse only (matches stc_simulation.simulate_target_echo).
    """
    echo = np.zeros_like(lfm_signal, dtype=complex)
    for (trange, tvel) in targets:
        echo += simulate_target_echo(lfm_signal, trange, tvel, C, FS)
    return echo


def build_echo_coherent(lfm_signal, targets, pulse_idx=0):
    """Coherent echo model for pulse-Doppler processing.

    Slow time p (pulse index) accumulates the cross-pulse Doppler phase
    exp(j*2*pi*fd*(p*PRI + t_fast)), which is required for velocity
    estimation via FFT across pulses.
    """
    n = len(lfm_signal)
    t_fast = np.arange(n) / FS
    pri = 1.0 / PRF
    echo = np.zeros(n, dtype=complex)
    for (trange, tvel) in targets:
        d = int(2 * trange / C * FS)
        if d >= n:
            continue
        fd = 2 * tvel * F0 / C
        phase = np.exp(1j * 2 * np.pi * fd * (pulse_idx * pri + t_fast))
        echo[d:] += lfm_signal[: n - d] * phase[d:] * 0.1
    return echo


def detect_peaks(profile_db, max_peaks=4, mask_radius=15):
    """Peak-pick on a dB range profile; returns [(index, peak_db), ...].

    mask_radius covers the LFM compressed mainlobe plus its near
    sidelobes so that only genuine targets are reported.
    """
    peaks = []
    work = profile_db.copy()
    for _ in range(max_peaks):
        idx = int(np.argmax(work))
        if work[idx] < -80:
            break
        peaks.append((idx, float(work[idx])))
        lo = max(0, idx - mask_radius)
        hi = min(len(work), idx + mask_radius + 1)
        work[lo:hi] = -np.inf
    return peaks


def estimate_velocity(data_matrix, range_bin, n_pulses=N_PULSES):
    """Doppler peak around the target range bin -> velocity (m/s)."""
    spec = np.fft.fftshift(np.fft.fft(data_matrix, axis=1), axes=1)
    row = int(np.clip(range_bin, 0, spec.shape[0] - 1))
    band = slice(max(0, row - 3), min(spec.shape[0], row + 4))
    sub = np.abs(spec[band, :])
    col = int(np.argmax(sub.ravel()) % n_pulses)
    freq = (col - n_pulses // 2) * PRF / n_pulses
    return freq * C / (2 * F0)


def run_scene(scene, rng):
    """Run one scene and return metrics dict."""
    t0 = time.time()
    lfm_t, lfm_signal = generate_lfm_signal(F0, BANDWIDTH, PULSE_WIDTH, FS)

    # Beam pattern for the scene's steering direction
    wavelength = C / F0
    theta = np.linspace(-60, 60, 121)
    phi = np.linspace(-60, 60, 121)
    af = array_factor_2d(theta, phi, scene["azimuth"], scene["elevation"],
                         wavelength)

    # Echo, noise, pulse compression
    echo = build_echo(lfm_signal, scene["targets"])
    echo = add_noise(echo, scene["snr_db"], rng)
    compressed = pulse_compression(echo, lfm_signal)
    profile_db = 20 * np.log10(np.abs(compressed) + 1e-10)

    # Range-Doppler (multi-pulse, coherent Doppler phase across pulses)
    data_matrix = np.zeros((len(compressed), N_PULSES), dtype=complex)
    for i in range(N_PULSES):
        echo_pulse = build_echo_coherent(lfm_signal, scene["targets"],
                                         pulse_idx=i)
        echo_pulse = add_noise(echo_pulse, scene["snr_db"], rng)
        data_matrix[:, i] = pulse_compression(echo_pulse, lfm_signal)

    # Metric extraction
    # Matched-filter 'same' mode adds a delay offset of
    # (n-1)-(n-1)//2 samples; compensate so peaks map to true range.
    n = len(compressed)
    delay_offset = (n - 1) - (n - 1) // 2
    meters_per_bin = C / (2 * FS)
    peaks = detect_peaks(profile_db)
    detected_ranges = [(int(idx) - delay_offset) * meters_per_bin
                       for (idx, _) in peaks]
    true_ranges = sorted(r for (r, _) in scene["targets"])

    # Window truncation note: echoes from targets farther than
    # ~750 m exceed the one-pulse receive window and lose lock.
    eff_bins = n - 1 - delay_offset
    window_truncated = [r > eff_bins * meters_per_bin for r in true_ranges]

    range_errors = []
    used = [False] * len(true_ranges)
    for dr in detected_ranges:
        best, best_err = None, 1e9
        for j, tr in enumerate(true_ranges):
            if used[j]:
                continue
            err = abs(dr - tr)
            if err < best_err:
                best, best_err = j, err
        if best is not None:
            used[best] = True
            range_errors.append(best_err)
        else:
            range_errors.append(1e9)
    range_errors = range_errors[: len(true_ranges)]

    pslr_db = None
    if len(peaks) >= 2:
        pslr_db = peaks[0][1] - peaks[1][1]
    elif peaks:
        # single peak: sidelobe max outside the mainlobe mask
        idx0 = peaks[0][0]
        mask = np.ones(len(profile_db), dtype=bool)
        lo = max(0, idx0 - 8)
        hi = min(len(profile_db), idx0 + 9)
        mask[lo:hi] = False
        if mask.any():
            pslr_db = peaks[0][1] - float(np.max(profile_db[mask]))

    # Velocity of the primary target
    true_vel = scene["targets"][0][1]
    det_vel = estimate_velocity(data_matrix, peaks[0][0] if peaks else 0)

    range_ok = all(e <= 3 * RANGE_RES for e in range_errors) and len(range_errors) == len(true_ranges)
    vel_ok = abs(det_vel - true_vel) <= 3 * SPEED_RES
    success = range_ok and vel_ok

    runtime = time.time() - t0
    return {
        "id": scene["id"],
        "type": scene["type"],
        "azimuth_deg": scene["azimuth"],
        "targets": scene["targets"],
        "snr_db": scene["snr_db"],
        "true_ranges_m": true_ranges,
        "detected_ranges_m": detected_ranges,
        "range_errors_m": range_errors,
        "detected_velocity_mps": det_vel,
        "true_velocity_mps": true_vel,
        "velocity_error_mps": det_vel - true_vel,
        "pslr_db": pslr_db,
        "range_resolution_m": RANGE_RES,
        "speed_resolution_mps": SPEED_RES,
        "window_truncated": window_truncated,
        "success": bool(success),
        "runtime_s": round(runtime, 2),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None,
                        help="max number of scenes to run (debug)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dataset"))
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    scenarios = build_scenarios()
    if args.limit:
        scenarios = scenarios[: args.limit]

    out_dir = args.out
    scenes_dir = os.path.join(out_dir, "scenarios")
    os.makedirs(scenes_dir, exist_ok=True)

    print(f"Running {len(scenarios)} scenes (seed={args.seed}) -> {out_dir}")
    rows = []
    for sc in scenarios:
        metrics = run_scene(sc, rng)
        fname = os.path.join(scenes_dir, f"scene_{sc['id']:03d}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        rows.append(metrics)
        print(f"  scene {sc['id']:03d} [{metrics['type']:8s}] "
              f"success={metrics['success']} "
              f"range_err={metrics['range_errors_m']} "
              f"vel_err={metrics['velocity_error_mps']:.2f} m/s")

    # summary.csv
    summary_path = os.path.join(out_dir, "summary.csv")
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "type", "azimuth_deg", "targets", "snr_db",
                      "true_ranges_m", "detected_ranges_m", "range_errors_m",
                      "detected_velocity_mps", "true_velocity_mps",
                      "velocity_error_mps", "pslr_db",
                      "range_resolution_m", "speed_resolution_mps",
                      "window_truncated", "success", "runtime_s"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # manifest.json
    n_ok = sum(1 for r in rows if r["success"])
    manifest = {
        "project": "PLFM-RIS-Enhanced",
        "generator": "6_Simulation/generate_dataset.py",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "seed": args.seed,
        "num_scenes": len(rows),
        "success_rate": round(n_ok / len(rows), 4) if rows else 0.0,
        "system_parameters": {
            "f0_hz": F0, "bandwidth_hz": BANDWIDTH,
            "pulse_width_s": PULSE_WIDTH, "fs_hz": FS,
            "prf_hz": PRF, "num_pulses": N_PULSES,
            "range_resolution_m": RANGE_RES,
            "speed_resolution_mps": SPEED_RES,
            "max_unambiguous_speed_mps": MAX_SPEED,
            "effective_max_range_m": C / (2 * FS) * (2001 - 1 - 1000),
        },
    }
    with open(os.path.join(out_dir, "manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Done: {len(rows)} scenes, success rate "
          f"{n_ok}/{len(rows)} ({100.0 * n_ok / len(rows):.1f}%)")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
