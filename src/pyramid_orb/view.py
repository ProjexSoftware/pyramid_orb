import orb
import projex.text

from pyramid.view import view_config

class orb_view_config(object):
    """
    Wrapper decorator to define meta information for a view class

    :param      section | <str>
                path    | <str>
    """
    def __init__(self, model, **settings):
        # pop out custom options
        self.__model = model
        self.__route_base = settings.get('route_base',
                                         projex.text.pluralize(projex.text.underscore(model.schema().name())))

        self.__template_path = settings.pop('template_path', '')
        self.__template_suffix = settings.pop('template_suffix', '.mako')

        self.__permits = settings.pop('permits', {})

        # setup generic view options
        self.__config_defaults = settings

    def __call__(self, **settings):
        new_settings = {}
        new_settings.update(self.__config_defaults)
        new_settings.update(settings)

        new_settings.setdefault('custom_predicates', [])
        predicates = new_settings['custom_predicates']
        predicates.append(self.lookup_records)
        if 'permit' in new_settings:
            predicates.append(new_settings.pop('permit'))

        permit = self.__permits.get(new_settings.get('request_method', 'GET'))
        if permit:
            predicates.append(permit)

        return view_config(**new_settings)

    def model(self):
        return self.__model

    # predicates
    def lookup_records(self, context, request):
        model = self.model()

        # get the record information
        id = request.matchdict.get('id', request.params.get('id'))
        if id is not None:
            request.record = lambda: model(id)
        else:
            request.record = None

        return True

    # HTTP routes
    def create(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.create')
        settings.setdefault('renderer', self.__template_path + '/create' + self.__template_suffix)

        return self(**settings)

    def edit(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.edit')
        settings.setdefault('renderer', self.__template_path + '/edit' + self.__template_suffix)

        return self(**settings)

    def index(self, **settings):
        settings.setdefault('route_name', self.__route_base)
        settings.setdefault('renderer', self.__template_path + '/index' + self.__template_suffix)

        return self(**settings)

    def remove(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.remove')
        settings.setdefault('renderer', self.__template_path + '/remove' + self.__template_suffix)

        return self(**settings)

    def show(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.show')
        settings.setdefault('renderer', self.__template_path + '/show' + self.__template_suffix)

        return self(**settings)

    # REST routes
    def delete(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.rest.delete')
        settings.setdefault('renderer', 'orb_json')
        settings.setdefault('request_method', 'DELETE')

        return self(**settings)

    def insert(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.rest.insert')
        settings.setdefault('renderer', 'orb_json')
        settings.setdefault('request_method', 'POST')

        return self(**settings)

    def get(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.rest.get')
        settings.setdefault('renderer', 'orb_json')
        settings.setdefault('request_method', 'GET')

        return self(**settings)

    def select(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.rest.select')
        settings.setdefault('renderer', 'orb_json')
        settings.setdefault('request_method', 'GET')

        return self(**settings)

    def update(self, **settings):
        settings.setdefault('route_name', self.__route_base + '.rest.update')
        settings.setdefault('renderer', 'orb_json')
        settings.setdefault('request_method', 'PUT')

        return self(**settings)


