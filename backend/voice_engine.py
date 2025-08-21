"""Enhanced TTS engine with multiple voice options."""
import os
import tempfile
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
import pyttsx3

logger = logging.getLogger(__name__)

class VoiceEngine:
    """Enhanced TTS service supporting multiple voice engines and tiers."""
    
    def __init__(self):
        self.engines = {}
        self.voice_catalog = {}
        self.initialize_engines()
        
    def initialize_engines(self):
        """Initialize all available TTS engines."""
        # Always initialize basic pyttsx3 engine
        self._init_basic_engine()
        
        # Try to initialize enhanced engines
        self._init_coqui_engine()
        
        # Build voice catalog
        self._build_voice_catalog()
        
        logger.info(f"Initialized TTS engines: {list(self.engines.keys())}")
    
    def _init_basic_engine(self):
        """Initialize pyttsx3 basic engine."""
        try:
            engine = pyttsx3.init()
            
            # Configure for better audiobook quality
            engine.setProperty('rate', 175)  # Slightly slower for audiobooks
            engine.setProperty('volume', 0.9)
            
            # Try to find the best available voice
            voices = engine.getProperty('voices')
            if voices:
                # Prefer female voices for audiobooks (generally more pleasant)
                female_voices = [v for v in voices if 'female' in v.name.lower() or 'zira' in v.name.lower()]
                if female_voices:
                    engine.setProperty('voice', female_voices[0].id)
                    logger.info(f"Selected voice: {female_voices[0].name}")
            
            self.engines['basic'] = engine
            logger.info("Basic pyttsx3 engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize basic TTS engine: {e}")
            raise
    
    def _init_coqui_engine(self):
        """Initialize Coqui TTS engine if available."""
        try:
            # Try to import TTS
            from TTS.api import TTS
            import torch
            
            # Use CPU for compatibility (can be enhanced for GPU later)
            device = "cpu"
            
            # Initialize XTTS v2 model (professional quality)
            model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            
            self.engines['coqui'] = {
                'model': model,
                'device': device
            }
            
            logger.info("Coqui XTTS engine initialized successfully")
            
        except ImportError:
            logger.info("Coqui TTS not available - install with: pip install TTS torch torchaudio")
        except Exception as e:
            logger.warning(f"Could not initialize Coqui TTS: {e}")
    
    def _build_voice_catalog(self):
        """Build catalog of available voices per subscription tier."""
        
        # Basic voices (free tier) - always available
        basic_voices = []
        if 'basic' in self.engines:
            engine = self.engines['basic']
            voices = engine.getProperty('voices')
            if voices:
                for i, voice in enumerate(voices[:3]):  # Limit to 3 for free tier
                    basic_voices.append({
                        'id': f'basic_{i}',
                        'name': voice.name,
                        'engine': 'basic',
                        'tier_required': 'free',
                        'gender': self._detect_gender(voice.name),
                        'language': 'en',
                        'description': f'System voice: {voice.name}',
                        'sample_rate': '22050',
                        'quality': 'standard'
                    })
        
        # Professional voices (requires professional+ tier)
        premium_voices = []
        if 'coqui' in self.engines:
            coqui_voices = [
                {
                    'id': 'coqui_female_narrator',
                    'name': 'Professional Female Narrator',
                    'engine': 'coqui',
                    'tier_required': 'professional',
                    'gender': 'female',
                    'language': 'en',
                    'description': 'High-quality AI narrator, perfect for audiobooks',
                    'sample_rate': '24000',
                    'quality': 'premium'
                },
                {
                    'id': 'coqui_male_narrator',
                    'name': 'Professional Male Narrator', 
                    'engine': 'coqui',
                    'tier_required': 'professional',
                    'gender': 'male',
                    'language': 'en',
                    'description': 'Warm, authoritative voice ideal for storytelling',
                    'sample_rate': '24000',
                    'quality': 'premium'
                },
                {
                    'id': 'coqui_warm_female',
                    'name': 'Warm Female Voice',
                    'engine': 'coqui', 
                    'tier_required': 'professional',
                    'gender': 'female',
                    'language': 'en',
                    'description': 'Gentle, conversational tone',
                    'sample_rate': '24000',
                    'quality': 'premium'
                },
                {
                    'id': 'coqui_storyteller_male',
                    'name': 'Male Storyteller',
                    'engine': 'coqui',
                    'tier_required': 'professional', 
                    'gender': 'male',
                    'language': 'en',
                    'description': 'Dynamic voice perfect for fiction and narratives',
                    'sample_rate': '24000',
                    'quality': 'premium'
                }
            ]
            premium_voices.extend(coqui_voices)
        
        # Build complete catalog
        self.voice_catalog = {
            'free': basic_voices,
            'professional': basic_voices + premium_voices,
            'enterprise': basic_voices + premium_voices  # Enterprise gets same voices + API access
        }
        
        logger.info(f"Voice catalog built - Free: {len(basic_voices)}, Premium: {len(premium_voices)}")
    
    def _detect_gender(self, voice_name):
        """Detect gender from voice name."""
        female_indicators = ['female', 'zira', 'hazel', 'susan', 'anna', 'emma']
        male_indicators = ['male', 'david', 'mark', 'james', 'ryan']
        
        name_lower = voice_name.lower()
        
        for indicator in female_indicators:
            if indicator in name_lower:
                return 'female'
        
        for indicator in male_indicators:
            if indicator in name_lower:
                return 'male'
        
        return 'neutral'
    
    def get_available_voices(self, user_tier='free'):
        """Get voices available for a specific subscription tier."""
        return self.voice_catalog.get(user_tier, self.voice_catalog['free'])
    
    def synthesize_speech(self, text, voice_id='basic_0', output_path=None, user_tier='free'):
        """Synthesize speech using the specified voice."""
        if not output_path:
            output_path = tempfile.mktemp(suffix='.wav')
        
        # Get voice info
        available_voices = self.get_available_voices(user_tier)
        voice_info = next((v for v in available_voices if v['id'] == voice_id), None)
        
        if not voice_info:
            # Fallback to first available voice
            voice_info = available_voices[0] if available_voices else None
            if not voice_info:
                raise ValueError("No voices available")
            voice_id = voice_info['id']
            logger.warning(f"Voice not found, using fallback: {voice_id}")
        
        # Check if user has access to this voice
        if voice_info['tier_required'] == 'professional' and user_tier == 'free':
            # Downgrade to free voice
            free_voices = self.voice_catalog['free']
            if free_voices:
                voice_info = free_voices[0]
                voice_id = voice_info['id']
                logger.info(f"Downgraded to free voice: {voice_id}")
            else:
                raise ValueError("No free voices available")
        
        # Synthesize based on engine
        engine_type = voice_info['engine']
        
        if engine_type == 'basic':
            return self._synthesize_basic(text, voice_id, output_path)
        elif engine_type == 'coqui':
            return self._synthesize_coqui(text, voice_id, output_path)
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
    
    def _synthesize_basic(self, text, voice_id, output_path):
        """Synthesize using pyttsx3."""
        try:
            engine = self.engines['basic']
            
            # Set specific voice if requested
            if voice_id.startswith('basic_'):
                voice_index = int(voice_id.split('_')[1])
                voices = engine.getProperty('voices')
                if voices and voice_index < len(voices):
                    engine.setProperty('voice', voices[voice_index].id)
            
            # Generate speech
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            logger.info(f"Basic TTS synthesis completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Basic TTS synthesis failed: {e}")
            raise
    
    def _synthesize_coqui(self, text, voice_id, output_path):
        """Synthesize using Coqui XTTS."""
        try:
            coqui_engine = self.engines['coqui']
            model = coqui_engine['model']
            
            # Map voice IDs to speaker configurations
            speaker_mapping = {
                'coqui_female_narrator': 'Claribel Dervla',
                'coqui_male_narrator': 'Daisy Studious', 
                'coqui_warm_female': 'Gitta Nikolina',
                'coqui_storyteller_male': 'Abrahan Mack'
            }
            
            speaker = speaker_mapping.get(voice_id, 'Claribel Dervla')
            
            # Generate speech with XTTS
            model.tts_to_file(
                text=text,
                speaker=speaker,
                file_path=output_path,
                language='en'
            )
            
            logger.info(f"Coqui XTTS synthesis completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Coqui TTS synthesis failed: {e}")
            # Fallback to basic engine
            logger.info("Falling back to basic TTS engine")
            return self._synthesize_basic(text, 'basic_0', output_path)
    
    def get_voice_info(self, voice_id, user_tier='free'):
        """Get detailed information about a specific voice."""
        available_voices = self.get_available_voices(user_tier)
        return next((v for v in available_voices if v['id'] == voice_id), None)
    
    def validate_voice_access(self, voice_id, user_tier):
        """Check if user has access to specified voice."""
        voice_info = self.get_voice_info(voice_id, user_tier)
        if not voice_info:
            return False
            
        tier_hierarchy = {'free': 0, 'professional': 1, 'enterprise': 2}
        required_level = tier_hierarchy.get(voice_info['tier_required'], 999)
        user_level = tier_hierarchy.get(user_tier, 0)
        
        return user_level >= required_level
    
    def get_engine_status(self):
        """Get status of all TTS engines."""
        status = {}
        for engine_name in self.engines:
            status[engine_name] = {
                'available': True,
                'voice_count': len([v for v in self.voice_catalog.get('enterprise', []) if v['engine'] == engine_name])
            }
        return status

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