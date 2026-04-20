import os

from .gateways import BancoNacionalProcesador


class MockPaymentProcessor:
    def pagar(self, monto: float) -> bool:
        print(f"[DEBUG] Mock Payment: Procesando pago de ${monto} sin cargo real.")
        return True


class PaymentFactory:
    @staticmethod
    def get_processor():
        # La infraestructura se decide por configuracion del entorno.
        provider = os.getenv('PAYMENT_PROVIDER', 'BANCO').strip().upper()

        if provider == 'MOCK':
            return MockPaymentProcessor()

        return BancoNacionalProcesador()
