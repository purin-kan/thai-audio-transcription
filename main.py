#!/usr/bin/env python3
"""
Execution script for Thai audio transcription.
Handles model loading and batch processing orchestration.
"""

import sys
import time
from transcribe import transcribe_thai, transcribe_batch, trim_audio
from check_duplicates import check_all_timestamped_files, print_report
from faster_whisper import WhisperModel


start_time = time.time()


# --------------------- USAGE EXAMPLES ---------------------
# 1) Trim an audio file to the first 3 minutes (180s) and transcribe the trimmed clip:
# trimmed = trim_audio("audio_input/drItthisek.m4a", duration_sec=180)
# transcribe_thai(trimmed)

# 2) Trim and provide a custom output filename for the trimmed clip:
# trimmed = trim_audio("audio_input/drItthisek.m4a", output_path="short_clip.m4a", duration_sec=180)
# transcribe_thai(trimmed, output_txt="short_clip_transcript.txt")

# ----------------------------------------------------------

model_size = "large-v3"
print(f"Loading Whisper {model_size} model (faster-whisper)...\n")
try:
    try:
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
        print("✅ Using GPU acceleration\n")
    except:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("✅ Using CPU (no GPU detected)\n")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    sys.exit(1)

# Helper: process batches with pre-loaded model
def process_batch(path):
    return transcribe_batch(path)

# ===== EXECUTION MODES =====

# MODE 1: Single file transcription
# audio_file = "audio_input/drItthisek.m4a"
# output_file = None 
# transcribe_thai(audio_file, output_file)
transcribe_thai("audio_input/Baka_Survey/Esan/Title/2025-11-07 14-37-31.mkv", "audio_input/Baka_Survey/Title/")

# MODE 2: Trim and transcribe
# trimmed = trim_audio("audio_input/drItthisek.m4a", duration_sec=180)
# transcribe_thai(trimmed)

# MODE 3: Batch processing - List of files
audio_files = [
    "audio_input/Baka_Survey/Central/Interviewee 2.m4a",
    "audio_input/Baka_Survey/Central/New Recording 31.m4a",
]
# transcribe_batch(audio_files)

# MODE 4: Batch processing - Entire folder(s)
# Uncomment the folders you want to process:
# process_batch("audio_input/Baka_Survey")
# process_batch("audio_input/Baka_Survey/Central")
# process_batch("audio_input/Baka_Survey/Esan")
# process_batch("audio_input/Baka_Survey/Title")




# ===== Check for duplicates =====

# Check for duplicate lines in transcriptions
print("\n" + "="*60)
print("Running duplicate checker...")
print("="*60)
files_with_duplicates = check_all_timestamped_files("output")
print_report(files_with_duplicates)


# ===== SHOW ELAPSED TIME =====

elapsed_time = time.time() - start_time
hours = int(elapsed_time // 3600)
minutes = int((elapsed_time % 3600) // 60)
seconds = int(elapsed_time % 60)

if hours > 0:
    time_str = f"{hours}h {minutes}m {seconds}s"
elif minutes > 0:
    time_str = f"{minutes}m {seconds}s"
else:
    time_str = f"{seconds}s"

print(f"\n{'='*60}")
print(f"Total elapsed time: {time_str}")
print(f"{'='*60}\n")
