#!/usr/bin/env python3
"""
Check for duplicate lines in timestamped transcription output.
Reads all *_timestamped.txt files in the output directory and reports files with duplicates.
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def extract_text_from_timestamped(line):
    """
    Extract just the text part from a timestamped line.
    Format: [00.00s → 00.00s] text here
    Returns the text part without the timestamp.
    """
    match = re.match(r'\[\d{2}\.\d{2}s → \d{2}\.\d{2}s\]\s*(.*)', line.strip())
    if match:
        return match.group(1)
    return line.strip()


def check_duplicates_in_file(filepath):
    """
    Check a single timestamped file for duplicate lines.
    Only counts duplicates that are at least 10 characters long.
    Returns a list of (text, count) tuples for lines appearing more than once.
    """
    duplicates = defaultdict(int)
    seen = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                text = extract_text_from_timestamped(line)
                # Only process lines that are at least 10 characters long
                if text and len(text) >= 10:
                    if text in seen:
                        duplicates[text] += 1
                    else:
                        seen[text] = line_num
                        duplicates[text] = 1
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return []
    
    # Return only lines that appear more than once
    return [(text, count) for text, count in duplicates.items() if count > 1]


def check_all_timestamped_files(output_dir="output"):
    """
    Check all *_timestamped.txt files in the output directory.
    Returns a dict mapping filenames to their duplicate lines.
    """
    files_with_duplicates = {}
    
    # Find all timestamped files recursively
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"⚠️ Output directory '{output_dir}' not found!")
        return files_with_duplicates
    
    timestamped_files = list(output_path.glob("**/*_timestamped.txt"))
    
    if not timestamped_files:
        print(f"ℹ️ No timestamped files found in '{output_dir}'")
        return files_with_duplicates
    
    print(f"🔍 Checking {len(timestamped_files)} timestamped file(s)...\n")
    
    for filepath in timestamped_files:
        duplicates = check_duplicates_in_file(filepath)
        if duplicates:
            rel_path = filepath.relative_to(output_path)
            files_with_duplicates[str(rel_path)] = duplicates
    
    return files_with_duplicates


def print_report(files_with_duplicates):
    """
    Print a formatted report of files with duplicates.
    Only shows filenames, not the duplicate text.
    """
    if not files_with_duplicates:
        print("✅ No duplicate lines found in any transcription files!")
        return
    
    print(f"\n{'='*70}")
    print(f"⚠️  FILES WITH DUPLICATE LINES: {len(files_with_duplicates)}")
    print(f"{'='*70}\n")
    
    for filepath in sorted(files_with_duplicates.keys()):
        filename = Path(filepath).stem.replace("_timestamped", "")
        print(f"   • {filename}")
    
    print(f"\n{'='*70}\n")


def main():
    print("🔎 Duplicate Line Checker for Transcriptions\n")
    
    # Check the output directory
    files_with_duplicates = check_all_timestamped_files("output")
    
    # Print the report
    print_report(files_with_duplicates)
    
    return files_with_duplicates


if __name__ == "__main__":
    main()
