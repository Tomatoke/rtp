import argparse
from pathlib import Path
import sys

from .preprocess import load_template, scan_dir, discover_categories
from .pick import rating_filter, pick_random_tags, pick_tags_by_template

def main():
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).resolve().parent.parent
    texts_dir = base_dir / "texts"
    default_dir = texts_dir / "sample"
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, help="texts directory")
    parser.add_argument("-r", "--rating", type=str, choices=["g","p","r"], help="rating")
    parser.add_argument("-c", "--count", type=int, default=5, help="count of tags")
    parser.add_argument("-t", "--template", type=str, help="template key from template.json")
    args = parser.parse_args()
    if args.directory:
        directory = Path(args.directory)
    else:
        directory = default_dir
    if not directory.exists():
        directory = texts_dir / args.directory
        if not directory.exists():
            print(f"Directory '{args.directory}' not found.", file=sys.stderr)
            sys.exit(1)
    known_categories = discover_categories(directory)
    files = scan_dir(directory, known_categories)

    if args.template:
        template_file = directory / "template.json"
        templates = load_template(template_file)
        if args.template not in templates:
            print(f"Template '{args.template}' not found in template.json", file=sys.stderr)
            sys.exit(1)
        template = templates[args.template]
        rating = args.rating if args.rating else template.get("rating", "g")
        files = rating_filter(files, rating)
        file_counts = template.get("values", {})
        pairs = pick_tags_by_template(files, file_counts)
    else:
        rating = args.rating if args.rating else "g"
        files = rating_filter(files, rating)
        pairs = pick_random_tags(files, args.count)

    output_by_cat_file = {}
    for tag, src in pairs:
        f_obj = next((f for f in files if f.name == src), None)
        if not f_obj:
            continue
        cat = f_obj.category
        output_by_cat_file.setdefault(cat, {}).setdefault(f_obj.name, []).append(tag)
    for cat in sorted(known_categories):
        if cat in output_by_cat_file:
            print(f"{cat}:")
            for file_name in sorted(output_by_cat_file[cat]):
                tags = sorted(output_by_cat_file[cat][file_name])
                print(f"  {file_name}: {', '.join(tags)}")

if __name__ == "__main__":
    main()
