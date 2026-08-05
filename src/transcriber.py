"""
Módulo de Transcrição - whisperx wrapper
Realiza transcrição com alinhamento de palavras e timestamps precisos
"""

import torch
import whisperx
from typing import Optional, List, Dict, Any
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


class Transcriber:
    """
    Wrapper para whisperx com suporte a transcrição e alinhamento
    
    O WhisperX fornece:
    - Transcrição precisa baseada em Whisper da OpenAI
    - Alinhamento de palavras em nível fonético
    - Timestamps precisos para cada palavra
    """
    
    def __init__(self, model_name: str = "large-v2", language: str = "pt", 
                 device: Optional[str] = None):
        """
        Inicializa o modelo de transcrição
        
        Args:
            model_name: Modelo Whisper (tiny, base, small, medium, large-v1, large-v2, large-v3)
            language: Código do idioma (ex: 'pt' para português)
            device: Dispositivo para inferência ('cuda', 'cpu', ou None para auto)
        """
        self.model_name = model_name
        self.language = language
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.align_model = None
        
    def load_model(self, compute_type: str = "float16"):
        """
        Carrega o modelo de transcrição
        
        Args:
            compute_type: Tipo de computação ('float16', 'int8', 'int8_float16', 'float32')
        """
        if self.model is None:
            # Ajusta compute_type para CPU
            if self.device == "cpu":
                compute_type = "float32"
                
            self.model = whisperx.load_model(
                self.model_name,
                self.device,
                compute_type=compute_type,
                language=self.language
            )
            
    def load_align_model(self):
        """Carrega o modelo de alinhamento fonético"""
        if self.model is not None and self.align_model is None:
            self.align_model, self.metadata = whisperx.load_align_model(
                language_code=self.language,
                device=self.device
            )
    
    def transcribe(self, audio_path: str, batch_size: int = 16,
                   print_progress: bool = False) -> Dict[str, Any]:
        """
        Transcreve áudio com timestamps precisos
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            batch_size: Tamanho do batch para processamento
            print_progress: Mostra barra de progresso
            
        Returns:
            Dicionário com resultados da transcrição:
            {
                "segments": [...],  # Segmentos com texto e timestamps
                "language": str,    # Idioma detectado
                "text": str         # Texto completo transcrito
            }
        """
        if self.model is None:
            self.load_model()
            
        # Transcrição inicial
        result = self.model.transcribe(
            audio_path,
            batch_size=batch_size,
            print_progress=print_progress
        )
        
        # Detecta idioma se não especificado
        language = result.get("language", self.language)
        
        # Carrega modelo de alinhamento para o idioma detectado
        if language != self.language:
            self.align_model, self.metadata = whisperx.load_align_model(
                language_code=language,
                device=self.device
            )
        elif self.align_model is None:
            self.load_align_model()
        
        # Alinha transcrição com áudio (word-level timestamps)
        result_aligned = whisperx.align(
            result["segments"],
            self.align_model,
            self.metadata,
            audio_path,
            self.device,
            return_char_alignments=False
        )
        
        return {
            "segments": result_aligned["segments"],
            "language": language,
            "text": result.get("text", "")
        }
    
    def get_word_segments(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrai segmentos em nível de palavra
        
        Args:
            result: Resultado da transcrição alinhada
            
        Returns:
            Lista de palavras com timestamps precisos:
            [
                {
                    "word": str,      # Palavra transcrita
                    "start": float,   # Tempo inicial em segundos
                    "end": float,     # Tempo final em segundos
                    "confidence": float  # Confiança da transcrição
                },
                ...
            ]
        """
        words = []
        for segment in result.get("segments", []):
            if "words" in segment:
                for word_info in segment["words"]:
                    words.append({
                        "word": word_info.get("word", ""),
                        "start": word_info.get("start", 0.0),
                        "end": word_info.get("end", 0.0),
                        "confidence": word_info.get("score", 1.0)
                    })
        return words
    
    def format_timestamp(self, seconds: float) -> str:
        """
        Formata segundos em timestamp HH:MM:SS.mmm
        
        Args:
            seconds: Tempo em segundos
            
        Returns:
            String formatada como HH:MM:SS.mmm
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs % 1) * 1000)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{int(secs):02d}.{millis:03d}"
        else:
            return f"{minutes:02d}:{int(secs):02d}.{millis:03d}"
