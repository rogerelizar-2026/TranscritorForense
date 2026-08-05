"""
Testes Unitários - Módulo Diarizer
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.diarizer import Diarizer


class TestDiarizer(unittest.TestCase):
    """Testes para o módulo Diarizer"""
    
    def setUp(self):
        """Configura testes"""
        self.diarizer = Diarizer(huggingface_token="test_token")
    
    def test_init(self):
        """Testa inicialização"""
        self.assertEqual(self.diarizer.huggingface_token, "test_token")
        self.assertIsNone(self.diarizer.pipeline)
    
    def test_get_unique_speakers(self):
        """Testa extração de falantes únicos"""
        segments = [
            {"speaker": "SPEAKER_00", "start": 0, "end": 5},
            {"speaker": "SPEAKER_01", "start": 5, "end": 10},
            {"speaker": "SPEAKER_00", "start": 10, "end": 15},
        ]
        
        speakers = self.diarizer.get_unique_speakers(segments)
        self.assertEqual(speakers, ["SPEAKER_00", "SPEAKER_01"])
    
    def test_get_speaker_segments(self):
        """Testa filtragem por falante"""
        segments = [
            {"speaker": "SPEAKER_00", "start": 0, "end": 5},
            {"speaker": "SPEAKER_01", "start": 5, "end": 10},
            {"speaker": "SPEAKER_00", "start": 10, "end": 15},
        ]
        
        speaker_00_segs = self.diarizer.get_speaker_segments(segments, "SPEAKER_00")
        self.assertEqual(len(speaker_00_segs), 2)
        self.assertTrue(all(s["speaker"] == "SPEAKER_00" for s in speaker_00_segs))
    
    def test_merge_overlapping_segments(self):
        """Testa mesclagem de segmentos sobrepostos"""
        segments = [
            {"speaker": "SPEAKER_00", "start": 0, "end": 5},
            {"speaker": "SPEAKER_00", "start": 4.9, "end": 8},  # Sobreposição
            {"speaker": "SPEAKER_01", "start": 8, "end": 12},
        ]
        
        merged = self.diarizer.merge_overlapping_segments(segments, tolerance=0.5)
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]["end"], 8)  # Segmentos mesclados


if __name__ == "__main__":
    unittest.main()
