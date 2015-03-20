import projex.text

from pyramid.view import view_config
from .utils import collect_query_info


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

        self.__default_page_size = settings.pop('default_page_size', 0)
        self.__permits = settings.pop('permits', {})

        # setup generic view options
        self.__config_defaults = settings

    def __call__(self, **settings):
        new_settings = {}
        new_settings.update(self.__config_defaults)
        new_settings.update(settings)

        new_settings.setdefault('custom_predicates', [])
        predicates = new_settings['custom_predicates']

        def lookup_records(custom):
            def call(context, request):
                return self.lookup_records(context, request, custom)
            return call

        custom_settings = {
            'default_page_size': new_settings.pop('default_page_size', self.__default_page_size)
        }

        predicates.append(lookup_records(custom_settings))
        if 'permit' in new_settings:
            predicates.append(new_settings.pop('permit'))

        permit = self.__permits.get(new_settings.get('request_method', 'GET'))
        if permit:
            predicates.append(permit)

        return view_config(**new_settings)

    def model(self):
        return self.__model

    # predicates
    def lookup_records(self, context, request, settings):
        model = self.model()

        # record getter
        info = collect_query_info(model, request)
        info['lookup'].pageSize = info['lookup'].pageSize or settings['default_page_size']

        id = int(request.matchdict.get('id') or info.get('id') or 0)

        # grab an individual record from the request
        def get_record(model, id, info):
            def getter():
                return model(id, options=info['options'])
            return getter

        # collect a record set based on the information from the request
        def select_records(model, info):
            def select(**options):
                info['lookup'].update(options)
                info['options'].update(options)
                method = getattr(model, info.get('method', 'select'), model.select)
                return method(**info)
            return select

        request.record = get_record(model, id, info)
        request.records = select_records(model, info)

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
        settings.setdefault('route_name', 'api.{0}.delete'.format(self.__route_base))
        settings.setdefault('renderer', 'json2')
        settings.setdefault('request_method', 'DELETE')

        return self(**settings)

    def delete_many(self, **settings):
        settings.setdefault('route_name', 'api.{0}.delete_many'.format(self.__route_base))
        settings.setdefault('renderer', 'json2')
        settings.setdefault('request_method', 'DELETE')

        return self(**settings)

    def insert(self, **settings):
        settings.setdefault('route_name', 'api.{0}.create'.format(self.__route_base))
        settings.setdefault('renderer', 'json2')
        settings.setdefault('request_method', 'POST')

        return self(**settings)

    def get(self, **settings):
        settings.setdefault('route_name', 'api.{0}.get'.format(self.__route_base))
        settings.setdefault('renderer', 'json2')
        settings.setdefault('request_method', 'GET')

        return self(**settings)

    def select(self, **settings):
        settings.setdefault('route_name', 'api.{0}'.format(self.__route_base))
        settings.setdefault('renderer', 'json2')
        settings.setdefault('request_method', 'GET')

        return self(**settings)

    def update(self, **settings):
        settings.setdefault('route_name', 'api.{0}.update'.format(self.__route_base))
        settings.setdefault('renderer', 'json2')
        settings.setdefault('request_method', 'PUT')

        return self(**settings)

    def update_many(self, **settings):
        settings.setdefault('route_name', 'api.{0}.update_many'.format(self.__route_base))
        settings.setdefault('renderer', 'json2')
        settings.setdefault('request_method', 'PUT')

        return self(**settings)

