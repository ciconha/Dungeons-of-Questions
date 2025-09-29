# phase_maps.py
from pathlib import Path
import csv

def load_phase(n: int):
    """
    Carrega o CSV phase{n}.csv de assets/maps e retorna List[List[int]]
    """
    path = Path(__file__).parent / "assets" / "maps" / f"phase{n}.csv"
    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        return [[int(cell) for cell in row] for row in reader]

# pré-carrega as 6 fases
phase_maps = [load_phase(i) for i in range(1, 7)]
