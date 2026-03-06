import time
import random
import logging
from rest_framework.views import APIView, Response
from rest_framework.renderers import JSONRenderer

from rest_framework import status
logger = logging.getLogger(__name__)


# Mock service endpoint
class MockValidationService(APIView):
    permission_classes = []
    renderer_classes = [JSONRenderer,]

    def post(self, request):
        payload = request.data.get("payload")
        latency = random.uniform(3, 5)
        time.sleep(latency)

        # Simulate a 20% failure rate
        if random.random() < 0.2:
            logger.warning("Mock Service Fail - Simulating 503")
            # Return a proper JSON response with a failure status
            return Response(
                {"error": "External API Timeout/Unavailable"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        result = {
            "valid": True,
            "provider_ref": f"EXT-{random.randint(1000, 9999)}",
            "latency": latency,
        }
        return Response(result, status=status.HTTP_200_OK)