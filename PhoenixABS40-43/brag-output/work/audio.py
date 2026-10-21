"""Soundtrack for the Phoenix 40-43 brag video: one 21 s piece, A minor, 100 BPM.
Music and effects share the key and one reverb so the hits sit inside the track."""
import numpy as np, wave

SR = 48000
DUR = 21.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(3)
BEAT = 0.6

def hz(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def lp(x, fc):  # one-pole low-pass, fc may be an array
    fc = np.broadcast_to(fc, x.shape)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y

def add(buf, x, at):
    i = int(at * SR); j = min(N, i + len(x))
    if j > i: buf[i:j] += x[:j - i]

pad = np.zeros(N); bass = np.zeros(N); drums = np.zeros(N); fx = np.zeros(N)

# ---- pad: Am | F | C | G | Am, changes near the scene cuts -------------------------
chords = [(0.0, [57, 60, 64]), (3.0, [53, 57, 60]), (7.0, [48, 55, 60, 64]),
          (11.5, [55, 59, 62]), (15.0, [53, 57, 60, 65]), (18.0, [45, 57, 60, 64, 69])]
for k, (st, notes) in enumerate(chords):
    en = chords[k + 1][0] if k + 1 < len(chords) else DUR
    n = int((en - st + 0.6) * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes:
        for det in (-0.07, 0.07):
            f = hz(m + det)
            x += 2 * ((tt * f) % 1) - 1          # saw
    x /= len(notes) * 2
    e = env_adsr(n, 0.35 if k else 1.2, 0.6)
    add(pad, x * e, st)
# filter opens over the whole piece, dips at the outro then blooms
cut = 350 + 1700 * np.clip(t / 18, 0, 1) ** 1.5
cut = np.where(t > 18, 900 + 2200 * np.clip((t - 18) / 1.2, 0, 1), cut)
pad = lp(pad, cut) * 0.4
pad *= np.clip((DUR - t) / 1.2, 0, 1)

# ---- bass pulse + kick on the beat from the reveal to the outro ---------------------
roots = {0: 45, 3.0: 41, 7.0: 36, 11.5: 43, 15.0: 41, 18.0: 33}
def root_at(x):
    r = 45
    for s, m in roots.items():
        if x >= s: r = m
    return r
b = 3.0
while b < 18.0 - 1e-6:
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = hz(root_at(b))
    add(bass, np.sin(2 * np.pi * f * tt) * np.exp(-tt * 5) * 0.5, b)
    kick = np.sin(2 * np.pi * (45 * tt + 60 * (1 - np.exp(-tt * 30)) / 30)) * np.exp(-tt * 9)
    add(drums, kick * 0.3, b)
    b += BEAT
# soft closed hats on 8ths during the deploy/latch/sled scenes
h = 7.0
while h < 18.0 - 1e-6:
    n = int(0.05 * SR); tt = np.arange(n) / SR
    noise = rng.standard_normal(n)
    noise = noise - lp(noise, 6000)               # crude high-pass
    add(drums, noise * np.exp(-tt * 90) * (0.07 if (round((h - 7) / 0.3)) % 2 else 0.045), h)
    h += BEAT / 2
# outro: one low A hit to land the title
n = int(2.5 * SR); tt = np.arange(n) / SR
add(bass, np.sin(2 * np.pi * hz(33) * tt) * np.exp(-tt * 1.4) * 0.6, 18.0)
add(drums, np.sin(2 * np.pi * (40 * tt + 50 * (1 - np.exp(-tt * 25)) / 25)) * np.exp(-tt * 5) * 0.55, 18.0)

# ---- effects (tuned to A / E) -------------------------------------------------------
def whump(level):
    n = int(1.3 * SR); tt = np.arange(n) / SR
    f = 110 * np.exp(-tt * 3) + 41
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
    noise = lp(rng.standard_normal(n), 900 * np.exp(-tt * 2) + 120) * np.exp(-tt * 4) * 2.2
    return (body + noise) * level
add(fx, whump(0.55), 1.45)                         # hook: tail kick
add(fx, whump(0.42), 9.75)                         # deploy: ejection charge
# canopy pop: soft filtered noise swell
n = int(0.6 * SR); tt = np.arange(n) / SR
add(fx, lp(rng.standard_normal(n), 1500) * np.sin(np.pi * np.clip(tt / 0.6, 0, 1)) * 0.25, 10.0)

def click(level, f0):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f0 * tt) + 0.5 * np.sin(2 * np.pi * f0 * 2.01 * tt)) * np.exp(-tt * 55)
    x[:int(0.002 * SR)] += rng.standard_normal(int(0.002 * SR)) * 0.6
    return x * level
add(fx, click(0.38, hz(76)), 11.5 + 1.5)           # E5
add(fx, click(0.38, hz(76)), 11.5 + 1.88)

# counter ticks v1 -> v19, same easing as the page
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
prev = 1
for i in range(int(3 * 600)):
    u = i / 600
    v = round(1 + 18 * eio(min(1, max(0, (u - .35) / 1.0))))
    if v != prev:
        add(fx, click(0.07, hz(88)), 15.0 + u); prev = v
# risers into each cut
for c in (3.0, 7.0, 11.5, 15.0, 18.0):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    add(fx, lp(rng.standard_normal(n), 400 + 3000 * (tt / 0.5) ** 2) * (tt / 0.5) ** 2 * 0.07, c - 0.5)

# ---- mix: one shared room ----------------------------------------------------------
def reverb(x, seed):
    r = np.random.default_rng(seed)
    n = int(1.6 * SR); tt = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-tt * 3.2); ir[0] = 0
    ir = lp(ir, 5000)
    L = len(x) + n
    F = np.fft.rfft(x, L) * np.fft.rfft(ir, L)
    return np.fft.irfft(F, L)[:len(x)] / np.sqrt(np.sum(ir ** 2)) * 0.18

dry = pad + bass * 0.9 + drums * 0.8 + fx * 0.75
send = pad * 0.6 + fx * 0.8 + drums * 0.15
left = dry + reverb(send, 1)
right = dry + reverb(send, 2)
st = np.stack([left, right], 1)
st /= np.max(np.abs(st)) / 0.95
st = np.tanh(st * 1.2) / np.tanh(1.2) * 0.89     # gentle limiter, ≈ -1 dBFS peak
fade = np.clip(t / 0.03, 0, 1)[:, None]
st *= fade
with wave.open('brag_audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', st.shape)
