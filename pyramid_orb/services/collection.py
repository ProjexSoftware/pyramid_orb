import orb

from pyramid.httpexceptions import HTTPForbidden
from pyramid_orb.utils import get_context
from .orbservice import OrbService


class CollectionService(OrbService):
    def __init__(self, request, collection, parent=None, name=None):
        super(CollectionService, self).__init__(request=request, parent=parent, name=name)

        self.model = collection.model()
        self.collection = collection

    def __getitem__(self, key):
        # look for a view
        view_collection = self.collection.view(key)
        if view_collection is not None:
            return CollectionService(self.request, view_collection, parent=self)

        # look for a record
        else:
            try:
                record_id = int(key)
            except ValueError:
                record_id = key

            from .model import ModelService
            return ModelService(self.request,
                                self.model,
                                record_id=record_id,
                                parent=self,
                                from_collection=self.collection)

    def get(self):
        values, context = get_context(self.request, model=self.model)
        if values:
            where = orb.Query.build(values)
            context.where = where & context.where
        return self.collection.refine(context=context)

    def put(self):
        values, context = get_context(self.request, model=self.model)
        return self.collection.update(values, context=context)

    def post(self):
        values, context = get_context(self.request, model=self.model)
        return self.collection.create(values, context=context)

    def permission(self):
        method = self.request.method.lower()
        auth = getattr(self.model, '__auth__', None)
        if callable(auth):
            return auth(self.request)
        elif isinstance(auth, dict):
            try:
                method_auth = auth[method]
            except KeyError:
                raise HTTPForbidden()
            else:
                if callable(method_auth):
                    return method_auth(self.request)
                else:
                    return method_auth
        elif isinstance(auth, (list, tuple, set)):
            return method in auth
        else:
            return auth
