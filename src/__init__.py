"""
Transcritor Forense de Áudio - Pacote Principal
Ferramenta para transcrição forense com validade jurídica

Módulo único consolidado: todas as funcionalidades em src/app.py
"""

__version__ = "1.0.0"
__author__ = "Forensic Audio Tools"

from .app import ForensicTranscriber

__all__ = ["ForensicTranscriber"]
