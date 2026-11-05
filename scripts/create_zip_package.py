import os
import zipfile
import sys
from pathlib import Path

def create_project_zip():
    root_dir = Path(__file__).resolve().parent.parent
    output_zip = root_dir / "WorkCheck-Kachchh-SSIP-Website-Complete.zip"
    
    print(f"Packaging project from: {root_dir}")
    print(f"Target archive: {output_zip}")
    
    # Folders to include
    include_folders = [
        "app",
        "charts",
        "data",
        "database",
        "db",
        "docs",
        "final_dataset",
        "rules_engine",
        "scripts",
        "services",
        "tests"
    ]
    
    # Root files to include
    include_files = [
        "index.html",
        "requirements.txt",
        "run_website.bat",
        "README.md",
        "DATASET_CATALOG_PUBLIC_DOWNLOADS.md",
        ".gitignore"
    ]
    
    # Exclude patterns
    exclude_patterns = [
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".vscode",
        ".idea",
        "*.pyc",
        "*.pyo",
        "WorkCheck-Kachchh-SSIP-Website-Complete.zip",
        "PS000109_final_dataset_csv.zip" # Avoid re-compressing existing giant zip inside zip
    ]
    
    total_files = 0
    total_uncompressed_bytes = 0
    
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        # Add root files
        for fname in include_files:
            fpath = root_dir / fname
            if fpath.exists() and fpath.is_file():
                arcname = fname
                zipf.write(fpath, arcname)
                size = fpath.stat().st_size
                total_files += 1
                total_uncompressed_bytes += size
                print(f"  Added root file: {arcname} ({size:,} bytes)")
        
        # Add included directories recursively
        for folder_name in include_folders:
            folder_path = root_dir / folder_name
            if not folder_path.exists() or not folder_path.is_dir():
                continue
            
            for root, dirs, files in os.walk(folder_path):
                # Prune excluded directories
                dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"]]
                
                for f in files:
                    if f.endswith((".pyc", ".pyo", ".DS_Store")):
                        continue
                    if f.endswith(".zip") and f.startswith("WorkCheck"):
                        continue
                    
                    full_p = Path(root) / f
                    arcname = full_p.relative_to(root_dir).as_posix()
                    zipf.write(full_p, arcname)
                    size = full_p.stat().st_size
                    total_files += 1
                    total_uncompressed_bytes += size
                    
    zip_size = output_zip.stat().st_size
    print("\n" + "=" * 60)
    print("ZIP PACKAGE CREATED SUCCESSFULLY!")
    print(f"Archive: {output_zip.name}")
    print(f"Absolute Path: {output_zip}")
    print(f"Total Files Archived: {total_files}")
    print(f"Uncompressed Size: {total_uncompressed_bytes / (1024*1024):.2f} MB")
    print(f"Compressed ZIP Size: {zip_size / (1024*1024):.2f} MB")
    print(f"Compression Ratio: {(1 - zip_size / total_uncompressed_bytes)*100:.1f}% reduction")
    print("=" * 60)

if __name__ == "__main__":
    create_project_zip()
