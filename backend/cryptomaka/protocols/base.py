from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional

class Protocol(ABC):
    """
    Base interface for MAKA protocols.
    """
    
    @abstractmethod
    def run_protocol(self) -> Dict[str, Any]:
        """
        Execute the full protocol end-to-end.
        Must return a structured dictionary containing at least:
        - status: "success" or "error"
        - authentication_success: bool
        - session_key_match: bool
        - messages: List of message metadata
        - timings: Dict of timings (registration, auth, key_derivation)
        """
        pass
