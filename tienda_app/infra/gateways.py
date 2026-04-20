import datetime
from pathlib import Path

from ..domain.interfaces import ProcesadorPago

class BancoNacionalProcesador(ProcesadorPago):
    """
    Implementación concreta de la infraestructura.
    Simula un banco local escribiendo en un log.
    """
    def pagar(self, monto: float) -> bool:
        # Simulamos una operación de red o persistencia externa
        archivo_log = Path(__file__).resolve().parents[2] / "pagos_locales_Samuel_Arango_Echeverri.log"

        with archivo_log.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] BANCO NACIONAL - Cobro procesado: ${monto}\n")
        return True