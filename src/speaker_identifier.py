"""
Módulo de Identificação de Falantes - SpeechBrain wrapper
Identifica falantes por comparação com amostras de voz de referência
"""

import torch
import torchaudio
from speechbrain.inference.speaker import EncoderClassifier
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning)


class SpeakerIdentifier:
    """
    Wrapper para SpeechBrain com identificação de falantes por amostras
    
    Utiliza embeddings de voz para comparar segmentos transcritos
    com amostras de referência fornecidas.
    """
    
    def __init__(self, model_name: str = "speechbrain/spkrec-ecapa-voxceleb",
                 device: Optional[str] = None,
                 threshold: float = 0.75):
        """
        Inicializa o modelo de identificação de falantes
        
        Args:
            model_name: Modelo SpeechBrain para extração de embeddings
            device: Dispositivo para inferência ('cuda', 'cpu', ou None para auto)
            threshold: Threshold de similaridade para identificação (0.0 a 1.0)
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.threshold = threshold
        self.classifier = None
        self.reference_embeddings: Dict[str, torch.Tensor] = {}
        
    def load_model(self):
        """Carrega o modelo de extração de embeddings"""
        if self.classifier is None:
            self.classifier = EncoderClassifier.from_hparams(
                source=self.model_name,
                savedir=os.path.join("models", self.model_name.replace("/", "_")),
                run_opts={"device": self.device}
            )
            
    def extract_embedding(self, audio_path: str, start: float = None, 
                         end: float = None) -> Optional[torch.Tensor]:
        """
        Extrai embedding de voz de um segmento de áudio
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            start: Tempo inicial do segmento em segundos (opcional)
            end: Tempo final do segmento em segundos (opcional)
            
        Returns:
            Tensor com embedding do falante ou None se falhar
        """
        if self.classifier is None:
            self.load_model()
            
        try:
            # Carrega áudio
            waveform, sample_rate = torchaudio.load(audio_path)
            
            # Extrai segmento se especificado
            if start is not None and end is not None:
                start_sample = int(start * sample_rate)
                end_sample = int(end * sample_rate)
                waveform = waveform[:, start_sample:end_sample]
                
            # Verifica se há áudio suficiente
            if waveform.shape[1] < sample_rate * 0.5:  # Mínimo 0.5 segundos
                return None
                
            # Extrai embedding
            embedding = self.classifier.encode_batch(waveform)
            
            # Normaliza embedding
            embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
            
            return embedding.squeeze(0)
            
        except Exception as e:
            print(f"Erro ao extrair embedding: {e}")
            return None
    
    def register_reference(self, name: str, audio_path: str) -> bool:
        """
        Registra amostra de referência de um falante
        
        Args:
            name: Nome do falante para identificação
            audio_path: Caminho para arquivo de áudio de referência
            
        Returns:
            True se registrado com sucesso, False caso contrário
        """
        embedding = self.extract_embedding(audio_path)
        if embedding is not None:
            self.reference_embeddings[name] = embedding
            return True
        return False
    
    def identify_speaker(self, embedding: torch.Tensor) -> Tuple[Optional[str], float]:
        """
        Identifica falante comparando com referências registradas
        
        Args:
            embedding: Embedding do segmento a identificar
            
        Returns:
            Tupla (nome_do_falante, score_de_similaridade)
            Retorna (None, max_score) se nenhum falante atingir o threshold
        """
        if not self.reference_embeddings:
            return None, 0.0
            
        # Normaliza embedding de entrada
        embedding = torch.nn.functional.normalize(embedding.unsqueeze(0), p=2, dim=1).squeeze(0)
        
        best_match = None
        best_score = 0.0
        
        for name, ref_embedding in self.reference_embeddings.items():
            # Calcula similaridade de cosseno
            similarity = torch.dot(embedding, ref_embedding)
            score = similarity.item()
            
            if score > best_score:
                best_score = score
                best_match = name
                
        # Verifica se atingiu threshold
        if best_score >= self.threshold:
            return best_match, best_score
        else:
            return None, best_score
    
    def identify_segments(self, segments: List[Dict[str, Any]], 
                         audio_path: str) -> List[Dict[str, Any]]:
        """
        Identifica falantes em segmentos de diarização
        
        Args:
            segments: Lista de segmentos da diarização
            audio_path: Caminho para o arquivo de áudio original
            
        Returns:
            Lista de segmentos com identificação de falantes:
            [
                {
                    "start": float,
                    "end": float,
                    "speaker": str,           # ID original (ex: SPEAKER_00)
                    "identified_as": str,     # Nome identificado (ou None)
                    "confidence": float,      # Score de similaridade
                    "text": str               # Texto transcrito (se disponível)
                },
                ...
            ]
        """
        identified_segments = []
        
        for segment in segments:
            # Extrai embedding do segmento
            embedding = self.extract_embedding(
                audio_path, 
                segment["start"], 
                segment["end"]
            )
            
            result = segment.copy()
            result["identified_as"] = None
            result["confidence"] = 0.0
            
            if embedding is not None:
                identified_name, score = self.identify_speaker(embedding)
                result["identified_as"] = identified_name
                result["confidence"] = score
                
            identified_segments.append(result)
            
        return identified_segments
    
    def get_registered_speakers(self) -> List[str]:
        """Retorna lista de falantes registrados"""
        return list(self.reference_embeddings.keys())
    
    def clear_references(self):
        """Limpa todas as referências registradas"""
        self.reference_embeddings.clear()
