import projex.text
from pyramid_orb.utils import collect_query_info
import orb

class Resource(dict):
    def __init__(self, name, parent):
        self.__name__ = name
        self.__parent__ = parent

class ApiFactory(Resource):
    def __init__(self, request):
        super(ApiFactory, self).__init__('api', None)

        self.request = request

        for model in orb.system.models():
            model_name = projex.text.underscore(model.schema().name())
            resource_name = projex.text.pluralize(model_name)
            self[resource_name] = ModelResource(request, model, self)

class ModelResource(Resource):
    def __init__(self, request, model, parent):
        model_name = projex.text.underscore(model.schema().name())
        resource_name = projex.text.pluralize(model_name)

        super(ModelResource, self).__init__(resource_name, parent)

        self.request = request
        self.model = model

    def __getitem__(self, key):
        # look for a record
        try:
            id = int(key)
        except ValueError:
            try:
                method = getattr(self.model, key, None)
            except AttributeError:
                raise KeyError(key)
            else:
                # use a classmethod
                if getattr(method, '__self__', None) == self.model:
                    return None
                else:
                    raise KeyError(key)
        else:
            return RecordResource(self.request, self.model(id), self)

    def json(self):
        return self.model.select(**collect_query_info(self.request, self.model))

class RecordResource(Resource):
    def __init__(self, request, record, parent):
        super(RecordResource, self).__init__(record.id(), parent)

        self.request = request
        self.record = record

    def __getitem__(self, key):
        try:
            method = getattr(self.record, key)
        except AttributeError:
            raise KeyError(key)

        raise KeyError(key)

    def json(self):
        return self.record

def api_factory(request):
    return ApiFactory(request)