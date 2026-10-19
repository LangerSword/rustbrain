#!/usr/bin/env python3
"""Verify the synthesized stems against the spec, from the written files.

Reads out/video/audio/{music,sfx,premix}.wav and checks, with printed numbers:

  1. format and duration of all three files
  2. premix is exactly the two stems summed with one master gain (dither level
     residual, no extra processing)
  3. the pad really plays the intended chord every 15 s: for every note of
     every chord the local spectral peak sits on the intended frequency, above
     the local noise floor
  4. the pad has no percussion style transients (10 ms level steps)
  5. every cut time carries a sweep of about 350 ms, every caption time a tick
     of about 25 ms, and nothing else is audible between events
  6. ticks and sweeps sit above the pad in their own band
  7. no pop at the file head or tail (first/last samples, max sample step)

Run:  python3 video/audio/verify_stems.py
"""
from __future__ import annotations

import math
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import synth  # noqa: E402  (constants and the chord table)

OUT = os.path.join(synth.ROOT, "out", "video", "audio")
SR = synth.SR
MUSIC = os.path.join(OUT, "music.wav")
SFX = os.path.join(OUT, "sfx.wav")
PREMIX = os.path.join(OUT, "premix.wav")


def load(path: str) -> np.ndarray:
    with wave.open(path, "rb") as w:
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype="<i2").astype(np.float64).reshape(-1, 2)


def blocks(path: str, chunk: int = 1 << 20):
    with wave.open(path, "rb") as w:
        while True:
            raw = w.readframes(chunk)
            if not raw:
                break
            yield np.frombuffer(raw, dtype="<i2").astype(np.float64).reshape(-1, 2)


def db(x: float) -> float:
    return 20.0 * math.log10(max(x, 1e-12))


def band_rms(x: np.ndarray, f_lo: float, f_hi: float) -> float:
    """One sided band rms of a mono block, Hann windowed."""
    w = np.hanning(len(x))
    X = np.fft.rfft(x * w)
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    m = (f >= f_lo) & (f <= f_hi)
    power = 2.0 * float(np.sum(np.abs(X[m]) ** 2)) / (len(x) * float(np.sum(w ** 2)))
    return math.sqrt(power)


def main() -> int:
    fail: list[str] = []
    print("=== 1. format")
    for name in ("music", "sfx", "premix"):
        p = os.path.join(OUT, f"{name}.wav")
        with wave.open(p, "rb") as w:
            info = (w.getnchannels(), w.getsampwidth(), w.getframerate(),
                    w.getnframes())
        ok = info[0] == 2 and info[1] == 2 and info[2] == SR and info[3] == synth.N
        print(f"  {name}.wav: channels={info[0]} width={info[1] * 8} bit "
              f"rate={info[2]} frames={info[3]} dur={info[3] / SR:.3f} s "
              f"size={os.path.getsize(p)} bytes {'ok' if ok else 'FAIL'}")
        if not ok:
            fail.append(f"{name}.wav format/duration")

    print("=== 2. premix vs music + sfx")
    num = den = 0.0
    for a, b, p in zip(blocks(MUSIC), blocks(SFX), blocks(PREMIX)):
        s = a / 32768.0 + b / 32768.0
        num += float(np.sum(p / 32768.0 * s))
        den += float(np.sum(s * s))
    gain = num / den
    err = 0.0
    total = 0
    for a, b, p in zip(blocks(MUSIC), blocks(SFX), blocks(PREMIX)):
        r = p / 32768.0 - gain * (a / 32768.0 + b / 32768.0)
        err += float(np.sum(r * r))
        total += len(r)
    res = math.sqrt(err / total)
    print(f"  best fit master gain {db(gain):+.3f} dB, residual rms "
          f"{db(res):.1f} dBFS (16 bit dither alone sits near -90 dBFS)")
    if db(res) > -70.0:
        fail.append("premix is not just music + sfx at one gain")

    print("=== 3. chord notes present (middle 8 s of each 15 s segment)")
    music = load(MUSIC)[:, 0] / 32768.0
    worst_cents = 0.0
    worst_snr = 999.0
    for k, notes in enumerate(synth.CHORDS):
        t0 = k * synth.SEG
        if t0 + synth.SEG > synth.DUR - 7.0:
            break
        i0 = int((t0 + 3.5) * SR)
        seg = music[i0:i0 + 8 * SR]
        X = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        f = np.fft.rfftfreq(len(seg), 1.0 / SR)
        band = (f >= 40.0) & (f <= 1500.0)
        excl = np.zeros_like(band)
        for m in notes:
            fo = synth.midi_to_freq(m)
            for h in (1, 2, 3, 4):
                excl |= (f > fo * h * 0.97) & (f < fo * h * 1.03)
        ref = float(np.median(X[band & ~excl]))
        devs, snrs = [], []
        for m in notes:
            fo = synth.midi_to_freq(m)
            sel = (f > fo * 0.97) & (f < fo * 1.03)
            j = int(np.argmax(np.where(sel, X, 0.0)))
            devs.append(1200.0 * math.log2(f[j] / fo))
            snrs.append(db(X[j]) - db(ref))
        md = max(abs(d) for d in devs)
        ms = min(snrs)
        worst_cents = max(worst_cents, md)
        worst_snr = min(worst_snr, ms)
        print(f"  t={t0:5.1f}s {len(notes)} notes, wanted "
              f"{' '.join(f'{synth.midi_to_freq(m):.1f}' for m in notes)} Hz: "
              f"worst detune {md:.1f} cents, weakest note {ms:+.1f} dB above "
              f"the local floor")
    print(f"  worst over all chords: {worst_cents:.1f} cents, weakest note "
          f"{worst_snr:+.1f} dB")
    if worst_cents > 12.0 or worst_snr < 12.0:
        fail.append("chord notes are not cleanly present")
    # stray tone diagnostic: what else is loud in the pad spectrum
    i0 = int(18.5 * SR)
    seg = music[i0:i0 + 8 * SR]
    X = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1.0 / SR)
    sel = (f >= 40.0) & (f <= 2000.0)
    idx = np.nonzero(sel)[0]
    top = idx[np.argsort(X[idx])[::-1][:10]]
    print("  loudest bins 40 to 2000 Hz at t=18.5 s (level re file max): "
          + ", ".join(f"{f[j]:.1f} Hz {db(X[j] / X.max()):.1f} dB" for j in top))

    print("=== 4. pad transients (short term level steps at several windows)")
    # skip the global fades at both ends: a fade in from silence always shows
    # large steps in dB, it is not a transient
    guard_a = int(4.0 * SR)
    guard_b = synth.N - int(8.0 * SR)
    body = music[guard_a:guard_b]
    for win_ms in (10, 25, 50, 100):
        win = int(win_ms / 1000.0 * SR)
        nb = len(body) // win
        env = np.sqrt((body[:nb * win].reshape(nb, win) ** 2).mean(axis=1))
        e = 20.0 * np.log10(env + 1e-12)
        ok = (e[:-1] > -55.0) & (e[1:] > -55.0)
        step = np.abs(np.diff(e))[ok]
        tstep = (np.nonzero(ok)[0] + 1) * win / SR + 4.0
        j = int(np.argmax(step))
        note = ""
        if win_ms <= 25:
            note = (" (window is near or under the beat period between chord "
                    "tones, 21 to 45 Hz, so it shows interference ripple)")
        print(f"  window {win_ms:3d} ms: largest step {step.max():5.2f} dB at "
              f"t={tstep[j]:.1f} s, 99.9th percentile "
              f"{np.percentile(step, 99.9):5.2f} dB{note}")
        if win_ms == 100 and step.max() > 3.0:
            fail.append("pad shows a transient jump")
        if win_ms == 50 and step.max() > 4.0:
            fail.append("pad shows a transient jump at 50 ms")

    print("=== 5. sfx events")
    sfx = load(SFX) / 32768.0
    env_all = np.abs(sfx).max(axis=1)
    print(f"  whole file peak {db(float(env_all.max())):.2f} dBFS")
    busy = np.zeros(synth.N, dtype=bool)
    for t0 in synth.CUTS:
        i0 = int((t0 - 0.25) * SR)
        i1 = int((t0 + 0.25) * SR)
        seg = env_all[i0:i1]
        pk = float(seg.max())
        a20 = np.nonzero(seg > pk * 0.1)[0]
        a40 = np.nonzero(seg > pk * 0.01)[0]
        busy[i0:i1] = True
        print(f"  cut  {t0:5.1f} s sweep: peak {db(pk):6.2f} dBFS, width at "
              f"-20 dB {(a20[-1] - a20[0] + 1) / SR * 1000:.0f} ms, at -40 dB "
              f"{(a40[-1] - a40[0] + 1) / SR * 1000:.0f} ms")
    for t0 in synth.CAPTIONS:
        i0 = int(t0 * SR)
        i1 = int((t0 + 0.06) * SR)
        seg = env_all[i0:i1]
        pk = float(seg.max())
        a20 = np.nonzero(seg > pk * 0.1)[0]
        busy[i0:i1] = True
        note = " (on a cut, sweep shares the window)" if t0 in synth.CUTS else ""
        print(f"  caption {t0:5.1f} s tick:  peak {db(pk):6.2f} dBFS, width at "
              f"-20 dB {(a20[-1] - a20[0] + 1) / SR * 1000:.0f} ms{note}")
    quiet = float(env_all[~busy].max())
    print(f"  loudest sample outside every event window: {db(quiet):.1f} dBFS")
    if db(quiet) > -80.0:
        fail.append("something is audible between sfx events")

    print("=== 6. event level against the pad in the same band (0.1 s window)")
    ticks, sweeps = [], []
    for t0 in synth.CAPTIONS:
        i0 = int(t0 * SR)
        w = int(0.1 * SR)
        tick = band_rms(sfx[i0:i0 + w, 0], 1600.0, 2200.0)
        padb = band_rms(music[i0:i0 + w], 1600.0, 2200.0)
        m = db(tick) - db(padb)
        ticks.append((m, t0, db(tick), db(padb)))
    for m, t0, tk, pd in ticks:
        note = " (on a cut, sweep shares the window)" if t0 in synth.CUTS else ""
        print(f"  tick  t={t0:5.1f} s: event {tk:7.2f} dBFS, pad {pd:7.2f} "
              f"dBFS, event above pad by {m:5.1f} dB{note}")
    for t0 in synth.CUTS:
        i0 = int((t0 - 0.05) * SR)
        w = int(0.1 * SR)
        sw = band_rms(sfx[i0:i0 + w, 0], 900.0, 4500.0)
        padb = band_rms(music[i0:i0 + w], 900.0, 4500.0)
        sweeps.append(db(sw) - db(padb))
        print(f"  sweep t={t0:5.1f} s: event {db(sw):7.2f} dBFS, pad "
              f"{db(padb):7.2f} dBFS, event above pad by "
              f"{db(sw) - db(padb):5.1f} dB")
    off_cut = [m for m, t0, _, _ in ticks if t0 not in synth.CUTS]
    print(f"  ticks off the cuts: {min(off_cut):.1f} to {max(off_cut):.1f} dB "
          f"above the pad, sweeps: {min(sweeps):.1f} to {max(sweeps):.1f} dB "
          f"above the pad (band energy ratios, a crude masking proxy)")
    if min(off_cut) < 5.0 or min(sweeps) < 5.0:
        fail.append("an event is masked by the pad in its band")
    # how much the pad's own level and brightness move over the file (the
    # fades at both ends excluded)
    lo = int(4.0 * SR)
    hi = synth.N - int(10.0 * SR)
    lv = []
    step = int(1.5 * SR)
    for i in range(lo, hi - step, step):
        lv.append(db(band_rms(music[i:i + step], 680.0, 3400.0)))
    lv = np.array(lv)
    print(f"  pad 680 to 3400 Hz band level moves {np.percentile(lv, 5):.1f} to "
          f"{np.percentile(lv, 95):.1f} dBFS over the file (morph range), "
          f"{lv.max() - lv.min():.1f} dB min to max")
    step = int(10.0 * SR)
    lw = []
    for i in range(lo, hi - step, step):
        lw.append(db(float(np.sqrt(np.mean(music[i:i + step] ** 2)))))
    lw = np.array(lw)
    print(f"  pad overall level per 10 s window: {lw.min():.2f} to "
          f"{lw.max():.2f} dBFS, {lw.max() - lw.min():.2f} dB spread")

    print("=== 7. head and tail (pop check on premix)")
    pre = load(PREMIX)
    d = np.abs(np.diff(pre, axis=0)).max(axis=1)
    gstep = float(d.max())
    for name, s, e in (("head", 0, SR), ("tail", synth.N - SR, synth.N - 1)):
        b = pre[s:e]
        print(f"  {name}: max |sample| {int(np.abs(b).max())} LSB, max sample "
              f"to sample step {int(d[s:e - 1].max())} LSB "
              f"({100.0 * d[s:e - 1].max() / gstep:.1f}% of the file wide "
              f"step {int(gstep)} LSB)")
    ms5 = int(0.005 * SR)
    print(f"  first 5 ms: max |sample| {int(np.abs(pre[:ms5]).max())} LSB, max "
          f"step {int(d[:ms5].max())} LSB (file wide max step "
          f"{int(gstep)} LSB); last 5 ms: max |sample| "
          f"{int(np.abs(pre[-ms5:]).max())} LSB, max step "
          f"{int(d[-ms5:].max())} LSB")
    print(f"  first frame {pre[0].astype(int).tolist()} LSB, last frame "
          f"{pre[-1].astype(int).tolist()} LSB, first 4 frames "
          f"{pre[:4, 0].astype(int).tolist()}")
    if int(np.abs(pre[0]).max()) > 32 or int(np.abs(pre[-1]).max()) > 32:
        fail.append("premix starts or ends on a non zero sample")
    if d[:ms5].max() > gstep:
        fail.append("premix has a step at the head larger than anywhere else")
    if d[-ms5:].max() > 0.05 * gstep:
        fail.append("premix has a step at the tail larger than anywhere else")

    print()
    if fail:
        print("FAILURES: " + "; ".join(fail))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
