# -*- coding: utf-8 -*-
"""
Phoenix ABS 40-43 -- preview renderer for the aft assembly.

Plain Python + numpy, no FreeCAD and no image library. Reads the coarse meshes that
PhoenixABS40-43_aft_assembly_v1.py drops in Models/_render/ and rasterises them with a
z-buffer, so the aft end can be eyeballed without opening the GUI.

Run (after the assembly script):
  python Models/render_aft_assembly.py

Writes Models/_render/aft_assembly_iso.png and aft_assembly_section.png.
"""

import os
import struct
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.join(HERE, "_render")

W, H = 1100, 820
BG = (250, 249, 246)

# livery from DESIGN.md section 10, plus stand-in colours for the reference bodies
COLOR = {
    "AftFinCan": (212, 185, 145),
    "AftSectionSealed": (212, 185, 145),
    "MotorRetainerCap": (58, 58, 64),
    "Fin_A": (246, 246, 250),
    "Fin_B": (238, 238, 243),
    "Fin_C": (230, 230, 236),
    "DummyMotor": (116, 62, 48),
    "FwdTubeStub": (198, 173, 138),
}
ORDER = ["AftFinCan", "AftSectionSealed", "MotorRetainerCap",
         "Fin_A", "Fin_B", "Fin_C", "DummyMotor", "FwdTubeStub"]


def load_stl(path):
    with open(path, "rb") as fh:
        n = struct.unpack("<I", fh.read(84)[80:84])[0]
        raw = np.frombuffer(fh.read(n * 50), dtype=np.uint8).reshape(n, 50)
    return raw[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)


def write_png(path, img):
    """Minimal RGB PNG writer."""
    h, w, _ = img.shape
    raw = b"".join(b"\x00" + img[y].tobytes() for y in range(h))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    hdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", hdr)
                 + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def rotation(az_deg, el_deg):
    a, e = np.radians(az_deg), np.radians(el_deg)
    rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return rx.dot(rz)


def render(tris_by_name, az, el, path, half=False, label=""):
    tris, cols = [], []
    for name in ORDER:
        if name not in tris_by_name:
            continue
        t = tris_by_name[name]
        if half:
            t = t[t[:, :, 1].mean(1) <= 0.0]        # cut the near half away
        if len(t):
            tris.append(t)
            cols.append(np.tile(np.array(COLOR[name], float), (len(t), 1)))
    tris = np.concatenate(tris)
    cols = np.concatenate(cols)

    # rocket axis is Z; stand it on its side so the long axis runs across the frame
    base = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float)
    M = rotation(az, el).dot(base)
    v = tris.reshape(-1, 3).dot(M.T).reshape(-1, 3, 3)

    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
    ln = np.linalg.norm(n, axis=1)
    keep = ln > 1e-9
    v, cols, n, ln = v[keep], cols[keep], n[keep], ln[keep]
    n = n / ln[:, None]

    light = np.array([-0.35, -0.55, 0.76])
    light /= np.linalg.norm(light)
    shade = 0.32 + 0.68 * np.clip(np.abs(n.dot(light)), 0, 1)
    rgb = np.clip(cols * shade[:, None], 0, 255)

    mn, mx = v.reshape(-1, 3).min(0), v.reshape(-1, 3).max(0)
    span = max(mx[0] - mn[0], mx[1] - mn[1]) * 1.06
    sc = min(W, H) / span
    cx, cy = (mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0
    px = (v[:, :, 0] - cx) * sc + W / 2.0
    py = H / 2.0 - (v[:, :, 1] - cy) * sc
    pz = v[:, :, 2]

    img = np.zeros((H, W, 3), np.uint8)
    img[:, :] = BG
    zbuf = np.full((H, W), -1e18)

    order = np.argsort(pz.mean(1))          # far to near, helps the z-buffer settle
    for i in order:
        x0, x1 = px[i].min(), px[i].max()
        y0, y1 = py[i].min(), py[i].max()
        if x1 < 0 or y1 < 0 or x0 > W - 1 or y0 > H - 1:
            continue
        ix0, ix1 = int(max(0, np.floor(x0))), int(min(W - 1, np.ceil(x1)))
        iy0, iy1 = int(max(0, np.floor(y0))), int(min(H - 1, np.ceil(y1)))
        if ix1 < ix0 or iy1 < iy0:
            continue
        xs = np.arange(ix0, ix1 + 1)
        ys = np.arange(iy0, iy1 + 1)
        gx, gy = np.meshgrid(xs, ys)
        ax, ay = px[i, 0], py[i, 0]
        e1x, e1y = px[i, 1] - ax, py[i, 1] - ay
        e2x, e2y = px[i, 2] - ax, py[i, 2] - ay
        det = e1x * e2y - e1y * e2x
        if abs(det) < 1e-12:
            continue
        qx, qy = gx - ax, gy - ay
        u = (qx * e2y - qy * e2x) / det
        w2 = (qy * e1x - qx * e1y) / det
        m = (u >= 0) & (w2 >= 0) & (u + w2 <= 1)
        if not m.any():
            continue
        z = pz[i, 0] + u * (pz[i, 1] - pz[i, 0]) + w2 * (pz[i, 2] - pz[i, 0])
        sub = zbuf[iy0:iy1 + 1, ix0:ix1 + 1]
        hit = m & (z > sub)
        if not hit.any():
            continue
        sub[hit] = z[hit]
        img[iy0:iy1 + 1, ix0:ix1 + 1][hit] = rgb[i].astype(np.uint8)

    write_png(path, img)
    print("  %-28s %6d triangles  %s" % (os.path.basename(path), len(v), label))


def main():
    if not os.path.isdir(RENDER):
        print("no Models/_render -- run PhoenixABS40-43_aft_assembly_v1.py first")
        return 1
    tris = {}
    for name in ORDER:
        p = os.path.join(RENDER, name + ".stl")
        if os.path.exists(p):
            tris[name] = load_stl(p)
    if not tris:
        print("no meshes in Models/_render")
        return 1
    print("rendering:")
    render(tris, 34, 22, os.path.join(RENDER, "aft_assembly_iso.png"),
           label="assembled, three-quarter view")
    render(tris, 0, 0, os.path.join(RENDER, "aft_assembly_section.png"),
           half=True, label="longitudinal half-section")
    return 0


if __name__ == "__main__":
    sys.exit(main())
