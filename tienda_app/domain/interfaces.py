from abc import ABC, abstractmethod

class ProcesadorPago(ABC):
    """
    D: Inversión de Dependencias.
    Definimos el CONTRATO que cualquier banco debe seguir.
    """
    @abstractmethod
    def pagar(self, monto: float) -> bool:
        pass