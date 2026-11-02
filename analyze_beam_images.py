"""Gaussian-profile fitting of DataLab beam images.

I fit the horizontal and vertical intensity profiles for each image,
then compare the radii and fit quality across the series. Values are in pixels.
The original image ZIP is downloaded separately (see README.md).
"""

import csv
import io
import re
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Save plots to PNG without opening a window.
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.optimize import curve_fit

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "outputs" / "image_analysis"
ZIP_CANDIDATES = [BASE / "laser_beam.zip", BASE / "data" / "laser_beam.zip"]


def position_label(filename):
    """Read a number from filenames like TEM00_z_13.jpg (arbitrary units)."""
    match = re.search(r"TEM00_z_(\d+)", Path(filename).name, re.I)
    return int(match.group(1)) if match else None


def list_images():
    """Find images inside the downloaded ZIP or an extracted data folder."""
    for filename in ZIP_CANDIDATES:
        if filename.is_file():
            with zipfile.ZipFile(filename) as archive:
                paths = [p for p in archive.namelist()
                         if p.lower().endswith((".jpg", ".jpeg", ".png"))
                         and "__macosx" not in p.lower()]
            if paths:
                paths.sort(key=lambda p: (position_label(p) is None,
                                          position_label(p) or 0, p))
                return ("zip", filename, paths)

    folder = BASE / "data"
    paths = [p for p in folder.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
    paths.sort(key=lambda p: (position_label(p.name) is None,
                              position_label(p.name) or 0, str(p)))
    if paths:
        return ("folder", folder, paths)

    raise FileNotFoundError(
        "No beam images found. Download the official laser_beam.zip and place "
        "it next to analyze_beam_images.py. You do not need to extract the ZIP."
    )


def load_image(source_type, source_path, image_name):
    """Read one image as a grayscale array."""
    if source_type == "zip":
        with zipfile.ZipFile(source_path) as archive:
            image_bytes = archive.read(image_name)
        with Image.open(io.BytesIO(image_bytes)) as im:
            return np.asarray(im.convert("L"), dtype=float)
    with Image.open(image_name) as im:
        return np.asarray(im.convert("L"), dtype=float)


def gaussian_profile(x, amplitude, center, radius, offset):
    # Fundamental TEM00 intensity: I(x) = I0 exp[-2 (x-x0)^2 / w^2] + background.
    return amplitude * np.exp(-2.0 * ((x - center) / radius) ** 2) + offset


def fit_profile(profile):
    """Fit the Gaussian intensity curve to one horizontal/vertical section."""
    x = np.arange(len(profile), dtype=float)
    peak_idx = int(np.argmax(profile))
    peak = float(profile[peak_idx])
    baseline = float(np.percentile(profile, 10))
    if peak - baseline < 4.0:
        raise ValueError("beam profile is too faint for a reliable fit")

    # Estimate initial radius from the full width at half of the peak.
    above_half = np.where(profile >= baseline + (peak - baseline) / 2)[0]
    approximate_radius = max(2.0, len(above_half) / np.sqrt(2.0 * np.log(2)))
    start = [peak - baseline, peak_idx, approximate_radius, max(0.0, baseline)]
    lower = [0, 0, 1, 0]
    upper = [np.inf, len(profile) - 1, len(profile) * 2, np.inf]

    params, _ = curve_fit(gaussian_profile, x, profile, p0=start,
                          bounds=(lower, upper), maxfev=10000)
    fitted = gaussian_profile(x, *params)
    residual = profile - fitted
    residual_sum = float(np.sum(residual ** 2))
    total_sum = float(np.sum((profile - np.mean(profile)) ** 2))
    r_squared = 1.0 - residual_sum / total_sum if total_sum > 0 else float("nan")
    return params, fitted, r_squared


def analyze_image(gray):
    # Background intensity is estimated using the image edges.
    border = np.concatenate([gray[0, ::4], gray[-1, ::4],
                             gray[::4, 0], gray[::4, -1]])
    background = float(np.median(border))
    corrected = np.maximum(gray - background, 0.0)
    max_signal = float(corrected.max())
    if max_signal < 10:
        raise ValueError("no visible beam signal")

    # Find the bright beam center; an approximate centroid is enough to select profiles.
    bright = np.where(corrected >= 0.20 * max_signal, corrected, 0.0)
    if bright.sum() == 0:
        raise ValueError("could not locate beam center")
    y_coords, x_coords = np.indices(gray.shape)
    cx = int(round(float((bright * x_coords).sum() / bright.sum())))
    cy = int(round(float((bright * y_coords).sum() / bright.sum())))
    cx = int(np.clip(cx, 0, gray.shape[1] - 1))
    cy = int(np.clip(cy, 0, gray.shape[0] - 1))

    # Average 11 adjacent image rows/columns to reduce camera noise.
    # These are two measured 1D sections, not a full 2D beam-quality measurement.
    horizontal = gray[max(0, cy - 5):cy + 6, :].mean(axis=0)
    vertical = gray[:, max(0, cx - 5):cx + 6].mean(axis=1)
    x_params, x_curve, x_r2 = fit_profile(horizontal)
    y_params, y_curve, y_r2 = fit_profile(vertical)
    saturation = float(np.mean(gray >= 254) * 100.0)
    return {
        "center_x": cx, "center_y": cy, "background": background,
        "w_x_px": float(x_params[2]), "w_y_px": float(y_params[2]),
        "r2_x": x_r2, "r2_y": y_r2, "saturation_pct": saturation,
        "horizontal": horizontal, "vertical": vertical,
        "x_curve": x_curve, "y_curve": y_curve,
    }


def plot_example(gray, result, name):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    axes[0].imshow(gray, cmap="gray", vmin=0, vmax=255)
    axes[0].scatter([result["center_x"]], [result["center_y"]], s=30,
                    facecolors="none", edgecolors="red")
    axes[0].set_title("Example beam image")
    axes[0].set_xlabel("x (pixels)")
    axes[0].set_ylabel("y (pixels)")
    for ax, axis, axis_name in [(axes[1], "horizontal", "Horizontal"),
                                (axes[2], "vertical", "Vertical")]:
        samples = result[axis]
        fit = result["x_curve"] if axis == "horizontal" else result["y_curve"]
        ax.plot(np.arange(len(samples)), samples, linewidth=1.2, label="Image profile")
        ax.plot(np.arange(len(samples)), fit, linestyle="--", linewidth=1.8,
                label="Gaussian fit")
        ax.set_xlabel("Pixel position")
        ax.set_ylabel("Gray-level intensity")
        ax.set_title(axis_name + " intensity fit")
        ax.legend()
    fig.suptitle("Beam-image analysis: " + name, fontsize=12)
    fig.tight_layout()
    fig.savefig(OUTPUT / "example_image_and_fits.png", dpi=160)
    plt.close(fig)


def plot_summary(rows):
    x = [row["image_label"] if row["image_label"] is not None
         else row["image_order"] for row in rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, [row["w_x_px"] for row in rows], "o-", label="Horizontal radius")
    ax.plot(x, [row["w_y_px"] for row in rows], "s-", label="Vertical radius")
    ax.set_xlabel("Image filename position label (arbitrary units)")
    ax.set_ylabel("Gaussian 1/e² intensity radius (pixels)")
    ax.set_title("Estimated beam radius across the image series")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT / "beam_width_across_images.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, [row["r2_x"] for row in rows], "o-", label="Horizontal fit")
    ax.plot(x, [row["r2_y"] for row in rows], "s-", label="Vertical fit")
    ax.set_xlabel("Image filename position label (arbitrary units)")
    ax.set_ylabel("R² of Gaussian fit")
    ax.set_title("How closely the image sections match a Gaussian")
    ax.set_ylim(-0.1, 1.05)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT / "fit_quality_across_images.png", dpi=160)
    plt.close(fig)


def main():
    source_type, source_path, images = list_images()
    print("Dataset:", source_path)
    print("Images found:", len(images))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = []
    example = None

    for order, image_name in enumerate(images, start=1):
        gray = load_image(source_type, source_path, image_name)
        try:
            result = analyze_image(gray)
        except (ValueError, RuntimeError) as exc:
            print("Skipped", image_name, "because:", exc)
            continue
        label = position_label(str(image_name))
        rows.append({
            "image_order": order,
            "image_name": Path(image_name).name,
            "image_label": label,
            "w_x_px": round(result["w_x_px"], 4),
            "w_y_px": round(result["w_y_px"], 4),
            "fwhm_x_px": round(result["w_x_px"] * np.sqrt(2*np.log(2)), 4),
            "fwhm_y_px": round(result["w_y_px"] * np.sqrt(2*np.log(2)), 4),
            "r2_x": round(result["r2_x"], 6),
            "r2_y": round(result["r2_y"], 6),
            "background_graylevel": round(result["background"], 3),
            "saturated_pixels_pct": round(result["saturation_pct"], 4),
        })
        if example is None or order == (len(images) + 1) // 2:
            # Use a middle image for the example plot, if available.
            example = (gray.copy(), result, Path(image_name).name)
        print(f"{Path(image_name).name}: wx={result['w_x_px']:.2f} px; "
              f"wy={result['w_y_px']:.2f} px; R²x={result['r2_x']:.3f}")

    if not rows:
        raise RuntimeError("No images could be analyzed. Check the input image files.")

    with (OUTPUT / "beam_measurements.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    plot_summary(rows)
    if example is not None:
        plot_example(*example)
    print(f"\nFinished: analyzed {len(rows)} of {len(images)} images.")
    print("Saved CSV and three figures in:", OUTPUT)
    print("Note: radii are in pixels; filename labels are not verified distances.")
    print("The code cannot calculate physical Rayleigh range or M² without calibration.")


if __name__ == "__main__":
    main()
