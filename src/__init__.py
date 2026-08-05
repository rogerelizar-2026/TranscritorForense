"""
Transcritor Forense de Áudio - Pacote Principal
Ferramenta para transcrição forense com validade jurídica

Nota: Os módulos diarizer, transcriber e speaker_identifier requerem
instalação das dependências completas (pyannote.audio, whisperx, speechbrain).
O forensic_formatter e speaker_mapper funcionam sem dependências externas.
"""

__version__ = "1.0.0"
__author__ = "Forensic Audio Tools"

# Imports condicionais para permitir uso parcial sem todas as dependências
try:
    from .diarizer import Diarizer
except ImportError:
    Diarizer = None

try:
    from .transcriber import Transcriber
except ImportError:
    Transcriber = None

try:
    from .speaker_identifier import SpeakerIdentifier
except ImportError:
    SpeakerIdentifier = None

from .forensic_formatter import ForensicFormatter
from .speaker_mapper import SpeakerMapper

__all__ = [
    "Diarizer",
    "Transcriber", 
    "SpeakerIdentifier",
    "ForensicFormatter",
    "SpeakerMapper"
]
