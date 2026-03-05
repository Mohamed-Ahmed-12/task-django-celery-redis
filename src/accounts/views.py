from rest_framework.authtoken.views import ObtainAuthToken
from project.utils.render import CustomJSONRenderer
# Create your views here.
class CustomAuthToken(ObtainAuthToken):
    renderer_classes =[ CustomJSONRenderer]