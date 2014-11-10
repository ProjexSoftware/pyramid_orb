import projex.rest
from pyramid.renderers import JSON

class ORB_JSON(JSON):
    def __init__(self, serializer=projex.rest.jsonify, adapters=(), **kw):
        serializer=projex.rest.jsonify
        super(ORB_JSON, self).__init__(serializer=serializer, adapters=adapters, **kw)

orb_json_renderer_factory = ORB_JSON()