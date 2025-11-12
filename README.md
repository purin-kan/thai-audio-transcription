# Thai Audio Transcription Script

Transcribe Thai audio files to text using OpenAI's Whisper Large-v3 model (most accurate free model for Thai). Features batch processing, audio trimming, GPU acceleration, and dual output formats.

## 🚀 Features

- **High Accuracy**: Uses Whisper Large-v3, the best free model for Thai transcription
- **GPU Accelerated**: Automatically uses NVIDIA GPU (CUDA) if available, falls back to CPU
- **Multiple Audio Formats**: Supports MP3, WAV, M4A, FLAC, OGG, WMA
- **Batch Processing**: Transcribe multiple files or entire folders at once
- **Audio Trimming**: Trim audio files to specific durations before transcription
- **Dual Output Formats**:
  - **Timestamped**: `[start → end] text` format (precise segment timing)
  - **Plain text**: Text only, no timestamps (easy to read/edit)
- **Voice Activity Detection**: Filters out silence for better results
- **Language Context**: Optimized for Thai with occasional English words

## 📦 Installation

### 1. Prerequisites
- Python 3.12+ (works with Python 3.11+)
- FFmpeg installed on your system

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg
- **Windows (recommended)**: `winget install ffmpeg`
- **Windows (alternative)**: Download from https://ffmpeg.org/download.html
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 4. (Optional) Install CUDA for GPU Support
For GPU acceleration (15-30x faster):
- Install NVIDIA CUDA Toolkit 12.1+
- Install cuDNN libraries
- PyTorch will automatically use GPU if available

**Note**: Script works fine on CPU too, just slower.

## 🎯 Usage

### Single File Transcription
Edit `main.py` and set:
```python
if __name__ == "__main__":
    audio_file = "audio/your_file.m4a"
    output_file = None  # Optional: custom output name
    transcribe_thai(audio_file, output_file)
```

Then run:
```bash
python main.py
```

### Batch Processing - Specific Files
```python
if __name__ == "__main__":
    audio_files = [
        "audio/file1.m4a",
        "audio/file2.mp3",
        "audio/file3.wav",
    ]
    transcribe_batch(audio_files)
```

### Batch Processing - Entire Folder
```python
if __name__ == "__main__":
    transcribe_batch("audio/my_folder/")
```

### Trim Audio Before Transcription
```python
if __name__ == "__main__":
    # Trim to first 3 minutes (180 seconds)
    trimmed = trim_audio("audio/long_file.m4a", duration_sec=180)
    if trimmed:
        transcribe_thai(trimmed)
```

### Trim with ffmpeg (Command Line)
```bash
ffmpeg -y -i "audio/input.m4a" -t 00:03:00 -c copy "trimmed/output.m4a"
```

## 📝 Output

For each audio file, the script creates **two transcript files** in the `output/` folder:

### 1. Timestamped Format (`*_timestamped.txt`)
```
[0.00s → 2.50s] สวัสดีครับ
[2.50s → 5.80s] วันนี้เราจะมาพูดถึง
[5.80s → 10.20s] เรื่องการเขียนโปรแกรม
[10.20s → 15.60s] ด้วยภาษาไพธอน
```

### 2. Plain Text Format (`*_plain.txt`)
```
สวัสดีครับ วันนี้เราจะมาพูดถึง เรื่องการเขียนโปรแกรม ด้วยภาษาไพธอน
```

**Console Output**:
```
🚀 Loading Whisper large-v3 model...
✅ Using GPU acceleration

🎧 Transcribing audio (Thai language)...

✅ Transcription complete!
   Language: th
   Probability: 99.82%
   Duration: 45.3s

============================================================
[0.00s → 2.50s] สวัสดีครับ
[2.50s → 5.80s] วันนี้เราจะมาพูดถึง
============================================================

✅ Timestamped transcript saved to: output/filename_timestamped.txt
✅ Plain text transcript saved to: output/filename_plain.txt
```

## ⚙️ Accuracy Settings

The script is configured for **maximum accuracy**:
- `beam_size=10` - Explores more transcription possibilities (slower but more accurate)
- `best_of=5` - Generates 5 candidates and picks the best one
- `temperature=0.0` - Most confident/deterministic output
- `condition_on_previous_text=True` - Uses context from previous sentences
- `vad_filter=True` - Filters silence and background noise

### Trade-off
- **Accuracy**: ⬆️⬆️⬆️ Best possible
- **Speed**: ⬇️ About 2-3x slower than base settings

To speed up (less accurate):
```python
# In transcribe_thai() function, change:
beam_size=5,      # (was 10)
best_of=1,        # (was 5)
# Remove temperature=0.0 for default behavior
```

## 🎛️ Model Options

Default: `large-v3` (most accurate for Thai)

Available models:
- `tiny` - Fastest (~1-2 sec per min audio), least accurate
- `base` - Fast, moderate accuracy
- `small` - Balanced speed/accuracy
- `medium` - Better accuracy, slower
- `large-v3` - Best accuracy (recommended), slowest

Change in `transcribe_thai()` or `transcribe_batch()` calls:
```python
transcribe_thai(audio_file, model_size="base")
```

## � Speed Comparison

| Component | Time | Notes |
|-----------|------|-------|
| **Model Loading** | 5-10s | Once per script run |
| **Transcription (GPU)** | 1-2 sec/min audio | RTX 4060 Ti |
| **Transcription (CPU)** | 30-60 sec/min audio | Varies by CPU |
| **Audio Trimming** | 1-5 sec | Depends on file size |

## 📁 Project Structure

```
transcription/
├── main.py              # Main transcription script
├── setup.py             # FFmpeg setup and initialization
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
├── audio/              # Input audio files (not in git)
├── output/             # Transcribed files (not in git)
└── trimmed/            # Trimmed audio files (not in git)
```

## 🔧 Troubleshooting

### "Error: Audio file not found"
- Check that the audio file path is correct
- Use absolute paths if needed: `"C:/full/path/to/file.m4a"`

### "Couldn't find ffmpeg or avconv"
- FFmpeg is not in your system PATH
- Install FFmpeg (see Installation section)
- Or restart your terminal after installing

### "No module named 'faster_whisper'"
- Run: `pip install -r requirements.txt`

### Slow transcription
- First run downloads the model (~3GB) - this is normal
- Use GPU (install CUDA) for 15-30x speedup
- Use smaller model: `model_size="base"` for faster (less accurate) results

### Out of Memory (GPU)
- Use smaller model or shorter audio clips
- Trim audio to 5-10 minute segments

### CUDA errors

- Ensure NVIDIA GPU drivers are installed: `nvidia-smi`
- Install CUDA 12.1+
- Check if PyTorch detects GPU: `python -c "import torch; print(torch.cuda.is_available())"`

### pkg_resources deprecation warning

- **Status**: Known issue in ctranslate2 (faster-whisper dependency)
- **Timeline**: pkg_resources will be removed around Nov 30, 2025
- **Action**: We've pinned setuptools<81 to prevent breaking. Monitor for ctranslate2 updates.
- **Updates**: Run `pip install --upgrade faster-whisper ctranslate2` after Nov 30 to get the fix

## 💡 Tips

1. **Audio Quality Matters**: Clear recordings with minimal background noise produce best results
2. **Batch Processing**: Process multiple files efficiently (model loads once)
3. **Use Timestamped Output**: Better for finding specific parts of the transcription
4. **Trim Long Files**: Process in 10-15 minute chunks for better accuracy and speed

## 📄 License

Uses OpenAI's Whisper model (MIT License)
