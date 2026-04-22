import os
import shutil
import random
from pathlib import Path

RND_SEED = 42
CLASS_MAP = {"benign": "benign", "malignant": "malignant"}


def find_source_dir():
    candidates = [
        Path("data/raw"),
        Path("data/processed"),
        Path("data/all"),
        Path("data/train"),
    ]
    for c in candidates:
        if c.exists() and any((c / k).exists() for k in CLASS_MAP.keys()):
            return c
    raise FileNotFoundError("No source directory with class folders found. Create data/raw or data/train with 'benign' and 'malignant' subfolders.")


def make_dirs(base_out):
    for split in ["train", "val", "test"]:
        for cls in CLASS_MAP.values():
            p = Path(base_out) / split / cls
            p.mkdir(parents=True, exist_ok=True)


def split_class_files(files, ratios=(0.7, 0.15, 0.15)):
    n = len(files)
    n_train = int(n * ratios[0])
    n_val = int(n * ratios[1])
    n_test = n - n_train - n_val
    return files[:n_train], files[n_train:n_train + n_val], files[n_train + n_val:]


def copy_files(file_list, dst_dir):
    for src in file_list:
        dst = dst_dir / src.name
        # if name collision, add suffix
        if dst.exists():
            stem = src.stem
            suff = src.suffix
            i = 1
            while True:
                newname = f"{stem}_{i}{suff}"
                dst = dst_dir / newname
                if not dst.exists():
                    break
                i += 1
        # Move rather than copy for speed
        shutil.move(str(src), str(dst))


def main(source_dir=None, out_base="data"):
    random.seed(RND_SEED)
    src = Path(source_dir) if source_dir else find_source_dir()
    print(f"Using source: {src}")

    make_dirs(out_base)

    for cls_name, cls_id in CLASS_MAP.items():
        cls_src = src / cls_name
        if not cls_src.exists():
            print(f"Warning: class folder missing: {cls_src}")
            continue
        files = [p for p in cls_src.iterdir() if p.is_file()]
        files.sort()
        random.shuffle(files)

        train_files, val_files, test_files = split_class_files(files)

        copy_files(train_files, Path(out_base) / "train" / cls_id)
        copy_files(val_files, Path(out_base) / "val" / cls_id)
        copy_files(test_files, Path(out_base) / "test" / cls_id)

        print(f"Class '{cls_name}' -> train: {len(train_files)}, val: {len(val_files)}, test: {len(test_files)}")

    print("Done. Dataset split created under", out_base)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Split dataset into train/val/test with 70/15/15 and map classes to 0/1")
    parser.add_argument("--source", help="Source directory containing 'benign' and 'malignant' folders (optional)")
    parser.add_argument("--out", default="data", help="Output base directory (default: data)")
    args = parser.parse_args()

    main(source_dir=args.source, out_base=args.out)
