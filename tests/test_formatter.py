"""
Testes Unitários - Módulo ForensicFormatter
"""

import unittest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.forensic_formatter import ForensicFormatter


class TestForensicFormatter(unittest.TestCase):
    """Testes para o módulo ForensicFormatter"""
    
    def setUp(self):
        """Configura testes com diretório temporário"""
        self.temp_dir = tempfile.mkdtemp()
        self.formatter = ForensicFormatter(output_dir=self.temp_dir)
        
        # Cria arquivo de áudio fake para testes
        self.test_audio_path = os.path.join(self.temp_dir, "test.wav")
        with open(self.test_audio_path, "wb") as f:
            f.write(b"fake audio content")
        
        self.test_segments = [
            {
                "speaker": "SPEAKER_00",
                "start": 0.0,
                "end": 5.0,
                "text": "Olá, bom dia!"
            },
            {
                "speaker": "SPEAKER_01",
                "start": 5.0,
                "end": 10.0,
                "text": "Bom dia, como posso ajudar?"
            }
        ]
        
        self.test_speaker_map = {
            "SPEAKER_00": "Cliente",
            "SPEAKER_01": "Atendente"
        }
        
        self.test_mappings = [
            {"speaker_id": "SPEAKER_00", "name": "Cliente", "method": "manual", "confidence": 1.0},
            {"speaker_id": "SPEAKER_01", "name": "Atendente", "method": "manual", "confidence": 1.0}
        ]
    
    def tearDown(self):
        """Limpa diretório temporário"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_format_timestamp(self):
        """Testa formatação de timestamp"""
        self.assertEqual(self.formatter.format_timestamp(0.0), "00:00.000")
        self.assertEqual(self.formatter.format_timestamp(65.5), "01:05.500")
        self.assertEqual(self.formatter.format_timestamp(3661.123), "01:01:01.123")
    
    def test_compute_content_hash(self):
        """Testa cálculo de hash de conteúdo"""
        content = "test content"
        hash1 = self.formatter.compute_content_hash(content)
        hash2 = self.formatter.compute_content_hash(content)
        self.assertEqual(hash1, hash2)  # Mesma entrada = mesmo hash
        
        hash3 = self.formatter.compute_content_hash("different content")
        self.assertNotEqual(hash1, hash3)  # Conteúdo diferente = hash diferente
    
    def test_generate_metadata(self):
        """Testa geração de metadados"""
        metadata = self.formatter.generate_metadata(
            self.test_audio_path,
            self.test_segments,
            self.test_mappings
        )
        
        self.assertIn("audio_file", metadata)
        self.assertIn("audio_hash_sha256", metadata)
        self.assertIn("processing_date", metadata)
        self.assertEqual(metadata["total_segments"], 2)
        self.assertEqual(metadata["speakers_identified"], 2)
    
    def test_format_markdown(self):
        """Testa geração de Markdown"""
        metadata = self.formatter.generate_metadata(
            self.test_audio_path,
            self.test_segments,
            self.test_mappings
        )
        
        md_content = self.formatter.format_markdown(
            self.test_segments,
            metadata,
            self.test_speaker_map
        )
        
        self.assertIn("RELATÓRIO DE TRANSCRIÇÃO FORENSE", md_content)
        self.assertIn("Cliente", md_content)
        self.assertIn("Atendente", md_content)
        self.assertIn("Olá, bom dia!", md_content)
    
    def test_format_txt(self):
        """Testa geração de TXT"""
        metadata = self.formatter.generate_metadata(
            self.test_audio_path,
            self.test_segments,
            self.test_mappings
        )
        
        txt_content = self.formatter.format_txt(
            self.test_segments,
            metadata,
            self.test_speaker_map
        )
        
        self.assertIn("RELATÓRIO DE TRANSCRIÇÃO FORENSE", txt_content)
        self.assertIn("Cliente:", txt_content)
    
    def test_format_html(self):
        """Testa geração de HTML"""
        metadata = self.formatter.generate_metadata(
            self.test_audio_path,
            self.test_segments,
            self.test_mappings
        )
        
        html_content = self.formatter.format_html(
            self.test_segments,
            metadata,
            self.test_speaker_map
        )
        
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("Cliente", html_content)
    
    def test_save_report(self):
        """Testa salvamento de relatório"""
        content = "Test content"
        filepath = self.formatter.save_report(content, "test_report", "txt")
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".txt"))
        
        with open(filepath, "r", encoding="utf-8") as f:
            saved_content = f.read()
        
        self.assertEqual(saved_content, content)
    
    def test_generate_full_report(self):
        """Testa geração de relatório completo"""
        files = self.formatter.generate_full_report(
            self.test_audio_path,
            self.test_segments,
            self.test_speaker_map,
            self.test_mappings,
            formats=["markdown", "txt"]
        )
        
        self.assertIn("markdown", files)
        self.assertIn("txt", files)
        self.assertTrue(os.path.exists(files["markdown"]))
        self.assertTrue(os.path.exists(files["txt"]))


if __name__ == "__main__":
    unittest.main()
