from pathlib import Path


class HeightStore:

    def __init__(self, path: Path):
        self._path = path

        try:
            self.load()
        except FileNotFoundError:
            self.save(0)

    def load(self):
        with self._path.open('r') as file:
            height = file.read()
            return int(height)

    def save(self, height):
        with self._path.open('w') as file:
            file.write(str(height))
