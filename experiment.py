"""Gaussian beam propagation and thin-lens focusing calculations.

I used the ideal TEM00 equations to compare wavelength, starting waist,
and lens focal length. The tables and plots correspond to Chapter 6.
"""

import csv
import math
from pathlib import Path

import matplotlib

# Save the plots as image files, so no plot window needs to be opened.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# Keep the output folders next to this Python file.
PROJECT_DIR = Path(__file__).resolve().parent
TABLES_DIR = PROJECT_DIR / "outputs" / "numerical" / "tables"
FIGURES_DIR = PROJECT_DIR / "outputs" / "numerical" / "figures"


def gaussian(wavelength_m, waist_m, distance_m):
    """Calculate Rayleigh range, divergence, and beam radius (Eq. 6-1).

    Inputs use metres. Distance may be one value or a NumPy array.
    The divergence returned here is the half-angle, in radians.
    """
    # Rayleigh range depends on the square of the initial waist.
    rayleigh_m = math.pi * waist_m**2 / wavelength_m
    half_angle_rad = wavelength_m / (math.pi * waist_m)

    # Beam radius at distance z from the waist: w(z) = w0 sqrt(1 + (z/zR)^2).
    radius_m = waist_m * np.sqrt(1.0 + (np.asarray(distance_m) / rayleigh_m) ** 2)
    return rayleigh_m, half_angle_rad, radius_m


def focus(wavelength_m, waist_m, focal_length_m):
    """Find the new waist formed by an ideal thin lens (Eqs. 6-2 to 6-4).

    Here the incoming beam waist is at the lens plane. The function returns:
    focus distance, new waist radius, approximate waist radius, percentage
    error of the approximation, and output Rayleigh range.
    """
    rayleigh_m = math.pi * waist_m**2 / wavelength_m
    denominator = focal_length_m**2 + rayleigh_m**2

    # Exact Gaussian beam result for this lens arrangement.
    focus_distance_m = focal_length_m * rayleigh_m**2 / denominator
    new_waist_m = focal_length_m * waist_m / math.sqrt(denominator)
    output_rayleigh_m = focal_length_m**2 * rayleigh_m / denominator

    # Compare with the commonly used strong-focusing approximation.
    approx_waist_m = wavelength_m * focal_length_m / (math.pi * waist_m)
    error_pct = 100.0 * (approx_waist_m / new_waist_m - 1.0)

    return focus_distance_m, new_waist_m, approx_waist_m, error_pct, output_rayleigh_m


def save_csv(filename, columns, rows):
    """Save a calculated table as a CSV file."""
    with (TABLES_DIR / filename).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)


def format_plot(ax, title, x_label, y_label):
    """Use the same layout for all five figures."""
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(alpha=0.26)
    ax.legend(frameon=False, loc="best")
    ax.figure.tight_layout()


def study_a():
    """Study A: effect of wavelength (Table 6.2 and Figure 6.1)."""
    print("\nSTUDY A — Change wavelength; keep beam waist = 0.50 mm")
    print("lambda(nm)  zR(m)   theta(mrad)   w(1m)(mm)   w(2m)(mm)")

    rows = []
    distances_m = np.linspace(0, 3, 301)  # 0 to 3 m, with 301 plot points
    waist_m = 0.50e-3  # 0.50 mm converted to metres
    fig, ax = plt.subplots(figsize=(8, 4.8))

    for wavelength_nm in (532, 1064, 1550):
        wavelength_m = wavelength_nm * 1e-9  # nm to m
        z_r, theta, radius = gaussian(wavelength_m, waist_m, distances_m)
        radius_1m = float(gaussian(wavelength_m, waist_m, 1.0)[2])
        radius_2m = float(gaussian(wavelength_m, waist_m, 2.0)[2])

        # The values are converted only for display: m -> mm, rad -> mrad.
        rows.append([
            wavelength_nm, f"{z_r:.4f}", f"{theta * 1e3:.4f}",
            f"{radius_1m * 1e3:.4f}", f"{radius_2m * 1e3:.4f}",
        ])
        print(
            f"{wavelength_nm:9d}  {z_r:6.4f}     {theta * 1e3:7.4f}"
            f"       {radius_1m * 1e3:7.4f}       {radius_2m * 1e3:7.4f}"
        )
        ax.plot(distances_m, radius * 1e3, linewidth=2, label=f"{wavelength_nm} nm")

    save_csv(
        "table_6_2_wavelength.csv",
        ["wavelength_nm", "rayleigh_m", "half_angle_mrad", "w_at_1m_mm", "w_at_2m_mm"],
        rows,
    )
    format_plot(ax, "Figure 6.1 — Propagation at three wavelengths",
                "Distance from waist (m)", "Beam radius (mm)")
    fig.savefig(FIGURES_DIR / "figure_6_1_wavelength.png", dpi=180)
    plt.close(fig)


def study_b():
    """Study B: effect of initial waist (Table 6.3, Figures 6.2 and 6.3)."""
    print("\nSTUDY B — Change initial waist; keep wavelength = 1064 nm")
    print("w0(mm)     zR(m)   theta(mrad)   w(1m)(mm)   w(3m)(mm)")

    rows = []
    wavelength_m = 1064e-9
    distances_m = np.linspace(0, 3, 301)
    fig, ax = plt.subplots(figsize=(8, 4.8))

    for waist_mm in (0.25, 0.50, 1.00):
        waist_m = waist_mm * 1e-3
        z_r, theta, radius = gaussian(wavelength_m, waist_m, distances_m)
        radius_1m = float(gaussian(wavelength_m, waist_m, 1.0)[2])
        radius_3m = float(gaussian(wavelength_m, waist_m, 3.0)[2])

        rows.append([
            waist_mm, f"{z_r:.4f}", f"{theta * 1e3:.4f}",
            f"{radius_1m * 1e3:.4f}", f"{radius_3m * 1e3:.4f}",
        ])
        print(
            f"{waist_mm:6.2f}    {z_r:6.4f}     {theta * 1e3:7.4f}"
            f"       {radius_1m * 1e3:7.4f}       {radius_3m * 1e3:7.4f}"
        )
        ax.plot(distances_m, radius * 1e3, linewidth=2,
                label=f"w0 = {waist_mm:.2f} mm")

    save_csv(
        "table_6_3_waist.csv",
        ["initial_waist_mm", "rayleigh_m", "half_angle_mrad", "w_at_1m_mm", "w_at_3m_mm"],
        rows,
    )
    format_plot(ax, "Figure 6.2 — Propagation at three waist sizes",
                "Distance from waist (m)", "Beam radius (mm)")
    fig.savefig(FIGURES_DIR / "figure_6_2_waist.png", dpi=180)
    plt.close(fig)

    # A separate plot shows that Rayleigh range increases with waist squared.
    waist_values_mm = np.linspace(0.15, 1.10, 301)
    rayleigh_values_m = math.pi * (waist_values_mm * 1e-3) ** 2 / wavelength_m
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(waist_values_mm, rayleigh_values_m, linewidth=2.5,
            label="zR = pi*w0^2 / lambda")
    for waist_mm in (0.25, 0.50, 1.00):
        z_r = math.pi * (waist_mm * 1e-3) ** 2 / wavelength_m
        ax.scatter([waist_mm], [z_r], s=35)
    format_plot(ax, "Figure 6.3 — Rayleigh range vs. waist",
                "Initial waist (mm)", "Rayleigh range (m)")
    fig.savefig(FIGURES_DIR / "figure_6_3_rayleigh.png", dpi=180)
    plt.close(fig)


def study_c():
    """Study C: ideal thin-lens focusing (Table 6.4 and Figure 6.4)."""
    print("\nSTUDY C — Thin-lens focusing; wavelength = 1064 nm")
    print("w0(mm)  f(mm)   s(mm)    new_waist(um)   approx_error(%)")

    rows = []
    wavelength_m = 1064e-9

    # Table 6.4 uses nine combinations of beam waist and focal length.
    for waist_mm in (0.5, 1.0, 2.0):
        for focal_mm in (50, 100, 200):
            focus_m, new_waist_m, _, error_pct, _ = focus(
                wavelength_m, waist_mm * 1e-3, focal_mm * 1e-3
            )
            rows.append([
                waist_mm, focal_mm, f"{focus_m * 1e3:.2f}",
                f"{new_waist_m * 1e6:.2f}", f"{error_pct:.3f}",
            ])
            print(
                f"  {waist_mm:3.1f}   {focal_mm:5d}    {focus_m * 1e3:6.2f}"
                f"         {new_waist_m * 1e6:7.2f}        {error_pct:7.3f}"
            )

    save_csv(
        "table_6_4_lens.csv",
        ["initial_waist_mm", "focal_length_mm", "focus_distance_mm",
         "new_waist_um", "approx_error_pct"],
        rows,
    )

    # Use more focal-length values to draw smooth curves for Figure 6.4.
    focal_values_mm = np.linspace(50, 200, 301)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for waist_mm in (0.5, 1.0, 2.0):
        focused_radii_um = np.array([
            focus(wavelength_m, waist_mm * 1e-3, float(f) * 1e-3)[1] * 1e6
            for f in focal_values_mm
        ])
        ax.plot(focal_values_mm, focused_radii_um, linewidth=2,
                label=f"w0 = {waist_mm:.1f} mm")
    format_plot(ax, "Figure 6.4 — Focused waist vs. focal length",
                "Lens focal length (mm)", "Focused radius (micrometres)")
    fig.savefig(FIGURES_DIR / "figure_6_4_focusing.png", dpi=180)
    plt.close(fig)


def approximation_error():
    """Compare the exact and approximate lens results (Table/Figure 6.5)."""
    print("\nFOCUSING APPROXIMATION — Change f / zR (Table 6.5)")
    print("f/zR     waist_error(%)    s/f")

    rows = []
    for ratio in (0.05, 0.10, 0.30, 0.50, 1.00, 2.00):
        # The difference depends on the ratio between focal length and zR.
        error_pct = 100 * (math.sqrt(1 + ratio**2) - 1)
        relative_focus_distance = 1 / (1 + ratio**2)
        rows.append([f"{ratio:.2f}", f"{error_pct:.2f}",
                     f"{relative_focus_distance:.4f}"])
        print(f"{ratio:4.2f}         {error_pct:8.2f}       {relative_focus_distance:6.4f}")

    save_csv(
        "table_6_5_error.csv",
        ["f_over_zR", "waist_error_pct", "exact_s_over_f"],
        rows,
    )

    ratios = np.linspace(0, 2.0, 401)
    error_percent = 100 * (np.sqrt(1 + ratios**2) - 1)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(ratios, error_percent, linewidth=2.5,
            label="100 * (sqrt(1 + (f/zR)^2) - 1)")
    format_plot(ax, "Figure 6.5 — Error of approximate focusing formula",
                "Ratio f / zR", "Relative error (%)")
    fig.savefig(FIGURES_DIR / "figure_6_5_approximation_error.png", dpi=180)
    plt.close(fig)


def verify_model():
    """Check the basic formulas against known limits and Chapter 6 values."""
    wavelength_m = 1064e-9
    waist_m = 0.50e-3
    z_r, theta, radius_at_waist = gaussian(wavelength_m, waist_m, 0)

    # At the waist, w(0) = w0; one Rayleigh range away, w(zR) = sqrt(2)*w0.
    assert math.isclose(float(radius_at_waist), waist_m, rel_tol=1e-12)
    assert math.isclose(float(gaussian(wavelength_m, waist_m, z_r)[2]),
                        math.sqrt(2) * waist_m, rel_tol=1e-12)

    # Compare with the rounded numerical results reported in the dissertation.
    assert math.isclose(z_r, 0.7382, abs_tol=5e-5)
    assert math.isclose(theta * 1e3, 0.6774, abs_tol=5e-5)
    assert math.isclose(float(gaussian(wavelength_m, waist_m, 1.0)[2]) * 1e3,
                        0.8419, abs_tol=5e-5)
    assert math.isclose(float(gaussian(wavelength_m, waist_m, 3.0)[2]) * 1e3,
                        2.0927, abs_tol=5e-5)

    focus_m, focused_waist_m, _, _, _ = focus(wavelength_m, 2e-3, 0.1)
    assert math.isclose(focus_m * 1e3, 99.99, abs_tol=0.005)
    assert math.isclose(focused_waist_m * 1e6, 16.93, abs_tol=0.005)
    assert math.isclose(100 * (math.sqrt(1 + 0.5**2) - 1),
                        11.80, abs_tol=0.005)
    print("\nChecks passed: selected Chapter 6 results agree with the calculations.")


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    study_a()
    study_b()
    study_c()
    approximation_error()
    verify_model()

    print("\nSaved 4 CSV tables in outputs/numerical/tables and 5 figures in outputs/numerical/figures.")
    print("All results are predictions from the ideal model, not laboratory measurements.")


if __name__ == "__main__":
    main()
