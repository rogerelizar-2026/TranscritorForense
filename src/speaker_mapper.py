"""
Módulo de Mapeamento de Falantes
Gerencia mapeamento entre IDs genéricos (SPEAKER_00) e nomes reais
"""

from typing import Dict, Optional, List


class SpeakerMapper:
    """
    Gerencia mapeamento entre IDs de falantes e nomes identificados
    
    Permite associação manual ou automática de falantes detectados
    com nomes reais para documentos forenses.
    """
    
    def __init__(self):
        """Inicializa o mapeador de falantes"""
        self.speaker_map: Dict[str, str] = {}  # speaker_id -> nome
        self.speaker_metadata: Dict[str, Dict] = {}  # speaker_id -> metadados
        
    def map_speaker(self, speaker_id: str, name: str, 
                   confidence: float = 1.0, method: str = "manual") -> None:
        """
        Mapeia um ID de falante para um nome
        
        Args:
            speaker_id: ID do falante (ex: SPEAKER_00)
            name: Nome real do falante
            confidence: Confiança no mapeamento (0.0 a 1.0)
            method: Método de identificação ('manual', 'automatic', 'hybrid')
        """
        self.speaker_map[speaker_id] = name
        self.speaker_metadata[speaker_id] = {
            "confidence": confidence,
            "method": method
        }
        
    def get_name(self, speaker_id: str, default_format: str = "{id}") -> str:
        """
        Obtém nome do falante para um dado ID
        
        Args:
            speaker_id: ID do falante
            default_format: Formato se não houver mapeamento ({id} será substituído)
            
        Returns:
            Nome do falante ou formato padrão se não mapeado
        """
        if speaker_id in self.speaker_map:
            return self.speaker_map[speaker_id]
        return default_format.format(id=speaker_id)
    
    def get_mapping(self, speaker_id: str) -> Optional[Dict]:
        """
        Obtém informações completas de mapeamento para um falante
        
        Args:
            speaker_id: ID do falante
            
        Returns:
            Dicionário com informações de mapeamento ou None se não existir
        """
        if speaker_id not in self.speaker_map:
            return None
            
        return {
            "speaker_id": speaker_id,
            "name": self.speaker_map[speaker_id],
            **self.speaker_metadata.get(speaker_id, {})
        }
    
    def get_all_mappings(self) -> List[Dict]:
        """
        Retorna todos os mapeamentos registrados
        
        Returns:
            Lista de dicionários com informações de mapeamento
        """
        mappings = []
        for speaker_id, name in self.speaker_map.items():
            mappings.append({
                "speaker_id": speaker_id,
                "name": name,
                **self.speaker_metadata.get(speaker_id, {})
            })
        return mappings
    
    def auto_map_from_identification(self, identified_segments: List[Dict]) -> None:
        """
        Cria mapeamento automático baseado em identificação por amostras
        
        Args:
            identified_segments: Segmentos com campo 'identified_as' preenchido
        """
        speaker_votes: Dict[str, Dict[str, float]] = {}
        
        for segment in identified_segments:
            speaker_id = segment.get("speaker", "")
            identified_as = segment.get("identified_as")
            confidence = segment.get("confidence", 0.0)
            
            if identified_as and speaker_id:
                if speaker_id not in speaker_votes:
                    speaker_votes[speaker_id] = {}
                    
                if identified_as not in speaker_votes[speaker_id]:
                    speaker_votes[speaker_id][identified_as] = []
                    
                speaker_votes[speaker_id][identified_as].append(confidence)
        
        # Decide mapeamento por maior média de confiança
        for speaker_id, votes in speaker_votes.items():
            best_name = None
            best_avg = 0.0
            
            for name, scores in votes.items():
                avg_score = sum(scores) / len(scores)
                if avg_score > best_avg:
                    best_avg = avg_score
                    best_name = name
            
            if best_name and best_avg >= 0.5:  # Threshold mínimo
                self.map_speaker(speaker_id, best_name, best_avg, "automatic")
    
    def clear_mappings(self):
        """Limpa todos os mapeamentos"""
        self.speaker_map.clear()
        self.speaker_metadata.clear()
    
    def export_mapping(self) -> Dict:
        """
        Exporta mapeamento como dicionário serializável
        
        Returns:
            Dicionário com mapeamento e metadados
        """
        return {
            "mappings": self.speaker_map.copy(),
            "metadata": self.speaker_metadata.copy()
        }
    
    def import_mapping(self, mapping_data: Dict) -> None:
        """
        Importa mapeamento de dicionário serializado
        
        Args:
            mapping_data: Dicionário com 'mappings' e 'metadata'
        """
        if "mappings" in mapping_data:
            self.speaker_map.update(mapping_data["mappings"])
        if "metadata" in mapping_data:
            self.speaker_metadata.update(mapping_data["metadata"])
