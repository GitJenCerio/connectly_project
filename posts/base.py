from rest_framework.views import APIView
from singletons.logger_singleton import LoggerSingleton 

class BaseLoggedAPIView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = LoggerSingleton().get_logger()