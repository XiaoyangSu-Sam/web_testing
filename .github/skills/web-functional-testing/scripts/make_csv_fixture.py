"""Write a bounded, deterministic synthetic CSV and print its exact expected totals."""

import argparse
import json
from pathlib import Path

AMOUNTS = ("-1.25", "0.00", "3.75")
HEADER = b"id,amount,note\n"


def make_csv(path, rows, note_bytes, max_bytes):
    if rows < 1 or not 0 <= note_bytes <= 65_536 or max_bytes < 1:
        raise ValueError("Use positive rows and maximum bytes, with note width from 0 to 65,536")
    width = len(str(rows))
    # ID width, separators, amount text, note and newline.
    amount_bytes = (rows // 3) * sum(map(len, AMOUNTS)) + sum(map(len, AMOUNTS[:rows % 3]))
    size = len(HEADER) + rows * (width + note_bytes + 3) + amount_bytes
    if size > max_bytes:
        raise ValueError(f"Fixture would use {size} bytes, above the {max_bytes}-byte budget")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    note = b"x" * note_bytes + b"\n"
    with path.open("xb") as output:
        output.write(HEADER)
        for index in range(1, rows + 1):
            output.write(f"{index:0{width}d},{AMOUNTS[(index - 1) % 3]},".encode("ascii") + note)
    cents = 250 * (rows // 3) + (0 if rows % 3 == 0 else -125)
    amount_sum = f"{'-' if cents < 0 else ''}{abs(cents) // 100}.{abs(cents) % 100:02d}"
    return {"file": str(path), "rows": rows, "bytes": size, "amount_sum": amount_sum}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--note-bytes", type=int, default=64)
    parser.add_argument("--max-bytes", type=int, default=100 * 1024 * 1024)
    args = parser.parse_args()
    try:
        print(json.dumps(make_csv(args.output, args.rows, args.note_bytes, args.max_bytes)))
    except (ValueError, OSError) as error:
        parser.exit(2, f"Fixture generation failed: {error}\n")


if __name__ == "__main__":
    main()
