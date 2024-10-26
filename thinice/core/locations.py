from pathlib import Path

class Locations:
    base_path: Path

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True)

    def __repr__(self):
        return f'Locations(base: {self.base_path})'