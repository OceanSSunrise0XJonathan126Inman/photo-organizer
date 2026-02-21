from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path
import shutil

import typer
from PIL import Image, ExifTags
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()


def _version_callback(value: bool):
    if not value:
        return
    try:
        typer.echo(pkg_version("photo-organizer"))
    except PackageNotFoundError:
        typer.echo("unknown")
    raise typer.Exit()


@dataclass(frozen=True)
class PlannedMove:
    src: Path
    dst: Path


def _exif_datetime(path: Path) -> datetime | None:
    try:
        img = Image.open(path)
        exif = getattr(img, "getexif", lambda: None)()
        if not exif:
            return None

        tagmap = {k: ExifTags.TAGS.get(k, k) for k in exif.keys()}

        def get_tag(name: str) -> str | None:
            for k, v in exif.items():
                if tagmap.get(k) == name and isinstance(v, str):
                    return v
            return None

        for key in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
            s = get_tag(key)
            if s:
                try:
                    return datetime.strptime(s, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    pass
        return None
    except Exception:
        return None


def _file_datetime_utc(path: Path) -> datetime:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _pick_datetime(path: Path) -> datetime:
    exif_dt = _exif_datetime(path)
    if exif_dt is not None:
        return exif_dt
    return _file_datetime_utc(path)


def _iter_images(src_dir: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff"}
    files: list[Path] = []
    for p in src_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            files.append(p)
    return sorted(files)


def _plan_moves(src_dir: Path, out_dir: Path) -> list[PlannedMove]:
    moves: list[PlannedMove] = []
    for p in _iter_images(src_dir):
        dt = _pick_datetime(p)
        year = f"{dt.year:04d}"
        year_month = f"{dt.year:04d}-{dt.month:02d}"
        dst_dir = out_dir / year / year_month
        dst = dst_dir / p.name
        moves.append(PlannedMove(src=p, dst=dst))
    return moves


def _print_plan(moves: list[PlannedMove], do_it: bool) -> None:
    title = "Planned moves" if not do_it else "Executed moves"
    table = Table(title=title)
    table.add_column("From")
    table.add_column("To")
    for m in moves[:30]:
        table.add_row(str(m.src), str(m.dst))
    if len(moves) > 30:
        table.add_row("...", f"({len(moves)} total)")
    console.print(table)


@app.command()
def main(
    src: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out: Path = typer.Argument(..., file_okay=False, dir_okay=True),
    do_it: bool = typer.Option(False, "--do-it", help="Apply changes (otherwise dry-run)."),
    version: bool = typer.Option(None, "--version", callback=_version_callback, is_eager=True),
):
    out.mkdir(parents=True, exist_ok=True)

    moves = _plan_moves(src, out)

    if do_it:
        for m in moves:
            m.dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(m.src), str(m.dst))

    _print_plan(moves, do_it=do_it)


if __name__ == "__main__":
    app()
