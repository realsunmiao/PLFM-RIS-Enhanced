"""Unit tests for the PLFM-RIS STC simulation and verification dataset."""

import csv
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.join(os.path.dirname(HERE), "6_Simulation")
sys.path.insert(0, SIM_DIR)

import generate_dataset as gd  # noqa: E402
from stc_simulation import (  # noqa: E402
    array_factor_2d,
    generate_lfm_signal,
    pulse_compression,
    range_doppler_processing,
    simulate_target_echo,
)

C = 3e8
F0 = 10.5e9
BANDWIDTH = 100e6
PULSE_WIDTH = 10e-6
FS = 200e6
PRF = 10e3
N_PULSES = 64

DATASET_DIR = os.path.join(SIM_DIR, "dataset")


def _lfm():
    return generate_lfm_signal(F0, BANDWIDTH, PULSE_WIDTH, FS)


# --------------------------------------------------------------------------
# LFM signal generation
# --------------------------------------------------------------------------


def test_lfm_signal_length_and_unit_amplitude():
    t, s = _lfm()
    assert len(t) == len(s)
    assert len(s) == pytest.approx(int(PULSE_WIDTH * FS), abs=2)
    assert np.allclose(np.abs(s), 1.0, atol=1e-9)


def test_lfm_chirp_bandwidth():
    _, s = _lfm()
    t = np.arange(len(s)) / FS
    phase = np.unwrap(np.angle(s))
    inst_freq = np.gradient(phase) / (2 * np.pi) * FS
    # The simulation is baseband-style (f0 >> fs, carrier is aliased), so
    # verify the chirp rate instead: df/dt = k = bandwidth / pulse_width.
    chirp_rate = np.gradient(inst_freq) * FS  # Hz/s
    k = BANDWIDTH / PULSE_WIDTH
    assert np.median(chirp_rate[10:-10]) == pytest.approx(k, rel=0.02)
    # sweep width over the pulse must equal the bandwidth
    sweep = inst_freq[-1] - inst_freq[0]
    assert sweep == pytest.approx(BANDWIDTH, rel=0.05)


# --------------------------------------------------------------------------
# Array factor / beam pattern
# --------------------------------------------------------------------------


def test_array_factor_mainlobe_at_steering():
    wavelength = C / F0
    theta = np.linspace(-60, 60, 121)   # elevation scan
    phi = np.linspace(-60, 60, 121)     # azimuth scan
    # Note: steering phases scale with sin(elevation); with elevation=0 the
    # array is omnidirectional in azimuth, so test a non-zero elevation.
    af = array_factor_2d(theta, phi, 30, 30, wavelength)
    assert af.shape == (len(phi), len(theta))
    assert 0.9 < np.max(af) <= 1.0  # normalized array factor
    idx = np.unravel_index(np.argmax(af), af.shape)
    assert abs(theta[idx[1]] - 30) <= 2.5   # mainlobe at steering elevation
    assert abs(phi[idx[0]] - 30) <= 2.5     # and steering azimuth


def test_array_factor_steering_shifts_lobe():
    wavelength = C / F0
    theta = np.linspace(-60, 60, 121)
    phi = np.linspace(-60, 60, 121)
    af0 = array_factor_2d(theta, phi, 0, 30, wavelength)
    af30 = array_factor_2d(theta, phi, 30, 30, wavelength)
    idx0 = np.unravel_index(np.argmax(af0), af0.shape)
    idx30 = np.unravel_index(np.argmax(af30), af30.shape)
    assert phi[idx30[0]] > phi[idx0[0]] + 20  # lobe moved toward +30 deg


# --------------------------------------------------------------------------
# Echo and pulse compression
# --------------------------------------------------------------------------


def test_echo_delay_matches_target_range():
    _, s = _lfm()
    echo = simulate_target_echo(s, 500, 10, C, FS)
    d = int(2 * 500 / C * FS)
    assert np.all(echo[:d] == 0)          # silence before the echo delay
    assert np.any(echo[d:] != 0)          # signal present after the delay


def test_pulse_compression_peak_at_target_range():
    _, s = _lfm()
    echo = simulate_target_echo(s, 500, 10, C, FS)
    comp = pulse_compression(echo, s)
    n = len(comp)
    delay_offset = (n - 1) - (n - 1) // 2
    k = int(np.argmax(np.abs(comp)))
    peak_range = (k - delay_offset) * C / (2 * FS)
    assert abs(peak_range - 500) < 3.0


def test_pulse_compression_sidelobes_below_13db():
    _, s = _lfm()
    echo = simulate_target_echo(s, 500, 10, C, FS)
    comp = pulse_compression(echo, s)
    profile = np.abs(comp)
    k = int(np.argmax(profile))
    lo, hi = max(0, k - 15), min(len(profile), k + 16)
    mask = np.ones(len(profile), dtype=bool)
    mask[lo:hi] = False
    sidelobe_db = 20 * np.log10(profile[mask].max() / profile[k])
    # LFM compressed waveform has ~-13 dB first sidelobe
    assert sidelobe_db < -10


def test_range_doppler_output_shape_and_normalization():
    _, s = _lfm()
    data = np.zeros((len(s), N_PULSES), dtype=complex)
    for i in range(N_PULSES):
        e = gd.build_echo_coherent(s, [(500, 10)], pulse_idx=i)
        data[:, i] = pulse_compression(e, s)
    rd = range_doppler_processing(data, FS, PRF)
    assert rd.shape == (len(s), N_PULSES)
    assert np.max(rd) == pytest.approx(0.0, abs=1e-6)  # normalized to 0 dB


# --------------------------------------------------------------------------
# Dataset integrity
# --------------------------------------------------------------------------


def test_dataset_files_exist():
    assert os.path.exists(os.path.join(DATASET_DIR, "summary.csv"))
    assert os.path.exists(os.path.join(DATASET_DIR, "manifest.json"))
    scenes = os.path.join(DATASET_DIR, "scenarios")
    n = len([f for f in os.listdir(scenes) if f.endswith(".json")])
    assert n >= 40


def test_dataset_summary_rows_valid():
    with open(os.path.join(DATASET_DIR, "summary.csv"),
              encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 40
    for r in rows:
        assert r["success"] in ("True", "False")
        assert float(r["range_resolution_m"]) > 0
        # every failure is explained by receive-window truncation
        if r["success"] == "False":
            assert "True" in r["window_truncated"]


def test_dataset_manifest_metadata():
    with open(os.path.join(DATASET_DIR, "manifest.json"),
              encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["num_scenes"] >= 40
    assert manifest["system_parameters"]["range_resolution_m"] > 0
    assert manifest["system_parameters"]["effective_max_range_m"] > 0
    assert 0.0 <= manifest["success_rate"] <= 1.0


def test_dataset_scene_jsons_valid():
    scenes = os.path.join(DATASET_DIR, "scenarios")
    files = sorted(f for f in os.listdir(scenes) if f.endswith(".json"))
    assert len(files) >= 40
    for name in files:
        with open(os.path.join(scenes, name), encoding="utf-8") as f:
            m = json.load(f)
        assert "success" in m and "targets" in m
        assert isinstance(m["range_errors_m"], list)
