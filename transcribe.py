# pip install -r requirements.txt

import warnings
# Suppress FFmpeg warning only (handled FFmpeg in setup.py)
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg or avconv")

from faster_whisper import WhisperModel
from pydub import AudioSegment
import os
import sys
import time

# Import setup module
from setup import initialize

# Run one-time setup
initialize()





def transcribe_thai(audio_path, output_txt=None, model_size="large-v3", model=None, output_base_dir=None):
    """
    Transcribe Thai audio to text using OpenAI's Whisper model (via faster-whisper).
    
    Args:
        audio_path: Path to audio file (supports mp3, wav, m4a, flac, etc.)
        output_txt: Optional custom output path for the transcript
        model_size: Whisper model size (tiny, base, small, medium, large-v3)
                   large-v3 is most accurate for Thai
        model: Pre-loaded WhisperModel instance (for batch processing).
               If None, loads model on-demand (slower for single file).
        output_base_dir: Optional base directory for output. If None, uses 'output/' folder.
                        Used by batch processing to organize by input folder structure.
    
    Returns:
        Transcribed text as string
    """
    
    # Check if file exists
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        return None
    
    # Convert to WAV if needed for better compatibility
    original_path = audio_path
    if not audio_path.lower().endswith(".wav"):
        print(f"Converting {os.path.basename(audio_path)} to WAV format...")
        # Create cache folder for temp files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.join(base_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Save temp WAV in cache folder
        file_name = os.path.splitext(os.path.basename(audio_path))[0]
        wav_path = os.path.join(cache_dir, f"{file_name}_temp.wav")
        try:
            audio = AudioSegment.from_file(audio_path)
            audio.export(wav_path, format="wav")
            audio_path = wav_path
            print("Conversion complete")
        except Exception as e:
            print(f"Warning: Could not convert to WAV: {e}")
            print("Trying to transcribe original file...")
    
    # Load Whisper model (or use pre-loaded one if provided)
    if model is None:
        print(f"Loading Whisper {model_size} model (faster-whisper)...")
        try:
            # Try GPU first (CUDA), fall back to CPU if not available
            try:
                model = WhisperModel(model_size, device="cuda", compute_type="float16")
                print("✅ Using GPU acceleration")
            except:
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
                print("✅ Using CPU (no GPU detected)")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return None
    else:
        print("✅ Using pre-loaded model")
    
    # Transcribe
    print("Transcribing audio (Thai language)...")
    try:
        segments, info = model.transcribe(
            audio_path, 
            language="th",  # Primary language is Thai (skips auto-detection for faster processing)
            beam_size=5,  # Reduced to prevent over-fitting and hallucination
            best_of=3,  # Reduced candidates for more stable predictions
            temperature=0.2,  # Slightly increased for diversity (was 0.0 = too rigid)
            vad_filter=True,  # Voice Activity Detection to filter silence
            vad_parameters=dict(min_silence_duration_ms=800),  # Increased from 500ms
            word_timestamps=False,  # Disable word-level timestamps for faster processing
            condition_on_previous_text=False,
            compression_ratio_threshold=2.4,  # Detect and skip repetitive segments
            log_prob_threshold=-1.0,  # Skip low-confidence segments
            no_speech_threshold=0.7,  # Increased from 0.6 to be more aggressive with silence
        )
        
        print(f"   Language: {info.language}")
        print(f"   Probability: {info.language_probability:.2%}")
        print(f"   Duration: {info.duration:.1f}s\n")
        
        # Collect segments - two formats
        full_text = ""  # Plain text (no timestamps)
        timestamped_text = ""  # Format: [start → end] text
        
        print("=" * 60)
        for seg in segments:
            print(f"[{seg.start:.2f}s → {seg.end:.2f}s] {seg.text}")
            full_text += seg.text + " "
            timestamped_text += f"[{seg.start:.2f}s → {seg.end:.2f}s] {seg.text}\n"
        print("=" * 60)
        
        # Save output in 'output' folder (or custom base directory)
        if output_base_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        else:
            output_dir = output_base_dir
        os.makedirs(output_dir, exist_ok=True)
        
        if output_txt is None:
            base_name = os.path.splitext(os.path.basename(original_path))[0]
        else:
            # If user provides a filename, use it as base name
            if not os.path.isabs(output_txt):
                base_name = os.path.splitext(output_txt)[0]
            else:
                base_name = os.path.splitext(os.path.basename(output_txt))[0]
        
        # Save timestamped version (with [start → end] format)
        timestamped_path = os.path.join(output_dir, f"{base_name}_timestamped.txt")
        with open(timestamped_path, "w", encoding="utf-8") as f:
            f.write(timestamped_text.strip())
        print(f"\n✅ Timestamped transcript saved to: {timestamped_path}")
        
        # Save plain text version (text only, no timestamps)
        plain_path = os.path.join(output_dir, f"{base_name}_plain.txt")
        with open(plain_path, "w", encoding="utf-8") as f:
            f.write(full_text.strip())
        print(f"✅ Plain text transcript saved to: {plain_path}")
        # Clean up temporary WAV file
        if audio_path != original_path and os.path.exists(audio_path):
            os.remove(audio_path)
        return full_text.strip()
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def transcribe_batch(audio_files, model_size="large-v3", model=None):
    """
    Batch process multiple audio files.
    
    Args:
        audio_files: List of audio file paths or folder path
        model_size: Whisper model size (tiny, base, small, medium, large-v3)
        model: Pre-loaded WhisperModel instance. If None, loads model on-demand.
    
    Returns:
        Dictionary with results for each file
    """
    # If a single folder path is provided, get all audio files from it
    input_folder = None
    if isinstance(audio_files, str) and os.path.isdir(audio_files):
        input_folder = audio_files
        folder = audio_files
        audio_files = []
        # Search recursively for audio files in all subfolders
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith((".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".mp4", ".mkv")):
                    audio_files.append(os.path.join(root, file))
    
    if not audio_files:
        print("❌ No audio files found!")
        return {}
    
    print(f"\n{'='*60}")
    print(f"🔄 BATCH PROCESSING: {len(audio_files)} file(s)")
    print(f"{'='*60}\n")
    
    # Determine output directory based on input folder structure
    # If input is "audio_input/Baka_Survey/Central", output will be "output/Baka_Survey/Central"
    if input_folder:
        # Get relative path from project root to input folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        input_folder_abs = os.path.abspath(input_folder)
        # Try to find a meaningful relative path from base_dir
        try:
            rel_path = os.path.relpath(input_folder_abs, base_dir)
            # Remove "audio_input" prefix if present (e.g., "audio_input/Baka_Survey/Central" → "Baka_Survey/Central")
            if rel_path.startswith("audio_input" + os.sep):
                rel_path = rel_path[len("audio_input" + os.sep):]
            output_base_dir = os.path.join(base_dir, "output", rel_path)
        except ValueError:
            # If on different drives (Windows), just use the folder name
            output_base_dir = os.path.join(base_dir, "output", os.path.basename(input_folder_abs))
    else:
        output_base_dir = None
    
    # Load model ONCE for all files (or use pre-loaded one if provided)
    if model is None:
        print(f"Loading Whisper {model_size} model (faster-whisper)...")
        try:
            # Try GPU first (CUDA), fall back to CPU if not available
            try:
                model = WhisperModel(model_size, device="cuda", compute_type="float16")
                print("✅ Using GPU acceleration\n")
            except:
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
                print("✅ Using CPU (no GPU detected)\n")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return {}
    else:
        print("✅ Using pre-loaded model\n")
    
    results = {}
    for idx, audio_file in enumerate(audio_files, 1):
        print(f"\n[{idx}/{len(audio_files)}] Processing: {os.path.basename(audio_file)}")
        print("-" * 60)
        # Pass the pre-loaded model and output directory to avoid reloading for each file
        try:
            result = transcribe_thai(audio_file, model_size=model_size, model=model, output_base_dir=output_base_dir)
            results[audio_file] = result
        except Exception as e:
            print(f"❌ FAILED: {os.path.basename(audio_file)}")
            print(f"   Error: {str(e)}")
            results[audio_file] = None
        print()
    
    print(f"\n{'='*60}")
    print(f"✅ BATCH PROCESSING COMPLETE!")
    print(f"{'='*60}")
    successful = sum(1 for v in results.values() if v is not None)
    print(f"Successfully processed: {successful}/{len(audio_files)} files")
    
    # Print failed files
    if successful < len(audio_files):
        print(f"\n❌ Failed files ({len(audio_files) - successful}):")
        for audio_file, result in results.items():
            if result is None:
                print(f"   - {os.path.basename(audio_file)}")
    
    if output_base_dir:
        print(f"\nOutput folder: {output_base_dir}\n")
    else:
        print(f"Output folder: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')}\n")
    
    return results

    
def trim_audio(input_path, output_path=None, duration_sec=180):
    """
    Trim an audio file to the first `duration_sec` seconds and save the result.

    Args:
        input_path: Path to the source audio file (supports mp3, m4a, wav, etc.).
        output_path: Optional path to save trimmed file. If None, a file is created
                     in a `trimmed/` subfolder next to this script with suffix
                     `_trimmed` added.
        duration_sec: Number of seconds to keep from the start (default 180 = 3 min).

    Returns:
        The path to the trimmed file, or None on error.
    """
    if not os.path.exists(input_path):
        print(f"Error: input file not found: {input_path}")
        return None

    # prepare output path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    trimmed_dir = os.path.join(base_dir, "trimmed")
    os.makedirs(trimmed_dir, exist_ok=True)

    root, ext = os.path.splitext(os.path.basename(input_path))
    ext = ext.lstrip('.').lower() or 'wav'
    
    # Map file extensions to pydub export formats
    # m4a and mp4 both use 'mp4' format in pydub
    format_map = {
        'm4a': 'mp4',
        'mp4': 'mp4',
        'aac': 'mp4',
    }
    export_format = format_map.get(ext, ext)
    
    if output_path is None:
        output_path = os.path.join(trimmed_dir, f"{root}_trimmed_{duration_sec}s.{ext}")
    else:
        # if not absolute, place inside trimmed_dir
        if not os.path.isabs(output_path):
            output_path = os.path.join(trimmed_dir, output_path)

    try:
        audio = AudioSegment.from_file(input_path)
        duration_ms = int(duration_sec * 1000)
        trimmed = audio[:duration_ms]
        # export using the mapped format
        trimmed.export(output_path, format=export_format)
        print(f"✅ Trimmed audio saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error trimming audio: {e}")
        return None

