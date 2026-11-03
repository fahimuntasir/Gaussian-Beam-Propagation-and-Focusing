
# Gaussian Beam Propagation and Focusing: Principles and Applications

**Course:** Principle of Laser  
**Author:** MUNTASIR MD FAHIM (王一然)  
**Major:** Information and Communication Engineering  
**University:** Changchun University of Science and Technology

## Project overview

This repository contains the Python work for my Principle of Laser course dissertation. I studied how an ideal Gaussian beam changes as it propagates and passes through a focusing lens. I also analyzed a set of published laser-beam images to examine their intensity profiles using Gaussian fitting.

The project has two separate studies: a numerical simulation based on Gaussian beam equations and an image-analysis study using existing laser-beam photographs. Their results are presented separately because the simulation uses chosen physical parameters, while the image analysis measures profiles in pixel units.

## Dissertation

The complete dissertation covers Gaussian beam theory, the calculation methods, both studies, their results, and the main limitations.

**[Read the full dissertation (PDF)](Gaussian%20Beam%20Propagation%20and%20Focusing.pdf)**

## Experiments

### 1. Numerical simulation of Gaussian beam propagation and focusing

In `experiment.py`, I calculated the beam radius, Rayleigh range, divergence, and focused waist using ideal TEM00 Gaussian beam equations. I compared three wavelengths, three initial waist sizes, and several thin-lens focal lengths. I also examined the difference between the exact and approximate focusing calculations.

This study produced **five figures and four CSV tables**.

![Gaussian beam propagation for different wavelengths](outputs/numerical/figures/figure_6_1_wavelength.png)

### 2. Gaussian fitting of laser-beam images

In `analyze_beam_images.py`, I analyzed 14 example `TEM00_z_*.jpg` images provided through the [DataLab laser-beam profiling tutorial](https://datalab-platform.com/en/intro/tutorials/laser_beam.html). The script estimates the centre of each beam, extracts averaged horizontal and vertical intensity profiles, and fits Gaussian curves using nonlinear least squares.

From these fits, I obtained the horizontal and vertical 1/e² intensity radii, full widths at half maximum (FWHM), and R² fit scores. The saved results contain **14 measurement rows and three figures**. The fitted radii generally increase across the image series, while the 28 individual profile fits have R² values of approximately **0.993–0.996**.

![Fitted beam radii across the image series](outputs/image_analysis/beam_width_across_images.png)

## Project files

| File or folder | Contents |
| --- | --- |
| `Gaussian Beam Propagation and Focusing.pdf` | Full course dissertation |
| `experiment.py` | Numerical propagation and focusing calculations |
| `analyze_beam_images.py` | Laser-image analysis and Gaussian profile fitting |
| `download_source_images.py` | Downloads the published DataLab image archive |
| `requirements.txt` | Python packages needed to run the scripts |
| `outputs/numerical/figures/` | Five figures from the numerical study |
| `outputs/numerical/tables/` | Four CSV tables from the numerical study |
| `outputs/image_analysis/` | Measurement CSV for 14 images and three figures |
| `data/README.md` | Information about the image source |

## Running the Python code

I used **Python 3.11** for this project. From the project folder, install the required libraries:

```bash
python -m pip install -r requirements.txt
```

**Experiment 1 — numerical simulation**

```bash
python experiment.py
```

**Experiment 2 — image analysis**

First, download the original image archive and then run the fitting script:

```bash
python download_source_images.py
python analyze_beam_images.py
```

If the download script does not work, download `laser_beam.zip` from the [DataLab tutorial](https://datalab-platform.com/en/intro/tutorials/laser_beam.html) and place it in the `data/` folder. The image-analysis script can read this ZIP without extracting it.

The scripts save their plots and CSV files in `outputs/`. The numerical simulation can be rerun using the files in this repository. The image-analysis results and figures are already available, but **repeating the image fitting requires the original JPEG archive**, which is not included in this repository.

## Interpretation and limitations

The numerical study uses ideal beam equations and selected input values. It is not based on laboratory measurements. The image-analysis study uses publicly available DataLab tutorial images, rather than photographs taken during my own experiment.

The fitted image radii are measured in **pixels**. Numbers in the `TEM00_z_*.jpg` filenames are treated as image labels, not as independently calibrated propagation distances. Therefore, the image measurements should not be used to claim a measured physical Rayleigh range or beam-quality factor M² without additional calibration and measurement information.

## Data source

DataLab Platform. *Laser beam profiling: measuring beam size along the propagation axis*. [Tutorial and example image dataset](https://datalab-platform.com/en/intro/tutorials/laser_beam.html).
