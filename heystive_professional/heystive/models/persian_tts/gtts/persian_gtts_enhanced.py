#!/usr/bin/env python3
'''
Enhanced Persian gTTS Configuration
Optimized Google Text-to-Speech for Persian language
'''

import gtts
from gtts.lang import tts_langs
import tempfile
import os
from pathlib import Path

class PersianGTTS:
    '''Enhanced Persian TTS using Google Text-to-Speech'''
    
    def __init__(self):
        self.supported_langs = self._get_persian_languages()
        self.default_lang = 'fa'  # Persian
        
    def _get_persian_languages(self):
        '''Get available Persian languages in gTTS'''
        try:
            all_langs = tts_langs()
            persian_langs = {}
            
            # Look for Persian/Farsi languages
            for code, name in all_langs.items():
                name_lower = name.lower()
                if any(term in name_lower for term in ['persian', 'farsi', 'fa']):
                    persian_langs[code] = name
            
            # Add known Persian codes
            known_persian = {'fa': 'Persian (Farsi)'}
            persian_langs.update(known_persian)
            
            return persian_langs
            
        except Exception as e:
            print(f"Warning: Could not fetch language list: {e}")
            return {'fa': 'Persian (Farsi)'}
    
    def synthesize(self, text, lang='fa', slow=False, output_file=None):
        '''Synthesize Persian text to speech'''
        try:
            # Use specified language or fallback
            if lang not in self.supported_langs:
                print(f"Warning: Language '{lang}' not supported, using 'fa'")
                lang = 'fa'
            
            # Create TTS object
            tts = gtts.gTTS(text=text, lang=lang, slow=slow)
            
            # Save to file
            if output_file:
                tts.save(output_file)
                return output_file
            else:
                # Use temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    tts.save(tmp_file.name)
                    return tmp_file.name
                    
        except Exception as e:
            print(f"TTS synthesis failed: {e}")
            return None
    
    def get_supported_languages(self):
        '''Get list of supported Persian languages'''
        return self.supported_langs
    
    def test_synthesis(self):
        '''Test Persian TTS synthesis'''
        test_text = "سلام! این یک تست سیستم تولید گفتار فارسی است."
        print(f"Testing synthesis with text: {test_text}")
        
        result = self.synthesize(test_text)
        if result and os.path.exists(result):
            print(f"✅ Test successful: {result}")
            return True
        else:
            print("❌ Test failed")
            return False

# Global instance
persian_tts = PersianGTTS()

def get_persian_gtts():
    '''Get the global Persian gTTS instance'''
    return persian_tts

if __name__ == "__main__":
    print("Persian gTTS Configuration Test")
    print("=" * 40)
    
    tts = get_persian_gtts()
    print(f"Supported languages: {tts.get_supported_languages()}")
    tts.test_synthesis()
