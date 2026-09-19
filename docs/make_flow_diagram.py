"""Render a public hero flow diagram for the docs (PNG)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / ".." / "docs" / "flow_overview.png"

GREEN = "#2e6b4f"
ORANGE = "#d98324"
INK = "#1e2a24"
GREY = "#8a8378"
PAPER = "#f3ead9"

fig, ax = plt.subplots(figsize=(12.5, 7.2), dpi=150)
ax.set_xlim(0, 12.5)
ax.set_ylim(0, 7.2)
ax.axis("off")
fig.patch.set_facecolor(PAPER)


def box(x, y, w, h, text, fc="#ffffff", ec=INK, fs=10, weight="bold"):
    b = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.08",
        linewidth=1.4,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(b)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        fontweight=weight,
        color=INK,
        linespacing=1.5,
    )


def arrow(x1, y1, x2, y2, color=INK):
    a = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=16,
        linewidth=1.6,
        color=color,
    )
    ax.add_patch(a)


# Input
box(0.45, 6.1, 2.3, 0.85, "Photo\nupload / snapshot / live cam", fc="#fffbe9")

# Detector
box(4.15, 6.1, 2.5, 0.85, "1. Cat detector\nYOLOv8n @640", fc="#eaf4ee", ec=GREEN)
arrow(2.75, 6.55, 4.15, 6.55)

# Crop + classify
box(8.0, 6.1, 3.6, 0.85, "2. Crop + classify\nMobileNetV2 224px + flip TTA", fc="#eaf4ee", ec=GREEN)
arrow(6.65, 6.55, 8.0, 6.55)

# Named cats
box(1.0, 4.2, 2.1, 0.8, "Meko\n→ green stamp", fc="#eaf4ee", ec=GREEN)
box(5.3, 4.2, 2.1, 0.8, "Lily\n→ orange stamp", fc="#fff2df", ec=ORANGE)
box(9.6, 4.2, 2.6, 0.8, "A visitor\n→ no stamp", fc="#f1efe9", ec=GREY)
arrow(8.7, 6.4, 2.05, 5.0)
arrow(10.0, 6.4, 6.35, 5.0)
arrow(11.9, 6.4, 10.9, 5.0)

# Fallback tile scan (Tier 1, planned)
box(1.6, 2.45, 3.4, 0.8, "Tiled scan (planned)\ncat missed by detector?", fc="#fffbe9", ec=ORANGE)
arrow(2.0, 4.2, 2.6, 3.25)
arrow(4.4, 2.85, 6.5, 2.85, color=ORANGE)

# Whole-photo card
box(7.3, 1.5, 3.4, 0.8, "3. Whole-photo card\n(best box wins)", fc="#eaf4ee", ec=GREEN)
arrow(6.5, 2.85, 8.4, 2.3, color=ORANGE)
arrow(10.6, 2.3, 10.6, 1.45)

# Verdict
box(3.4, 0.25, 4.6, 0.85, "4. Verdict: stamp Meko / Lily / Not registered", fc="#1e2a24", ec="#1e2a24", fs=11.5)
ax.text(3.4, 0.25, "", color=PAPER)
arrow(7.3, 1.5, 7.0, 1.1, color=GREEN)
arrow(8.0, 1.5, 8.0, 1.1, color=INK)

ax.text(
    9.6,
    4.0,
    "Tier 1 fixes:\nfind cats the detector missed",
    fontsize=9,
    ha="center",
    color=ORANGE,
    style="italic",
)

ax.set_title(
    "Meko or Lily? — how a photo becomes a stamp",
    fontsize=16,
    fontweight="bold",
    color=INK,
    pad=18,
)

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, bbox_inches="tight", facecolor=PAPER)
print("wrote", OUT.resolve())