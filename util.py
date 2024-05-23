from pathlib import Path
import json


def save_dotmatrix_charset_json(dotmatrix_charset: dict, filepath: str | Path):
    """Az argumentumban megadott szótárat elmenti egy JSON fájlba a megadott útvonalon és névvel."""
    with open(Path(filepath), 'w', encoding='UTF8', newline='\n') as f:
        json.dump(dotmatrix_charset, f)


def read_dotmatrix_charset_json(filepath: str | Path) -> dict:
    """Az argumentumban megadott útvonalon elérhető JSON fájl tartalmát beolvassa egy szótárba."""
    if Path(filepath).stat().st_size == 0:  # Ha a fájl létezik, de üres, akkor egy üres szótárat adunk vissza.
        return dict()
    with open(Path(filepath), 'r', encoding='UTF8', newline='\n') as f:
        d = json.load(f)
    return d
