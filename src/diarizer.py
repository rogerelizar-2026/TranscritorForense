"""
Módulo de Diarização - pyannote.audio wrapper
Realiza diarização acústica real (quem fala e quando)
"""

import torch
from pyannote.audio import Pipeline
from typing import Optional, List, Dict, Any
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


class Diarizer:
    """
    Wrapper para pyannote.audio com suporte a diarização acústica
    
    A diarização é baseada em características espectrais do áudio,
    não em inferência contextual de LLMs.
    """
    
    def __init__(self, huggingface_token: str, model_name: str = "pyannote/speaker-diarization-3.1"):
        """
        Inicializa o pipeline de diarização
        
        Args:
            huggingface_token: Token de autenticação Hugging Face
            model_name: Nome do modelo pyannote para diarização
        """
        self.huggingface_token = huggingface_token
        self.model_name = model_name
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Carrega o modelo de diarização"""
        if self.pipeline is None:
            self.pipeline = Pipeline.from_pretrained(
                self.model_name,
                use_auth_token=self.huggingface_token
            )
            self.pipeline.to(torch.device(self.device))
            
    def diarize(self, audio_path: str, min_speakers: int = 2, 
                max_speakers: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza diarização do áudio
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            min_speakers: Número mínimo de falantes esperados
            max_speakers: Número máximo de falantes esperados
            
        Returns:
            Lista de segmentos com informações do falante:
            [
                {
                    "start": float,  # Tempo inicial em segundos
                    "end": float,    # Tempo final em segundos
                    "speaker": str,  # ID do falante (ex: SPEAKER_00)
                    "confidence": float  # Confiança da detecção
                },
                ...
            ]
        """
        if self.pipeline is None:
            self.load_model()
            
        # Executa diarização
        diarization = self.pipeline(
            audio_path,
            min_speakers=min_speakers,
            max_speakers=max_speakers
        )
        
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker,
                "confidence": 1.0  # pyannote não fornece confiança por segmento
            })
            
        return segments
    
    def get_speaker_segments(self, segments: List[Dict[str, Any]], 
                            speaker_id: str) -> List[Dict[str, Any]]:
        """
        Filtra segmentos por falante específico
        
        Args:
            segments: Lista de segmentos da diarização
            speaker_id: ID do falante para filtrar
            
        Returns:
            Lista de segmentos apenas do falante especificado
        """
        return [seg for seg in segments if seg["speaker"] == speaker_id]
    
    def get_unique_speakers(self, segments: List[Dict[str, Any]]) -> List[str]:
        """
        Retorna lista única de falantes identificados
        
        Args:
            segments: Lista de segmentos da diarização
            
        Returns:
            Lista de IDs únicos de falantes
        """
        speakers = set(seg["speaker"] for seg in segments)
        return sorted(list(speakers))
    
    def merge_overlapping_segments(self, segments: List[Dict[str, Any]], 
                                   tolerance: float = 0.1) -> List[Dict[str, Any]]:
        """
        Mescla segmentos sobrepostos ou muito próximos
        
        Args:
            segments: Lista de segmentos da diarização
            tolerance: Tolerância em segundos para mesclar segmentos adjacentes
            
        Returns:
            Lista de segmentos mesclados
        """
        if not segments:
            return []
            
        # Ordena por tempo inicial
        sorted_segments = sorted(segments, key=lambda x: x["start"])
        merged = [sorted_segments[0].copy()]
        
        for current in sorted_segments[1:]:
            last = merged[-1]
            
            # Verifica se há sobreposição ou proximidade
            if current["start"] - last["end"] <= tolerance:
                # Mescla segmentos se forem do mesmo falante
                if current["speaker"] == last["speaker"]:
                    last["end"] = max(last["end"], current["end"])
                else:
                    merged.append(current.copy())
            else:
                merged.append(current.copy())
                
        return merged
