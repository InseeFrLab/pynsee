import zipfile
from pathlib import Path
from tqdm.utils import CallbackIOWrapper
from tqdm import tqdm
from shutil import copyfileobj
import os


def _unzip_pb(fzip, dest, desc="Extracting"):
    """
    Useful function to unzip with progress bar
    Args:
        fzip: Filename of the zipped file
        dest: Destination where data must be written
        desc: Argument inherited from zipfile.ZipFile

    Returns:
        zipfile.Zipfile(fzip).extractall(dest) with progress
    """

    dest = Path(dest).expanduser()
    Path(dest).mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(fzip) as zipf, tqdm(
        desc=desc,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        total=sum(getattr(i, "file_size", 0) for i in zipf.infolist()),
    ) as pbar:
        for i in zipf.infolist():
            if not getattr(i, "file_size", 0):  # directory
                zipf.extract(i, os.fspath(dest))
            else:
                with zipf.open(i) as tempfi, open(
                    os.fspath(dest / i.filename), "wb"
                ) as fileobj:
                    copyfileobj(CallbackIOWrapper(pbar.update, tempfi), fileobj)
