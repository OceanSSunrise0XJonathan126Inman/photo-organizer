import os
import subprocess
from pathlib import Path
from PIL import Image

def test_do_it_moves_into_year_month(tmp_path: Path):
    src = tmp_path / "src"
    out = tmp_path / "out"
    src.mkdir()
    out.mkdir()

    # Create a tiny jpg (no EXIF) so tool falls back to mtime
    img_path = src / "sample.jpg"
    Image.new("RGB", (2, 2)).save(img_path)

    # Set mtime to a known date: 2026-02-12
    ts = 1770854400  # 2026-02-12 00:00:00 UTC
    os.utime(img_path, (ts, ts))

    # Run CLI with --do-it
    subprocess.run(
        ["photo-organizer", "--do-it", str(src), str(out)],
        check=True,
        capture_output=True,
        text=True,
    )

    moved = out / "2026" / "2026-02" / "sample.jpg"
    assert moved.exists()
    assert not img_path.exists()
