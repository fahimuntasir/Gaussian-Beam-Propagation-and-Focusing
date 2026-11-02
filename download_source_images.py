"""Download the example laser-beam images from the DataLab tutorial.

The download is stored as data/laser_beam.zip for analyze_beam_images.py.
"""
from pathlib import Path
from urllib.request import urlopen, Request
from zipfile import ZipFile
import io

URL = "https://datalab-platform.com/en/_downloads/9f0c8646424df2aba2e7a778f56734d2/laser_beam.zip"
DEST = Path(__file__).resolve().parent / "data" / "laser_beam.zip"

if __name__ == "__main__":
    DEST.parent.mkdir(parents=True, exist_ok=True)
    print("Dataset source:", URL)
    try:
        with urlopen(Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=40) as response:
            data = response.read()
        if len(data) > 200_000_000:
            raise ValueError("Dataset exceeds 200 MB safety limit")
        with ZipFile(io.BytesIO(data)) as archive:
            images = [i for i in archive.namelist() if i.lower().endswith((".jpg", ".jpeg", ".png"))]
            expected = {f"TEM00_z_{x}.jpg" for x in (13,18,23,30,35,40,45,50,55,60,65,70,75,80)}
            present = {Path(i).name for i in images}
            missing = sorted(expected-present)
            if missing:
                raise ValueError(f"Expected tutorial files missing: {missing}")
            if len(images) != 14:
                print(f"Notice: archive contains {len(images)} images; 14 expected for the saved analysis.")
        DEST.write_bytes(data)
        print(f"Saved {DEST}, {len(data):,} bytes; {len(images)} image entries")
        print("To recompute fits: python analyze_beam_images.py")
    except Exception as exc:
        raise SystemExit(f"Download unavailable: {exc}\nDownload manually from the source tutorial and place laser_beam.zip in data/.")
