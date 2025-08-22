"""Coqui XTTS v2 TTS engine for high-quality audiobook generation."""
import os
import tempfile
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class VoiceEngine:
    """Coqui XTTS v2 TTS service for audiobook conversion."""
    
    def __init__(self):
        self.model = None
        self.device = "cpu"  # Use CPU for compatibility
        self.voices = self._get_default_voices()
        self.initialize_engine()
        
    def initialize_engine(self):
        """Initialize Coqui XTTS v2 model."""
        try:
            from TTS.api import TTS
            import torch
            
            # Use GPU if available, otherwise CPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")
            
            # Initialize XTTS v2 model
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            logger.info("Coqui XTTS v2 engine initialized successfully")
            
        except ImportError as e:
            logger.error("Coqui TTS not available. Install with: pip install TTS torch torchaudio")
            raise ImportError("Coqui TTS is required but not installed") from e
        except Exception as e:
            logger.error(f"Failed to initialize Coqui XTTS: {e}")
            raise
    
    def _get_default_voices(self):
        """Get available XTTS v2 voices."""
        return [
            {
                'id': 'xtts_female_narrator',
                'name': 'Female Narrator',
                'speaker': 'Claribel Dervla',
                'gender': 'female',
                'description': 'Clear, professional female voice perfect for audiobooks',
                'quality': 'premium'
            },
            {
                'id': 'xtts_male_narrator',
                'name': 'Male Narrator', 
                'speaker': 'Abrahan Mack',
                'gender': 'male',
                'description': 'Warm, authoritative male voice ideal for storytelling',
                'quality': 'premium'
            },
            {
                'id': 'xtts_warm_female',
                'name': 'Warm Female Voice',
                'speaker': 'Gitta Nikolina',
                'gender': 'female',
                'description': 'Gentle, conversational female tone',
                'quality': 'premium'
            },
            {
                'id': 'xtts_storyteller',
                'name': 'Storyteller',
                'speaker': 'Daisy Studious',
                'gender': 'female',
                'description': 'Dynamic voice perfect for fiction and narratives',
                'quality': 'premium'
            }
        ]
    
    def get_available_voices(self, user_tier='free'):
        """Get all available voices (simplified - no tier restrictions)."""
        return self.voices
    
    def synthesize_speech(self, text, voice_id='xtts_female_narrator', output_path=None, user_tier='free'):
        """Synthesize speech using Coqui XTTS v2."""
        if not output_path:
            output_path = tempfile.mktemp(suffix='.wav')
        
        # Get voice info
        voice_info = self.get_voice_info(voice_id)
        if not voice_info:
            # Fallback to default voice
            voice_info = self.voices[0]
            logger.warning(f"Voice {voice_id} not found, using fallback: {voice_info['id']}")
        
        try:
            # Get speaker name
            speaker = voice_info['speaker']
            
            # Clean text for better TTS results
            cleaned_text = self._clean_text_for_tts(text)
            
            # Split long text into chunks if needed
            chunks = self._split_text_into_chunks(cleaned_text)
            
            if len(chunks) == 1:
                # Single chunk - direct synthesis
                self.model.tts_to_file(
                    text=chunks[0],
                    speaker=speaker,
                    file_path=output_path,
                    language='en'
                )
            else:
                # Multiple chunks - synthesize and concatenate
                self._synthesize_chunks(chunks, speaker, output_path)
            
            logger.info(f"XTTS synthesis completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"XTTS synthesis failed: {e}")
            raise
    
    def _clean_text_for_tts(self, text):
        """Clean text to improve TTS quality."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common abbreviations
        text = re.sub(r'\bDr\.', 'Doctor', text)
        text = re.sub(r'\bMr\.', 'Mister', text)
        text = re.sub(r'\bMrs\.', 'Missus', text)
        text = re.sub(r'\bMs\.', 'Miss', text)
        text = re.sub(r'\bProf\.', 'Professor', text)
        
        # Handle numbers and dates better
        text = re.sub(r'\b(\d+)st\b', r'\1 first', text)
        text = re.sub(r'\b(\d+)nd\b', r'\1 second', text)
        text = re.sub(r'\b(\d+)rd\b', r'\1 third', text)
        text = re.sub(r'\b(\d+)th\b', r'\1 th', text)
        
        # Remove or replace problematic characters
        text = re.sub(r'[^\w\s.,!?;:()"\'-]', ' ', text)
        
        return text
    
    def _split_text_into_chunks(self, text, max_chunk_size=500):
        """Split text into manageable chunks for TTS."""
        # Split by sentences first
        sentences = re.split(r'[.!?]+\s*', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            # If adding this sentence would exceed max size, start a new chunk
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += (" " + sentence if current_chunk else sentence)
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]  # Fallback to original text
    
    def _synthesize_chunks(self, chunks, speaker, output_path):
        """Synthesize multiple chunks and concatenate them."""
        import tempfile
        import wave
        
        temp_files = []
        
        try:
            # Generate audio for each chunk
            for i, chunk in enumerate(chunks):
                temp_file = tempfile.mktemp(suffix=f'_chunk_{i}.wav')
                temp_files.append(temp_file)
                
                self.model.tts_to_file(
                    text=chunk,
                    speaker=speaker,
                    file_path=temp_file,
                    language='en'
                )
            
            # Concatenate all chunks
            self._concatenate_wav_files(temp_files, output_path)
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def _concatenate_wav_files(self, input_files, output_file):
        """Concatenate multiple WAV files into one."""
        import wave
        
        with wave.open(output_file, 'wb') as output_wav:
            first_file = True
            
            for input_file in input_files:
                if not os.path.exists(input_file):
                    continue
                    
                with wave.open(input_file, 'rb') as input_wav:
                    if first_file:
                        # Set parameters from first file
                        output_wav.setparams(input_wav.getparams())
                        first_file = False
                    
                    # Copy audio data
                    frames = input_wav.readframes(input_wav.getnframes())
                    output_wav.writeframes(frames)
    
    def get_voice_info(self, voice_id):
        """Get information about a specific voice."""
        return next((v for v in self.voices if v['id'] == voice_id), None)
    
    def validate_voice_access(self, voice_id, user_tier):
        """Check if voice is available (simplified - all voices available)."""
        return self.get_voice_info(voice_id) is not None
    
    def get_engine_status(self):
        """Get engine status."""
        return {
            'xtts_v2': {
                'available': self.model is not None,
                'device': self.device,
                'voice_count': len(self.voices)
            }
        }

# Global voice engine instance
voice_engine = None

def init_voice_engine():
    """Initialize the global voice engine instance."""
    global voice_engine
    try:
        voice_engine = VoiceEngine()
        return voice_engine
    except Exception as e:
        logger.error(f"Failed to initialize voice engine: {e}")
        raise

def get_voice_engine():
    """Get the global voice engine instance."""
    if voice_engine is None:
        return init_voice_engine()
    return voice_engine