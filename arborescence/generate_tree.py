import os

def generate_tree(start_path='.', output_file='arborescence.txt'):
    # Dossiers à exclure
    exclude_dirs = {
        '.git', '__pycache__', 'node_modules', 'env', '.env', 'venv',
        '.venv', '.idea', '.DS_Store', '.pytest_cache'
    }

    # Extensions de fichiers à exclure
    exclude_ext = {
        '.pyc', '.pyo', '.pyd', '.log', '.sqlite', '.db', '.so',
        '.dll', '.exe', '.zip', '.tar', '.gz'
    }

    tree_lines = []

    def walk(dir_path, prefix=""):
        try:
            entries = sorted(os.listdir(dir_path))
        except PermissionError:
            return  # Ignore les répertoires non accessibles

        entries = [
            e for e in entries
            if e not in exclude_dirs
            and not any(e.endswith(ext) for ext in exclude_ext)
        ]

        entries_count = len(entries)
        for i, entry in enumerate(entries):
            path = os.path.join(dir_path, entry)
            connector = "└── " if i == entries_count - 1 else "├── "
            tree_lines.append(f"{prefix}{connector}{entry}")

            if os.path.isdir(path):
                extension = "    " if i == entries_count - 1 else "│   "
                walk(path, prefix + extension)

    # Nom du dossier racine
    root_name = os.path.basename(os.path.abspath(start_path)) or start_path
    tree_lines.append(root_name)
    walk(start_path)

    output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(tree_lines))

    print(f"✅ Arborescence enregistrée dans : {output_path}")


if __name__ == "__main__":
    generate_tree()
