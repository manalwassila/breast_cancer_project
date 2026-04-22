import os
import shutil
import random
from pathlib import Path


def make_val_split(train_dir="data/train", val_dir="data/val", frac=0.1, seed=42):
    random.seed(seed)
    train_path = Path(train_dir)
    val_path = Path(val_dir)
    if not train_path.exists():
        raise SystemExit(f"train dir not found: {train_path}")
    val_path.mkdir(parents=True, exist_ok=True)

    summary = {}
    for cls in [p.name for p in train_path.iterdir() if p.is_dir()]:
        src = train_path / cls
        dst = val_path / cls
        dst.mkdir(parents=True, exist_ok=True)

        files = [p for p in src.iterdir() if p.is_file()]
        n = max(1, int(len(files) * frac)) if files else 0
        random.shuffle(files)
        sel = files[:n]

        moved = 0
        for f in sel:
            target = dst / f.name
            if target.exists():
                continue
            shutil.move(str(f), str(target))
            moved += 1

        summary[cls] = dict(total=len(files), moved=moved)

    print("Created val split:")
    for k, v in summary.items():
        print(f"  {k}: moved {v['moved']} of {v['total']}")


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--train", default="data/train")
    p.add_argument("--val", default="data/val")
    p.add_argument("--frac", type=float, default=0.1, help="Fraction to move to val per class")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    make_val_split(train_dir=args.train, val_dir=args.val, frac=args.frac, seed=args.seed)
