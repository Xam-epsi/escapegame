import os

def generate_tree(start_path='.', output_file='arborescence.txt'):
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'env', '.idea', '.DS_Store'}
    tree_lines = []

    def walk(dir_path, prefix=""):
        entries = sorted(os.listdir(dir_path))
        entries = [e for e in entries if e not in exclude_dirs]
        entries_count = len(entries)

        for i, entry in enumerate(entries):
            path = os.path.join(dir_path, entry)
            connector = "└── " if i == entries_count - 1 else "├── "
            tree_lines.append(f"{prefix}{connector}{entry}")

            if os.path.isdir(path):
                extension = "    " if i == entries_count - 1 else "│   "
                walk(path, prefix + extension)

    root_name = os.path.basename(os.path.abspath(start_path))
    tree_lines.append(root_name)
    walk(start_path)

    output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(tree_lines))

    print(f"✅ Arborescence enregistrée dans : {output_path}")

if __name__ == "__main__":
    generate_tree()

