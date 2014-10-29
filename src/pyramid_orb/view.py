import orb
import projex.text

from pyramid.view import view_config

class orb_config(object):
    """
    Wrapper decorator to define meta information for a view class

    :param      section | <str>
                path    | <str>
    """
    def __init__(self, model_name, **settings):
        # pop out custom options
        self.__model_name = model_name
        self.__template_path = settings.pop('template_path', '')
        self.__template_suffix = settings.pop('template_suffix', '.mako')
        self.__permits = settings.pop('permits', {})

        # setup generic view options
        self.__config_defaults = settings

    def __call__(self, **settings):
        new_settings = {}
        new_settings.update(self.__config_defaults)
        new_settings.update(settings)

        route_name = projex.text.pluralize(projex.text.underscore(self.__model_name))
        filename = new_settings.pop('filename', new_settings.get('route_name', route_name + '.index').replace('.', '/'))
        new_settings.setdefault('route_name', route_name)
        new_settings.setdefault('renderer', self.__template_path + '/' + filename + self.__template_suffix)
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
        return orb.system.model(self.__model_name)

    def lookup_records(self, context, request):
        model = self.model()
        if not model:
            raise StandardError('Invalid model: {0}'.format(self.__model_name))

        id = request.matchdict.get('id', request.params.get('id'))
        if id is not None:
            record = model(id)
            if not record.isRecord():
                raise StandardError('Invalid record: {0}({1})'.format(self.__model_name, id))
            request.record = record
        else:
            request.record = None
        return True
