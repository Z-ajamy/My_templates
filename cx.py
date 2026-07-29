#!/usr/bin/env python3
import os
import sys
import argparse
import re

# ================= Default Configurations =================
DEFAULT_EXCLUDE_DIRS = {
    '.git', 'venv', '.venv', 'env', 'node_modules', '__pycache__', 
    'target', 'build', 'dist', '.vscode', '.idea', 'out', 
    '.ruff_cache', '.pytest_cache', '.mypy_cache', '.tox', '.next'
}

DEFAULT_EXCLUDE_FILES = {
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Cargo.lock', 'CACHEDIR.TAG'
}

DEFAULT_EXCLUDE_EXTS = {
    '.toml', '.json', '.md', '.txt', '.log', '.pyc', '.tag',
    '.exe', '.dll', '.so', '.png', '.jpg', '.pdf', '.zip', '.tar'
}

DEFAULT_EXCLUDE_REGEXES = [
    r"\.min\.(js|css)$",       
    r".*migrations.*",         
    r"(^|/)\.[^/]+$",          
]
# =======================================================

def get_empty_file_comment(ext):
    if ext in ['.py', '.sh', '.rb', '.yaml', '.yml', '.conf']:
        return "# [Empty File or Contains Only Comments]"
    elif ext in ['.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', '.cs', '.php', '.swift']:
        return "// [Empty File or Contains Only Comments]"
    elif ext in ['.html', '.xml', '.svg']:
        return "<!-- [Empty File or Contains Only Comments] -->"
    elif ext in ['.css']:
        return "/* [Empty File or Contains Only Comments] */"
    elif ext in ['.sql']:
        return "-- [Empty File or Contains Only Comments]"
    else:
        return "[Empty File]"

def is_comment_line(line, ext):
    stripped = line.strip()
    if not stripped:
        return False 
        
    if ext in ['.py', '.sh', '.rb', '.yaml', '.yml']:
        return stripped.startswith('#') and not stripped.startswith('##')
        
    if ext in ['.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', '.cs']:
        return stripped.startswith('//') and not stripped.startswith('////')
        
    return False

def process_project(target_dir, limit=None, match_pattern=None, tree_only=False):
    # ⚙️ Compile Regexes
    compiled_regexes = []
    for pattern in DEFAULT_EXCLUDE_REGEXES:
        try:
            compiled_regexes.append(re.compile(pattern))
        except re.error as e:
            print(f"⚠️  [WARNING] Invalid regex pattern '{pattern}': {e}")

    # ================= Phase 1: Collect Valid Files =================
    valid_files = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE_DIRS and not d.startswith('.')]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            file_path = os.path.join(root, file)

            if file in DEFAULT_EXCLUDE_FILES or ext in DEFAULT_EXCLUDE_EXTS:
                continue
                
            if any(regex.search(file_path) for regex in compiled_regexes):
                continue
            
            if match_pattern and match_pattern.lower() not in file_path.lower():
                continue

            valid_files.append(file_path)
            
            if limit and len(valid_files) >= limit:
                break
        if limit and len(valid_files) >= limit:
            break

    # ================= Phase 2: Print 2D Nested Tree =================
    if not valid_files:
        print("\n\033[93m⚠️  [INFO] No files found matching the criteria.\033[0m")
        return

    print("\n\033[92m📂 === Project Structure ===\033[0m")
    
    # 1. Build a nested dictionary from paths
    tree_dict = {}
    for fpath in valid_files:
        # Standardize slashes
        parts = fpath.replace('\\', '/').split('/')
        current = tree_dict
        for part in parts:
            if part:
                current = current.setdefault(part, {})

    # 2. Recursive function to print the tree beautifully
    def print_tree(node, prefix="", current_path=""):
        keys = sorted(node.keys())
        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)
            connector = "└── " if is_last else "├── "
            
            # Reconstruct the true path for the AI context
            node_path = f"{current_path}/{key}" if current_path else key
            
            if not node[key]:  # Leaf node (File)
                # Print: Prefix + Connector + File Name (White) + Full Path (Dimmed Gray)
                print(f"{prefix}{connector}\033[97m{key}\033[0m \033[90m({node_path})\033[0m")
            else:  # Directory
                # Print Directory Name (Cyan)
                print(f"{prefix}{connector}\033[96m{key}/\033[0m")
                new_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(node[key], new_prefix, node_path)

    print_tree(tree_dict)
    print("\033[92m=============================\033[0m\n")

    if tree_only:
        return

    # ================= Phase 3: Print File Contents =================
    for file_path in valid_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            ext = os.path.splitext(file_path)[1].lower()
            
            cleaned_lines = [
                line for line in lines 
                if not is_comment_line(line, ext)
            ]
            
            if not any(line.strip() for line in cleaned_lines):
                cleaned_lines = [get_empty_file_comment(ext)]

            print(f"\n\033[94m📄 {'='*15} {file_path} {'='*15}\033[0m")
            print("".join(cleaned_lines).strip())

        except UnicodeDecodeError:
            pass
        except Exception as e:
            print(f"⚠️  [WARNING] Failed to read '{file_path}': {e}")

def main():
    parser = argparse.ArgumentParser(
        description="✨ AI Context Preparer: Outputs clean code (without standard comments) to feed into AI models."
    )
    
    parser.add_argument("directory", nargs="?", default=".", help="📁 Target directory to scan (default: current directory)")
    parser.add_argument("-n", "--limit", type=int, help="🛑 Maximum number of files to print")
    parser.add_argument("-m", "--match", type=str, help="🔍 Print only files containing this string in their name/path")
    parser.add_argument("-t", "--tree", action="store_true", help="🌳 Print ONLY the project structure (tree) and skip file contents")
    
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"❌ [ERROR] Directory not found or invalid path: {args.directory}")
        sys.exit(1)

    process_project(args.directory, args.limit, args.match, args.tree)

if __name__ == "__main__":
    main()

