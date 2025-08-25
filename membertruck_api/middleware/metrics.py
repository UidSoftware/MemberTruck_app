# middleware/metrics.py
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('membertruck_app')

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            # Log requisições lentas (> 1 segundo)
            if duration > 1.0:
                logger.warning(f"Requisição lenta: {request.method} {request.path} - {duration:.2f}s")

            # Adicionar header de tempo de resposta
            response['X-Response-Time'] = f"{duration:.3f}s"
            
        return response