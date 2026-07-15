"""
continuum_robot_sim.py

Visualizes the constant-curvature kinematic model of a soft continuum
(tapered) robot arm across several bending scenarios, alongside a
curvature-propagation engineering plot.

The robot is modeled as a chain of `segment_count` rigid sub-segments.
Each sub-segment rotates by a fixed incremental angle
(`total_bend_angle / segment_count`), producing a constant-curvature arc.
The cross-sectional radius decreases linearly from `base_radius` at the
fixed end to `base_radius * taper_ratio` at the tip, approximating a
tapered soft-robotics manipulator.

Usage:
    python continuum_robot_sim.py
    python continuum_robot_sim.py --angles 30 90 160 --save output.png
    python continuum_robot_sim.py --no-show --save output.png

Author: <your name>
License: MIT
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass, field
from typing import Sequence

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from numpy.typing import NDArray

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class RobotConfig:
    """Physical and rendering parameters for the continuum robot."""

    segment_count: int = 40          # Number of discrete sub-segments (higher = smoother)
    arm_length: float = 100.0        # Total arm length [mm]
    base_radius: float = 6.0         # Cross-sectional radius at the fixed base [mm]
    taper_ratio: float = 0.4         # Tip radius as a fraction of base_radius
    bend_scenarios: Sequence[float] = field(
        default_factory=lambda: (30.0, 90.0, 160.0)
    )  # Bending angles to simulate, in degrees
    colors: Sequence[str] = field(
        default_factory=lambda: ("#B0C4DE", "#778899", "#2F4F4F")
    )  # LightSteelBlue -> LightSlateGray -> DarkSlateGray


@dataclass(frozen=True)
class SegmentGeometry:
    """Result of the forward-kinematics computation for a single scenario."""

    x: NDArray[np.float64]
    y: NDArray[np.float64]
    radii: NDArray[np.float64]
    bend_angle_deg: float


# --------------------------------------------------------------------------- #
# Kinematics
# --------------------------------------------------------------------------- #

def compute_constant_curvature_geometry(
    config: RobotConfig, bend_angle_deg: float
) -> SegmentGeometry:
    """
    Computes the 2D backbone coordinates and per-segment radii of a
    constant-curvature continuum robot bent by `bend_angle_deg` degrees.

    The backbone starts at the origin, pointing straight up (90 degrees),
    and accumulates a fixed incremental rotation at every segment.

    Args:
        config: Robot physical parameters.
        bend_angle_deg: Total bend angle for this scenario, in degrees.

    Returns:
        SegmentGeometry containing backbone x/y coordinates (length
        segment_count + 1) and per-segment radii (length segment_count).
    """
    segment_length = config.arm_length / config.segment_count
    angle_increment = np.radians(bend_angle_deg) / config.segment_count

    theta = np.radians(90.0)  # Start pointing straight up
    x_coords = np.zeros(config.segment_count + 1)
    y_coords = np.zeros(config.segment_count + 1)

    for i in range(config.segment_count):
        theta += angle_increment
        x_coords[i + 1] = x_coords[i] + segment_length * np.cos(theta)
        y_coords[i + 1] = y_coords[i] + segment_length * np.sin(theta)

    # Linear taper from base_radius to base_radius * taper_ratio
    fractional_progress = np.arange(config.segment_count) / config.segment_count
    radii = config.base_radius * (
        1 - (1 - config.taper_ratio) * fractional_progress
    )

    return SegmentGeometry(
        x=x_coords, y=y_coords, radii=radii, bend_angle_deg=bend_angle_deg
    )


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def draw_robot_pose(
    ax: plt.Axes,
    geometry: SegmentGeometry,
    color: str,
    alpha: float,
    is_final_pose: bool,
) -> None:
    """Draws a single robot pose as a chain of overlapping circles."""
    for j in range(len(geometry.x) - 1):
        circle = patches.Circle(
            (geometry.x[j], geometry.y[j]),
            geometry.radii[j],
            color=color,
            alpha=alpha,
            linewidth=0,
        )
        ax.add_patch(circle)

    if is_final_pose:
        ax.scatter(
            geometry.x[-1],
            geometry.y[-1],
            color="#8B0000",
            s=50,
            zorder=10,
            label="End Effector",
        )
        ax.plot(
            geometry.x,
            geometry.y,
            color="white",
            linewidth=1,
            alpha=0.5,
            linestyle="--",
        )


def draw_curvature_plot(ax: plt.Axes, geometry: SegmentGeometry, color: str) -> None:
    """Plots bending angle vs. normalized arc length for one scenario."""
    normalized_length = np.linspace(0, 1, len(geometry.x))
    curvature_values = np.linspace(0, geometry.bend_angle_deg, len(geometry.x))

    ax.plot(
        normalized_length,
        curvature_values,
        color=color,
        linewidth=2,
        marker="o",
        markersize=3,
        markevery=5,
        label=f"Load Case: {geometry.bend_angle_deg:g} deg",
    )


def style_simulation_axes(ax: plt.Axes) -> None:
    """Applies consistent styling to the robot pose (left) subplot."""
    ax.set_aspect("equal")
    ax.set_title(
        "Continuum Robot Simulation\n(Constant Curvature Model)",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("X Position [mm]", fontsize=9, color="#555555")
    ax.set_ylabel("Y Position [mm]", fontsize=9, color="#555555")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.plot([-20, 20], [0, 0], color="black", linewidth=3)
    ax.text(0, -5, "FIXED BASE", ha="center", va="top", fontsize=8, fontweight="bold")


def style_data_axes(ax: plt.Axes) -> None:
    """Applies consistent styling to the engineering data (right) subplot."""
    ax.set_title(
        "Kinematic Performance Analysis", fontsize=12, fontweight="bold", pad=15
    )
    ax.set_xlabel("Normalized Length (L/L_total)", fontsize=10)
    ax.set_ylabel("Bending Angle (Degrees)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(fontsize=9, loc="upper left")
    for spine in ax.spines.values():
        spine.set_edgecolor("#555555")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def build_figure(config: RobotConfig) -> plt.Figure:
    """Builds the full two-panel figure (robot pose + curvature analysis)."""
    plt.style.use("default")

    fig, (ax_sim, ax_data) = plt.subplots(
        1, 2, figsize=(14, 7), gridspec_kw={"width_ratios": [1.5, 1]}
    )
    fig.patch.set_facecolor("#FAFAFA")
    ax_sim.set_facecolor("#FAFAFA")
    ax_data.set_facecolor("#FAFAFA")

    if len(config.colors) < len(config.bend_scenarios):
        raise ValueError(
            "config.colors must have at least as many entries as bend_scenarios"
        )

    for step_index, bend_angle_deg in enumerate(config.bend_scenarios):
        geometry = compute_constant_curvature_geometry(config, bend_angle_deg)
        is_final_pose = step_index == len(config.bend_scenarios) - 1
        color = config.colors[step_index]
        alpha = 1.0 if is_final_pose else 0.4

        draw_robot_pose(ax_sim, geometry, color, alpha, is_final_pose)
        draw_curvature_plot(ax_data, geometry, color)

    style_simulation_axes(ax_sim)
    style_data_axes(ax_data)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate and visualize a constant-curvature continuum robot."
    )
    parser.add_argument(
        "--angles",
        type=float,
        nargs="+",
        default=None,
        help="Bending angles to simulate, in degrees (e.g. --angles 30 90 160).",
    )
    parser.add_argument(
        "--segments",
        type=int,
        default=None,
        help="Number of discrete sub-segments used to approximate the arc.",
    )
    parser.add_argument(
        "--length",
        type=float,
        default=None,
        help="Total arm length in mm.",
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        metavar="PATH",
        help="Save the figure to PATH (e.g. output.png) instead of/in addition to displaying it.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not open an interactive window (useful for headless/CI environments).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    overrides = {}
    if args.angles is not None:
        overrides["bend_scenarios"] = tuple(args.angles)
    if args.segments is not None:
        overrides["segment_count"] = args.segments
    if args.length is not None:
        overrides["arm_length"] = args.length

    config = RobotConfig(**overrides)

    logger.info(
        "Rendering simulation for scenarios %s degrees...", config.bend_scenarios
    )
    fig = build_figure(config)

    if args.save:
        fig.savefig(args.save, dpi=200, facecolor=fig.get_facecolor())
        logger.info("Figure saved to %s", args.save)

    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()
