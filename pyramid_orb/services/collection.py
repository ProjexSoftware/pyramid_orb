from .restful import RestfulService
from pyramid_orb.utils import collect_params, collect_query_info, get_context


class CollectionService(RestfulService):
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
        info = collect_query_info(self.model, self.request)
        return self.collection.refine(**info)

    def put(self):
        try:
            values = self.request.json_body
            if type(values) == list:
                values = {'records': values}
        except StandardError:
            values = collect_params(self.request)

        return self.collection.update(values)

    def post(self):
        values = collect_params(self.request)
        context = get_context(self.request)
        return self.collection.create(values, context=context)

