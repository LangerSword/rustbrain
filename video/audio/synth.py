#!/usr/bin/env python3
"""Synthesize the rustbrain demo video audio stems.

Engine: numpy plus the stdlib wave module. No sampled audio, no third party
audio libraries, no voice: every sample is computed here. Deterministic
(fixed seed), 48000 Hz, stereo, 16 bit signed PCM.

Outputs
  out/video/audio/music.wav   186 s slow ambient pad, no melody, no drums
  out/video/audio/sfx.wav     186 s sparse soft events (cut sweeps, caption ticks)
  out/video/audio/premix.wav  music + sfx, mastered to about -16 LUFS / under -1 dBTP

The mastering stage measures the file with ffmpeg (loudnorm print_format=json)
and iterates its gain so the integrated loudness lands on the target instead of
being guessed. If ffmpeg is unavailable the script falls back to an internal
K-weighted estimate and says so.

Run:  python3 video/audio/synth.py
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np

SR = 48000
DUR = 186.0
N = int(round(DUR * SR))
SEED = 20261019

HERE = os.path.dirname(os.path.abspath(__file__))          # video/audio
ROOT = os.path.dirname(os.path.dirname(HERE))              # repo root
OUT = os.path.join(ROOT, "out", "video", "audio")

TARGET_I = -16.0        # LUFS integrated
TARGET_TP = -1.0        # dBTP ceiling to stay under
TOL_I = 0.2             # LU tolerance on the integrated measurement

# edit points from the storyboard: cuts and caption arrivals (seconds)
CUTS = [12.0, 30.0, 65.0, 110.0, 135.0, 160.0]
CAPTIONS = [0.0, 3.0, 12.0, 17.0, 30.0, 40.0, 50.0, 57.0, 65.0, 80.0,
            92.0, 102.0, 110.0, 120.0, 128.0, 135.0, 146.0, 152.0,
            160.0, 168.0]

SWEEP_PEAK_DB = -22.0   # absolute, before master gain
CLICK_PEAK_DB = -24.0   # absolute: audible in its own band over the pad,
                        # still about 20 dB under the pad's own peak
MUSIC_PEAK_DB = -6.0    # pad normalised to this before mixing

# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def midi_to_freq(m: float) -> float:
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


def db_to_lin(db: float) -> float:
    return 10.0 ** (db / 20.0)


def slope(u: np.ndarray) -> np.ndarray:
    """Raised cosine fade in [0, 1], zero derivative at both ends."""
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(u, 0.0, 1.0))


def write_wav(path: str, audio: np.ndarray, rng: np.random.Generator) -> None:
    """audio: (2, n) float64 in [-1, 1] -> 16 bit PCM with TPDF dither."""
    n = audio.shape[1]
    dither = (rng.random((2, n)) - rng.random((2, n))) * (0.5 / 32768.0)
    x = np.clip(audio + dither, -1.0, 1.0)
    inter = np.empty((n, 2), dtype="<i2")
    inter[:, 0] = np.round(x[0] * 32767.0).astype("<i2")
    inter[:, 1] = np.round(x[1] * 32767.0).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(inter.tobytes())


def read_wav(path: str) -> np.ndarray:
    with wave.open(path, "rb") as w:
        if w.getnchannels() != 2 or w.getsampwidth() != 2:
            raise RuntimeError(f"{path}: expected stereo 16 bit")
        n = w.getnframes()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return np.ascontiguousarray(a.reshape(-1, 2).T)


# ---------------------------------------------------------------------------
# music: slow ambient pad
# ---------------------------------------------------------------------------

# F major / A minor / C major family, roots low, top note under 400 Hz so the
# pad never sits in the voiceover's presence band. One chord every 15 s.
CHORDS = [
    [45, 52, 57, 60, 64],   # Am
    [41, 48, 53, 57, 60],   # F
    [48, 55, 60, 64],       # C
    [43, 50, 55, 59, 62],   # G
    [45, 52, 57, 64],       # Am
    [50, 57, 62, 65],       # Dm
    [46, 53, 58, 62],       # Bb
    [41, 48, 57, 60],       # F
    [48, 55, 64, 67],       # C
    [45, 52, 57, 64],       # Am
    [41, 48, 53, 57],       # F
    [48, 55, 60, 64, 67],   # C
    [45, 52, 57, 60],       # Am
]
SEG = 15.0      # chord length
XF = 4.0        # equal power crossfade between chords


def voice(f: float, tt: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """One soft pad voice: detuned sine pair plus two quiet upper partials,
    breathing under its own slow LFO."""
    lfo_rate = rng.uniform(0.028, 0.082)
    lfo_phase = rng.uniform(0.0, 2.0 * math.pi)
    lfo_depth = rng.uniform(0.07, 0.15)
    p1, p2, p3 = rng.uniform(0.0, 2.0 * math.pi, 3)
    det = rng.uniform(0.0008, 0.0018) * (1.0 if rng.random() < 0.5 else -1.0)
    w = 2.0 * math.pi * f * tt
    s = (0.50 * np.sin(w + p1)
         + 0.50 * np.sin(2.0 * math.pi * f * (1.0 + det) * tt + p2)
         + 0.15 * np.sin(2.0 * w + p3)
         + 0.05 * np.sin(3.0 * w + 1.7))
    breath = (1.0 - lfo_depth) + lfo_depth * np.sin(
        2.0 * math.pi * lfo_rate * tt + lfo_phase)
    return s * breath


def render_pad(rng: np.random.Generator) -> np.ndarray:
    out = np.zeros((2, N), dtype=np.float64)
    for k, notes in enumerate(CHORDS):
        t0 = k * SEG
        i0 = int(max(0, round((t0 - XF) * SR)))
        i1 = int(min(N, round((t0 + SEG + XF) * SR)))
        if i0 >= i1:
            break
        tt = np.arange(i0, i1, dtype=np.float64) / SR - t0
        env = np.ones_like(tt)
        m = tt < 0.0
        env[m] = np.sqrt(slope((tt[m] + XF) / XF))          # equal power in
        m = tt >= SEG
        env[m] = np.sqrt(slope(1.0 - (tt[m] - SEG) / XF))   # equal power out
        for j, note in enumerate(notes):
            f = midi_to_freq(note)
            sig = voice(f, tt, rng) * env * (1.0 / (1.0 + 0.22 * j))
            pan = rng.uniform(-0.72, 0.72)
            th = (pan + 1.0) * math.pi / 4.0
            out[0, i0:i1] += sig * math.cos(th)
            out[1, i0:i1] += sig * math.sin(th)
        del tt, env
    return out


def air_layer(rng: np.random.Generator) -> np.ndarray:
    """Very quiet pink-ish room tone, so the pad is not a bare sine stack."""
    white = rng.standard_normal((2, N))
    f = np.fft.rfftfreq(N, 1.0 / SR)
    shape = (1.0 / np.sqrt(1.0 + (f / 400.0) ** 2)
             * 1.0 / np.sqrt(1.0 + (f / 6000.0) ** 4))
    shape[f < 1.0] = 0.0
    y = np.fft.irfft(np.fft.rfft(white, axis=1) * shape, n=N, axis=1)
    del white
    y /= (np.sqrt(np.mean(y ** 2, axis=1, keepdims=True)) + 1e-12)
    t = np.arange(N, dtype=np.float64) / SR
    lfo = 1.0 + 0.35 * np.sin(2.0 * math.pi * 0.023 * t + 0.7)
    return y * db_to_lin(-46.0) * lfo


def shape_pair(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Static pad shaping: high pass, small presence dip, and two tilt curves
    (dark and bright) that get crossfaded slowly for filter-like motion."""
    n = x.shape[0]
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    hp = (f / 28.0) ** 2 / (1.0 + (f / 28.0) ** 2)
    dip = 1.0 - 0.18 * np.exp(
        -0.5 * ((np.log2(np.maximum(f, 1.0)) - 11.1) / 0.8) ** 2)
    base = hp * dip
    dark = base / np.sqrt(1.0 + (f / 2000.0) ** 4)
    bright = base / np.sqrt(1.0 + (f / 5500.0) ** 4)
    a = np.fft.irfft(X * dark, n=n)
    b = np.fft.irfft(X * bright, n=n)
    return a, b


def render_music(rng: np.random.Generator) -> np.ndarray:
    pad = render_pad(rng)
    pad += air_layer(rng)
    t = np.arange(N, dtype=np.float64) / SR
    # one shared dark/bright morph, skewed a few seconds between channels,
    # then a constant power stereo rotation: the image drifts, the level does not
    morph_rate = 0.0165
    morph_phase = rng.uniform(0.0, 2.0 * math.pi)
    skew = 0.25
    music = np.empty((2, N), dtype=np.float64)
    for ch in range(2):
        dark, bright = shape_pair(pad[ch])
        m = 0.5 + 0.30 * np.sin(
            2.0 * math.pi * morph_rate * t + morph_phase + skew * (2 * ch - 1))
        music[ch] = dark * (1.0 - m) + bright * m
        del dark, bright
    del pad
    rot = 0.15 * np.sin(2.0 * math.pi * 0.0131 * t + rng.uniform(0.0, 2.0 * math.pi))
    music[0] *= np.cos(math.pi / 4.0 + rot)
    music[1] *= np.sin(math.pi / 4.0 + rot)
    # global slow level drift
    music *= 1.0 + 0.05 * np.sin(2.0 * math.pi * 0.037 * t + 1.1)
    # match the two channels' long term rms (no constant left/right lean)
    rl = math.sqrt(float(np.mean(music[0] ** 2)))
    rr = math.sqrt(float(np.mean(music[1] ** 2)))
    trim = 20.0 * math.log10(rl / rr)
    music[0] *= db_to_lin(-trim / 2.0)
    music[1] *= db_to_lin(trim / 2.0)
    # clean ends: no pop at the file edges
    fade_in = int(2.0 * SR)
    music[:, :fade_in] *= slope(np.arange(fade_in) / fade_in)
    fade_out = int(7.0 * SR)
    idx = np.arange(fade_out)
    music[:, N - fade_out:] *= slope(1.0 - idx / fade_out)
    peak = float(np.max(np.abs(music)))
    music *= db_to_lin(MUSIC_PEAK_DB) / peak
    return music


# ---------------------------------------------------------------------------
# sfx: cut sweeps and caption ticks
# ---------------------------------------------------------------------------


def sweep_event(rng: np.random.Generator, dur: float = 0.35) -> np.ndarray:
    """Soft filtered noise sweep: band rises then falls, envelope gentle on
    both ends. 2 pole state variable filter, cutoff swept per sample. The band
    sits above the pad's harmonics (which stop near 1.2 kHz) so the sweep is
    not masked, and it stays under 5 kHz so it reads as air, not as a whoosh."""
    n = int(round(dur * SR))
    u = np.linspace(0.0, 1.0, n, endpoint=False)
    env = np.sin(np.pi * u) ** 1.6
    fc = 1000.0 + (4200.0 - 1000.0) * np.sin(np.pi * u) ** 0.9
    noise = rng.standard_normal(n)
    out = np.empty(n, dtype=np.float64)
    q1 = 1.0 / 0.7
    low = 0.0
    band = 0.0
    for i in range(n):
        g = 2.0 * math.sin(math.pi * fc[i] / SR)
        high = noise[i] - low - q1 * band
        band += g * high
        low += g * band
        out[i] = band
    out *= env
    out /= (np.max(np.abs(out)) + 1e-12)
    return out


def click_event(rng: np.random.Generator, dur: float = 0.025) -> np.ndarray:
    """Very soft caption tick: short high ping with a fast decay and a 1.5 ms
    attack, so its own first sample is exactly zero."""
    n = int(round(dur * SR))
    t = np.arange(n, dtype=np.float64) / SR
    atk = np.clip(t / 0.0015, 0.0, 1.0)
    dec = np.exp(-t / 0.006)
    body = np.sin(2.0 * math.pi * 1900.0 * t) + 0.3 * np.sin(
        2.0 * math.pi * 3800.0 * t)
    tick = rng.standard_normal(n) * 0.25 * np.exp(-t / 0.0025)
    tail = np.ones(n)
    ramp = int(0.004 * SR)
    tail[n - ramp:] = np.linspace(1.0, 0.0, ramp)
    out = (body * dec + tick) * atk * tail
    out /= (np.max(np.abs(out)) + 1e-12)
    return out


def render_sfx(rng: np.random.Generator) -> np.ndarray:
    out = np.zeros((2, N), dtype=np.float64)
    for t0 in CUTS:                      # sweep centred on the cut
        ev = sweep_event(rng) * db_to_lin(SWEEP_PEAK_DB)
        i0 = int(round((t0 - len(ev) / 2.0 / SR) * SR))
        out[0, i0:i0 + len(ev)] += ev * rng.uniform(0.9, 1.0)
        out[1, i0:i0 + len(ev)] += ev * rng.uniform(0.9, 1.0)
    for t0 in CAPTIONS:                  # tick starts at the caption
        ev = click_event(rng) * db_to_lin(CLICK_PEAK_DB)
        i0 = int(round(t0 * SR))
        out[0, i0:i0 + len(ev)] += ev * rng.uniform(0.85, 1.0)
        out[1, i0:i0 + len(ev)] += ev * rng.uniform(0.85, 1.0)
    return out


# ---------------------------------------------------------------------------
# mastering
# ---------------------------------------------------------------------------


def soft_limit(x: np.ndarray, ceiling: float) -> np.ndarray:
    """Lookahead style limiter: sliding peak envelope, smoothed gain curve.
    Only intended to catch the odd peak, not to squash the pad."""
    env = np.abs(x)
    dec = 16
    n = env.shape[1]
    pad_n = (-n) % dec
    if pad_n:
        env = np.concatenate([env, np.zeros((2, pad_n))], axis=1)
    env = env.reshape(2, -1, dec).max(axis=2)          # envelope at SR/dec
    gain = np.minimum(1.0, ceiling / (env + 1e-12))
    k = 18                                             # ~6 ms at 3 kHz
    win = np.hanning(2 * k + 1)
    win /= win.sum()
    m = gain.shape[1]
    padded = np.concatenate([gain, np.full((2, k), gain[:, -1:])], axis=1)
    gain = np.apply_along_axis(
        lambda v: np.convolve(v, win, mode="same")[:m], 1, padded)[:, :m]
    gain = np.repeat(gain, dec, axis=1)[:, :n]
    return x * gain


def measure_loudness(path: str) -> dict | None:
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
           "loudnorm=I=-16:TP=-1.0:LRA=11:print_format=json",
           "-f", "null", "-"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired):
        return None
    blocks = re.findall(r"\{[^{}]*\}", p.stderr, flags=re.S)
    if not blocks:
        return None
    try:
        return json.loads(blocks[-1])
    except json.JSONDecodeError:
        return None


def kweighted_lufs(x: np.ndarray) -> float:
    """Fallback estimate only. K-weighting via the FFT of the biquad
    transfer function, then ITU-R BS.1770-4 gating."""
    # BS.1770 K-weighting, 48 kHz coefficients
    stages = [((1.53512485958697, -2.69169618940638, 1.19839281085285),
               (1.0, -1.69065929318241, 0.73248077421585)),
              ((1.0, -2.0, 1.0),
               (1.0, -1.99004745483398, 0.99007225036621))]
    y = np.empty_like(x)
    for b, a in stages:
        H = np.fft.rfft(np.array([b[0], b[1], b[2]]), N)
        H /= np.fft.rfft(np.array([a[0], a[1], a[2]]), N)
        y = np.fft.irfft(np.fft.rfft(x, axis=1) * H, n=x.shape[1], axis=1)
    blk = int(0.4 * SR)
    hop = int(0.1 * SR)
    starts = range(0, x.shape[1] - blk + 1, hop)
    loud = []
    for s in starts:
        e = float(np.sum(y[:, s:s + blk] ** 2))
        loud.append(-0.691 + 10.0 * math.log10(e / blk / 2.0 + 1e-30))
    loud = np.array(loud)
    gate = loud[loud > -70.0]
    if gate.size == 0:
        return -70.0
    rel = -0.691 + 10.0 * math.log10(
        np.mean(10.0 ** ((gate + 0.691) / 10.0)))
    keep = gate[gate > rel - 10.0]
    if keep.size == 0:
        return -70.0
    return -0.691 + 10.0 * math.log10(
        np.mean(10.0 ** ((keep + 0.691) / 10.0)))


def master(path: str, mix: np.ndarray, rng: np.random.Generator) -> dict:
    """Gain the mix so ffmpeg measures about TARGET_I, with the limiter's
    ceiling chosen to keep the true peak under TARGET_TP."""
    gain_db = 0.0
    ceiling_db = -1.6
    report = {}
    for it in range(7):
        y = mix * db_to_lin(gain_db)
        if float(np.max(np.abs(y))) > db_to_lin(ceiling_db):
            y = soft_limit(y, db_to_lin(ceiling_db))
        write_wav(path, y, rng)
        m = measure_loudness(path)
        if m is None:
            est = kweighted_lufs(mix)
            gain_db = TARGET_I - est
            y = mix * db_to_lin(gain_db)
            if float(np.max(np.abs(y))) > db_to_lin(ceiling_db):
                y = soft_limit(y, db_to_lin(ceiling_db))
            write_wav(path, y, rng)
            report["measured_by"] = "internal K-weighted estimate (ffmpeg unavailable)"
            report["gain_db"] = round(gain_db, 3)
            report["estimate_lufs"] = round(est, 3)
            return report
        i = float(m["input_i"])
        tp = float(m["input_tp"])
        print(f"  pass {it + 1}: gain {gain_db:+.3f} dB, ceiling "
              f"{ceiling_db:+.2f} dBFS -> input_i {i} LUFS, input_tp {tp} dBTP")
        report["gain_db"] = round(gain_db, 3)
        report["ceiling_db"] = round(ceiling_db, 3)
        report["measured_by"] = "ffmpeg loudnorm"
        if abs(TARGET_I - i) <= TOL_I and tp < TARGET_TP:
            report["passes"] = it + 1
            return report
        if tp >= TARGET_TP:
            ceiling_db -= (tp - TARGET_TP) + 0.3
            print(f"  true peak {tp} dBTP is not under {TARGET_TP}: "
                  f"ceiling -> {ceiling_db:+.2f} dBFS")
            continue
        gain_db += (TARGET_I - i)
    report["passes"] = 7
    return report


# ---------------------------------------------------------------------------


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(SEED)

    print("music: pad")
    music = render_music(rng)
    music_path = os.path.join(OUT, "music.wav")
    write_wav(music_path, music, rng)
    print(f"  wrote {music_path} peak {20 * math.log10(np.max(np.abs(music))):.2f} dBFS")

    print("sfx: cuts and caption ticks")
    sfx = render_sfx(rng)
    sfx_path = os.path.join(OUT, "sfx.wav")
    write_wav(sfx_path, sfx, rng)
    print(f"  wrote {sfx_path} peak {20 * math.log10(np.max(np.abs(sfx))):.2f} dBFS")

    # premix is exactly what the two stems contain, summed
    mix = read_wav(music_path) + read_wav(sfx_path)
    del music, sfx
    print("mastering")
    premix_path = os.path.join(OUT, "premix.wav")
    info = master(premix_path, mix, rng)
    print("  " + json.dumps(info))
    return 0


if __name__ == "__main__":
    sys.exit(main())
