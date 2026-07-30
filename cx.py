#!/usr/bin/env python3
import os
import sys
import argparse
import re
import fnmatch

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
    elif ext in ['.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', '.cs']:
        return "// [Empty File or Contains Only Comments]"
    elif ext in ['.html', '.xml', '.svg']:
        return "<!-- [Empty File or Contains Only Comments] -->"
    elif ext in ['.css']:
        return "/* [Empty File or Contains Only Comments] */"
    else:
        return "[Empty File]"

def is_comment_line(line, ext):
    stripped = line.strip()
    if not stripped: return False 
    if ext in ['.py', '.sh', '.rb', '.yaml', '.yml']:
        return stripped.startswith('#') and not stripped.startswith('##')
    if ext in ['.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', '.cs']:
        return stripped.startswith('//') and not stripped.startswith('////')
    return False

def process_targets(targets, limit=None, tree_only=False, include_pat=None, exclude_pat=None, show_all=False):
    valid_files = []
    
    # ⚙️ Convert standard Linux globs (*.py, *test*) to Regex automatically
    def compile_user_pattern(pattern_str):
        if not pattern_str: return None
        try:
            # Allow multiple patterns separated by |
            rx_list = [fnmatch.translate(p.strip()) for p in pattern_str.split('|')]
            return re.compile("|".join(rx_list), re.IGNORECASE)
        except Exception as e:
            print(f"⚠️  [WARNING] Invalid pattern '{pattern_str}': {e}")
            return None

    inc_rx = compile_user_pattern(include_pat)
    exc_rx = compile_user_pattern(exclude_pat)
    
    # Compile default explicit regexes
    def_rx_list = []
    if not show_all:
        for p in DEFAULT_EXCLUDE_REGEXES:
            try: def_rx_list.append(re.compile(p))
            except: pass

    # ================= Phase 1: Collect Valid Files =================
    for target in targets:
        if os.path.isfile(target):
            valid_files.append(target)
            continue
            
        for root, dirs, files in os.walk(target):
            std_root = root.replace('\\', '/')

            valid_dirs = []
            for d in dirs:
                dir_path = f"{std_root}/{d}" if std_root != "." else d
                
                if exc_rx and exc_rx.search(dir_path):
                    continue
                    
                if not show_all:
                    if d in DEFAULT_EXCLUDE_DIRS or d.startswith('.'):
                        continue
                        
                valid_dirs.append(d)
            dirs[:] = valid_dirs 

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                file_path = os.path.join(root, file)
                std_file_path = file_path.replace('\\', '/')

                if exc_rx and exc_rx.search(std_file_path):
                    continue

                if inc_rx and not inc_rx.search(std_file_path):
                    continue

                if not show_all:
                    if file in DEFAULT_EXCLUDE_FILES or ext in DEFAULT_EXCLUDE_EXTS:
                        continue
                    if any(r and r.search(std_file_path) for r in def_rx_list):
                        continue

                valid_files.append(file_path)
                
                if limit and len(valid_files) >= limit: break
            if limit and len(valid_files) >= limit: break

    # ================= Phase 2: Print Tree =================
    if not valid_files:
        print("\n\033[93m⚠️  [INFO] No files found matching the criteria.\033[0m")
        return

    print("\n\033[92m📂 === Project Structure ===\033[0m")
    tree_dict = {}
    for fpath in valid_files:
        parts = fpath.replace('\\', '/').split('/')
        current = tree_dict
        for part in parts:
            if part: current = current.setdefault(part, {})

    def print_tree(node, prefix="", current_path=""):
        keys = sorted(node.keys())
        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)
            connector = "└── " if is_last else "├── "
            node_path = f"{current_path}/{key}" if current_path else key
            
            if not node[key]:  
                print(f"{prefix}{connector}\033[97m{key}\033[0m \033[90m({node_path})\033[0m")
            else:  
                print(f"{prefix}{connector}\033[96m{key}/\033[0m")
                new_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(node[key], new_prefix, node_path)

    print_tree(tree_dict)
    print("\033[92m=============================\033[0m\n")

    if tree_only: return

    # ================= Phase 3: Print Contents =================
    for file_path in valid_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            ext = os.path.splitext(file_path)[1].lower()
            cleaned_lines = [line for line in lines if not is_comment_line(line, ext)]
            
            if not any(line.strip() for line in cleaned_lines):
                cleaned_lines = [get_empty_file_comment(ext)]

            print(f"\n\033[94m📄 {'='*15} {file_path} {'='*15}\033[0m")
            print("".join(cleaned_lines).strip())
        except UnicodeDecodeError: pass
        except Exception as e:
            print(f"⚠️  [WARNING] Failed to read '{file_path}': {e}")

def main():
    parser = argparse.ArgumentParser(description="✨ AI Context Preparer - Clean, Standard, and Fast.")
    
    parser.add_argument("targets", nargs="*", default=["."], help="📁 Files/Dirs to scan (e.g., src/ main.py)")
    
    # 🎛️ FILTERS (Now accepts standard Globs like *.py)
    parser.add_argument("-i", "--include", type=str, help="✅ Pattern to INCLUDE (e.g., \"*.py\")")
    parser.add_argument("-x", "--exclude", type=str, help="❌ Pattern to EXCLUDE (e.g., \"*test*\")")
    
    parser.add_argument("-a", "--all", action="store_true", help="🔓 Force scan EVERYTHING")
    parser.add_argument("-n", "--limit", type=int, help="🛑 Maximum number of files to print")
    parser.add_argument("-t", "--tree", action="store_true", help="🌳 Print ONLY the project structure")
    
    args = parser.parse_args()

    valid_targets = [t for t in args.targets if os.path.exists(t)]
    if not valid_targets:
        print("❌ [ERROR] No valid targets to scan.")
        sys.exit(1)

    process_targets(
        valid_targets, args.limit, args.tree,
        include_pat=args.include, exclude_pat=args.exclude, show_all=args.all
    )

if __name__ == "__main__":
    main()
