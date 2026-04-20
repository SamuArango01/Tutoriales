class CalculadorImpuestos:
    """
    S: Responsabilidad única - Solo calcula impuestos.
    O: Abierto a extensión - Podríamos heredar para diferentes países.
    """
    @staticmethod
    def obtener_total_con_iva(precio_base: float) -> float:
        IVA = 1.19  # Regla de negocio pura
        return float(precio_base) * IVA