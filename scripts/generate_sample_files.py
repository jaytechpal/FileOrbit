#!/usr/bin/env python3
"""
Sample File Generator for FileOrbit Screenshots

This script creates a realistic file and folder structure for taking
professional screenshots of FileOrbit's interface and features.
"""

import sys
from pathlib import Path
import random
import string

def create_sample_files(base_path: Path):
    """Create a realistic file structure for screenshots"""
    
    # Ensure base directory exists
    base_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating sample files in: {base_path}")
    
    # Document files
    documents_dir = base_path / "Documents"
    documents_dir.mkdir(exist_ok=True)
    
    # Create various document types with realistic names
    doc_files = [
        ("Project_Proposal_2025.pdf", 2_500_000),      # 2.5 MB
        ("Financial_Report_Q4.docx", 1_200_000),       # 1.2 MB
        ("Presentation_Slides.pptx", 8_400_000),       # 8.4 MB
        ("Meeting_Notes.txt", 45_000),                 # 45 KB
        ("Spreadsheet_Data.xlsx", 3_100_000),          # 3.1 MB
        ("Contract_Template.pdf", 890_000),            # 890 KB
        ("README.md", 15_000),                         # 15 KB
    ]
    
    for filename, size in doc_files:
        create_file_with_size(documents_dir / filename, size)
    
    # Image files
    images_dir = base_path / "Images"
    images_dir.mkdir(exist_ok=True)
    
    image_files = [
        ("Photo_2025_01_15.jpg", 3_200_000),          # 3.2 MB
        ("Screenshot_Interface.png", 1_800_000),       # 1.8 MB
        ("Logo_Design.svg", 125_000),                 # 125 KB
        ("Wallpaper_4K.bmp", 12_500_000),            # 12.5 MB
        ("Icon_Set.png", 450_000),                    # 450 KB
        ("Diagram.tiff", 2_800_000),                  # 2.8 MB
    ]
    
    for filename, size in image_files:
        create_file_with_size(images_dir / filename, size)
    
    # Video files (for demonstrating large file handling)
    videos_dir = base_path / "Videos"
    videos_dir.mkdir(exist_ok=True)
    
    video_files = [
        ("Demo_Video.mp4", 245_000_000),              # 245 MB
        ("Tutorial_Screencast.mkv", 156_000_000),     # 156 MB
        ("Large_Video_4K.mov", 2_800_000_000),        # 2.8 GB (for 64-bit demo)
        ("Compressed_Video.webm", 89_000_000),        # 89 MB
    ]
    
    for filename, size in video_files:
        create_file_with_size(videos_dir / filename, size)
    
    # Archive files
    archives_dir = base_path / "Archives"
    archives_dir.mkdir(exist_ok=True)
    
    archive_files = [
        ("Backup_2025.zip", 156_000_000),             # 156 MB
        ("Project_Source.7z", 89_000_000),            # 89 MB
        ("Database_Export.tar.gz", 234_000_000),      # 234 MB
        ("Photos_Archive.rar", 512_000_000),          # 512 MB
    ]
    
    for filename, size in archive_files:
        create_file_with_size(archives_dir / filename, size)
    
    # Code and development files
    code_dir = base_path / "Development"
    code_dir.mkdir(exist_ok=True)
    
    # Create subdirectories for realistic code structure
    (code_dir / "src").mkdir(exist_ok=True)
    (code_dir / "tests").mkdir(exist_ok=True)
    (code_dir / "docs").mkdir(exist_ok=True)
    
    code_files = [
        ("src/main.py", 45_000),                      # 45 KB
        ("src/utils.py", 23_000),                     # 23 KB
        ("src/config.json", 8_500),                   # 8.5 KB
        ("tests/test_main.py", 34_000),               # 34 KB
        ("docs/API_Documentation.md", 67_000),        # 67 KB
        ("requirements.txt", 2_500),                  # 2.5 KB
        ("setup.py", 5_600),                          # 5.6 KB
        ("README.md", 12_000),                        # 12 KB
    ]
    
    for filepath, size in code_files:
        create_file_with_size(code_dir / filepath, size)
    
    # Mixed content folder (for demonstrating sorting and filtering)
    mixed_dir = base_path / "Mixed_Content"
    mixed_dir.mkdir(exist_ok=True)
    
    mixed_files = [
        ("data.csv", 1_200_000),                      # 1.2 MB
        ("analysis.ipynb", 890_000),                  # 890 KB
        ("results.json", 345_000),                    # 345 KB
        ("config.xml", 67_000),                       # 67 KB
        ("log_file.txt", 2_300_000),                  # 2.3 MB
        ("database.sqlite", 15_600_000),              # 15.6 MB
    ]
    
    for filename, size in mixed_files:
        create_file_with_size(mixed_dir / filename, size)
    
    print("Sample file structure created successfully!")
    print("\nDirectory structure:")
    print_directory_tree(base_path)

def create_file_with_size(file_path: Path, target_size: int):
    """Create a file with approximately the target size"""
    try:
        with open(file_path, 'wb') as f:
            # For smaller files, write random content
            if target_size < 1_000_000:  # Less than 1MB
                content = ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=target_size))
                f.write(content.encode('utf-8'))
            else:
                # For larger files, write in chunks to avoid memory issues
                chunk_size = 1024 * 1024  # 1MB chunks
                remaining = target_size
                
                while remaining > 0:
                    write_size = min(chunk_size, remaining)
                    chunk = b'0' * write_size  # Simple binary content
                    f.write(chunk)
                    remaining -= write_size
        
        print(f"Created: {file_path.name} ({format_size(target_size)})")
    except Exception as e:
        print(f"Error creating {file_path}: {e}")

def format_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def print_directory_tree(path: Path, prefix: str = "", level: int = 0):
    """Print a directory tree structure"""
    if level > 2:  # Limit depth for readability
        return
    
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        
        if item.is_file():
            size_str = f" ({format_size(item.stat().st_size)})"
            print(f"{prefix}{current_prefix}{item.name}{size_str}")
        else:
            print(f"{prefix}{current_prefix}{item.name}/")
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_directory_tree(item, next_prefix, level + 1)

def main():
    """Main function to create sample files"""
    if len(sys.argv) > 1:
        base_path = Path(sys.argv[1])
    else:
        # Default to a Screenshots_Sample_Data folder in the current directory
        base_path = Path.cwd() / "Screenshots_Sample_Data"
    
    print("FileOrbit Screenshot Sample File Generator")
    print("=" * 45)
    print(f"Target directory: {base_path.absolute()}")
    
    if base_path.exists():
        response = input(f"\nDirectory {base_path} already exists. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    try:
        create_sample_files(base_path)
        print(f"\n✅ Sample files created successfully in: {base_path.absolute()}")
        print("\nThese files can be used for taking professional screenshots of FileOrbit.")
        print("Make sure to:")
        print("1. Use these files for realistic file listings")
        print("2. Demonstrate large file operations with the 2.8GB video file")
        print("3. Show various file types and sizes")
        print("4. Test sorting and filtering with the mixed content")
        
    except Exception as e:
        print(f"❌ Error creating sample files: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
