from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')
        status_code = response.status_code
        success = 200 <= status_code < 300
        envelope = {
            "status": "success" if success else "error",
            "code": status_code,
            "data": data if success else None,
            "message": "Operation completed" if success else "An error occurred",
            "errors": data if status_code >= 400 else None,
        }
        return super().render(envelope, accepted_media_type, renderer_context)