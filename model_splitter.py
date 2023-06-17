import os
import glob
import io

SIZE_LIMIT = 1024 * 1024 * 99  # 100MB


def split_file(file: str):
    dir, file = os.path.split(os.path.abspath(file))
    start, end = file.rsplit(".", 1)
    with open(os.path.join(dir, file), "rb") as s:
        for i in range(1, 100):
            if chunk := s.read(SIZE_LIMIT):
                with open(
                    os.path.join(dir, "split", f"{start}_{i:0>3}.{end}"), "wb"
                ) as f:
                    f.write(chunk)
            else:
                break
        else:
            raise ValueError("File size too large to split: '{file}'")


def _read_file(file: str):
    dir, file = os.path.split(os.path.abspath(file))
    start, end = file.rsplit(".", 1)
    for i in range(1, 100):
        try:
            with open(os.path.join(dir, "split", f"{start}_{i:0>3}.{end}"), "rb") as f:
                while x := f.read():
                    yield x
        except FileNotFoundError:
            break
    yield b""


def join_file(file: str):
    f = io.BytesIO(b"".join(x for x in _read_file(file)))


class TempSplitFile:
    def __init__(self, filepath: str):
        dir, file = os.path.split(os.path.abspath(filepath))
        self.filepath = filepath
        self.tempfile = os.path.join(dir, f"temp_{file}")

    def __enter__(self):
        if os.path.exists(self.tempfile):
            raise FileExistsError(self.tempfile)
        with open(self.tempfile, "wb") as f:
            f.write(b"".join(x for x in _read_file(self.filepath)))

        return self.tempfile

    def __exit__(self, e_type, e_value, trace):
        os.remove(self.tempfile)


def temp_join_file(file: str):
    tempfile = f"temp_{file}"
    if os.path.exists(tempfile):
        raise FileExistsError(tempfile)
    with open(tempfile, "wb") as f:
        f.write(b"".join(x for x in _read_file(file)))
        yield tempfile


def temp_done(file: str):
    ...


if __name__ == "__main__":
    for file in glob.iglob("savedModel/*.*"):
        split_file(file)
