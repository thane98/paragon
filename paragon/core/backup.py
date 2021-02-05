import datetime
import os
import shutil
import time
import zipfile


def _make_path():
    filename = datetime.datetime.fromtimestamp(time.time()).strftime(
        "backup-%Y_%m_%d_%H_%M_%S"
    )
    return os.path.join("Backups", filename)


def smart_backup(gd, output_path):
    dirty_files = gd.dirty_files()
    if not dirty_files:
        return
    prefix = os.path.normpath(os.path.abspath(output_path))
    with zipfile.ZipFile(_make_path() + ".zip", 'w', zipfile.ZIP_DEFLATED) as z:
        for f in dirty_files:
            path = os.path.normpath(os.path.join(output_path, f))
            if os.path.exists(path):
                z.write(path, os.path.relpath(path, prefix))


def full_backup(output_path):
    if os.path.isdir(output_path) and os.listdir(output_path):
        shutil.make_archive(_make_path(), "zip", output_path)


def backup(gd, output_path, smart=True):
    if not os.path.exists("Backups"):
        os.mkdir("Backups")
    if smart:
        smart_backup(gd, output_path)
    else:
        full_backup(output_path)
