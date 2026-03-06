from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    """
    Wrap all API responses in a consistent JSON envelope.
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Defensive: renderer_context may be None
        response = renderer_context.get('response') if renderer_context else None
        status_code = getattr(response, 'status_code', 200)

        success = 200 <= status_code < 300

        # Allow custom message override
        message = None
        if renderer_context and 'message' in renderer_context:
            message = renderer_context['message']

        envelope = {
            "status": "success" if success else "error",
            "code": status_code,
            "data": data if success else None,
            "message": message or ("Operation completed" if success else "An error occurred"),
            "errors": None if success else data,
        }

        return super().render(envelope, accepted_media_type, renderer_context)
