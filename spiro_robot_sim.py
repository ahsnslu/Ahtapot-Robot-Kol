"""
spiro_robot_sim.py

Visualizes a logarithmic-spiral continuum robot: a chain of rigid
sub-segments whose length AND cross-sectional diameter shrink
geometrically (by a constant `decay_ratio` per segment) while the
heading angle accumulates a fixed increment per segment.

Unlike a constant-curvature / linearly-tapered continuum robot, the
geometric decay causes the backbone to spiral inward, so bend angles
greater than 360 degrees produce a nautilus-like, self-overlapping
shape. This is useful for exploring compliant "shrinking" manipulator
designs or purely as a parametric spiral generator.

Usage:
    python spiro_robot_sim.py
    python spiro_robot_sim.py --angle 540 --segments 40 --ratio 0.92
    python spiro_robot_sim.py --style paper --save spiral.png --no-show
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class SpiroConfig:
    """Physical and rendering parameters for the logarithmic-spiral robot."""

    segment_count: int = 25          # Number of discrete sub-segments
    start_length: float = 25.0       # Length of the first segment [mm]
    start_diameter: float = 50.0     # Cross-sectional diameter of the first segment [mm]
    decay_ratio: float = 0.95        # Per-segment length/diameter shrink factor (0 < ratio < 1)
    total_bend_deg: float = 540.0    # Total accumulated heading change [degrees]
    fill_alpha: float = 0.10         # Opacity of the overlapping diameter circles
    line_color: str = "purple"


@dataclass(frozen=True)
class SpiroGeometry:
    """Result of the forward-kinematics computation for the spiral backbone."""

    x: NDArray[np.float64]
    y: NDArray[np.float64]
    segment_lengths: NDArray[np.float64]
    segment_diameters: NDArray[np.float64]


# --------------------------------------------------------------------------- #
# Kinematics
# --------------------------------------------------------------------------- #

def compute_spiral_geometry(config: SpiroConfig) -> SpiroGeometry:
    """
    Computes the 2D backbone coordinates of a logarithmic-spiral robot.

    The backbone starts at the origin, pointing straight up (90 degrees).
    At each of `segment_count` steps, the heading angle is incremented by
    `total_bend_deg / segment_count`, and the segment length/diameter are
    scaled down by `decay_ratio` relative to the previous segment.

    Args:
        config: Spiral robot physical parameters.

    Returns:
        SpiroGeometry containing backbone x/y coordinates (length
        segment_count + 1) and per-segment lengths/diameters (length
        segment_count).
    """
    if not 0.0 < config.decay_ratio < 1.0:
        raise ValueError("decay_ratio must be strictly between 0 and 1.")

    indices = np.arange(config.segment_count)
    segment_lengths = config.start_length * (config.decay_ratio ** indices)
    segment_diameters = config.start_diameter * (config.decay_ratio ** indices)

    angle_increment = np.radians(config.total_bend_deg / config.segment_count)
    theta = np.radians(90.0)  # Start pointing straight up

    x_coords = np.zeros(config.segment_count + 1)
    y_coords = np.zeros(config.segment_count + 1)

    for i in range(config.segment_count):
        theta += angle_increment
        x_coords[i + 1] = x_coords[i] + segment_lengths[i] * np.cos(theta)
        y_coords[i + 1] = y_coords[i] + segment_lengths[i] * np.sin(theta)

    return SpiroGeometry(
        x=x_coords,
        y=y_coords,
        segment_lengths=segment_lengths,
        segment_diameters=segment_diameters,
    )


def log_segment_length_summary(geometry: SpiroGeometry) -> None:
    """Logs the first and last segment lengths for a quick sanity check."""
    logger.info(
        "Segment 1: length %.2f mm", geometry.segment_lengths[0]
    )
    logger.info(
        "Segment %d: length %.2f mm",
        len(geometry.segment_lengths),
        geometry.segment_lengths[-1],
    )


# --------------------------------------------------------------------------- #
# Styling
# --------------------------------------------------------------------------- #

def apply_plot_style(style: str) -> None:
    """
    Applies a global matplotlib rcParams style.

    Args:
        style: "default" for standard matplotlib styling, or "paper" for
            a serif, thesis/journal-article-friendly appearance.
    """
    plt.rcdefaults()
    plt.style.use("default")

    if style == "paper":
        plt.rcParams.update(
            {
                "font.family": "serif",
                "font.serif": ["Times New Roman"],
                "axes.grid": True,
                "grid.alpha": 0.3,
                "axes.labelsize": 12,
                "figure.figsize": (10, 5),
            }
        )


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def build_figure(config: SpiroConfig, geometry: SpiroGeometry) -> plt.Figure:
    """Builds the spiral robot figure: backbone line, tapering circles, base."""
    fig, ax = plt.subplots()

    ax.plot(
        geometry.x,
        geometry.y,
        "-o",
        linewidth=2,
        markersize=8,
        color=config.line_color,
    )

    for i in range(config.segment_count):
        circle = plt.Circle(
            (geometry.x[i], geometry.y[i]),
            geometry.segment_diameters[i] / 2,
            color=config.line_color,
            alpha=config.fill_alpha,
        )
        ax.add_patch(circle)

    ax.plot([-20, 20], [0, 0], "k-", linewidth=3)
    ax.axis("equal")
    ax.grid(True, alpha=0.3)
    ax.set_title(f"Spiro Robot Simulation\nTotal Bend: {config.total_bend_deg:g} deg")

    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def run_simulation(
    config: SpiroConfig, style: str = "default"
) -> plt.Figure:
    """Computes the spiral geometry and returns the rendered figure."""
    apply_plot_style(style)
    geometry = compute_spiral_geometry(config)
    log_segment_length_summary(geometry)
    return build_figure(config, geometry)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate and visualize a logarithmic-spiral continuum robot."
    )
    parser.add_argument(
        "--angle", type=float, default=540.0,
        help="Total accumulated heading change, in degrees.",
    )
    parser.add_argument(
        "--segments", type=int, default=25,
        help="Number of discrete sub-segments.",
    )
    parser.add_argument(
        "--ratio", type=float, default=0.95,
        help="Per-segment length/diameter decay ratio (0 < ratio < 1).",
    )
    parser.add_argument(
        "--start-length", type=float, default=25.0,
        help="Length of the first segment, in mm.",
    )
    parser.add_argument(
        "--start-diameter", type=float, default=50.0,
        help="Diameter of the first segment, in mm.",
    )
    parser.add_argument(
        "--style", choices=["default", "paper"], default="default",
        help="Plot style: 'default' or 'paper' (serif, thesis-style formatting).",
    )
    parser.add_argument(
        "--save", type=str, default=None, metavar="PATH",
        help="Save the figure to PATH instead of/in addition to displaying it.",
    )
    parser.add_argument(
        "--no-show", action="store_true",
        help="Do not open an interactive window (useful for headless/CI environments).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = SpiroConfig(
        segment_count=args.segments,
        start_length=args.start_length,
        start_diameter=args.start_diameter,
        decay_ratio=args.ratio,
        total_bend_deg=args.angle,
    )

    fig = run_simulation(config, style=args.style)

    if args.save:
        fig.savefig(args.save, dpi=200)
        logger.info("Figure saved to %s", args.save)

    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()
