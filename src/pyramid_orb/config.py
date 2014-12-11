import projex.text

def add_routes(config, model, base=None, api=None):
    if base is None:
        base = projex.text.pluralize(projex.text.underscore(model.schema().name()))

    # create the index route
    config.add_route(base, base)

    # create the CRUD routes for the web
    config.add_route('%s.create' % base, '%s/create' % base)
    config.add_route('%s.show' % base, '%s/{id:\d+}' % base)
    config.add_route('%s.edit' % base, '%s/{id:\d+}/edit' % base)
    config.add_route('%s.remove' % base, '%s/{id:\d+}/remove' % base)

    # create RESTFUL CRUD routes
    config.add_route('%s.rest.select' % base, '%s.json' % base, request_method='GET')
    config.add_route('%s.rest.insert' % base, '%s.json' % base, request_method='POST')
    config.add_route('%s.rest.get' % base, '%s/{id:\d+}.json' % base, request_method='GET')
    config.add_route('%s.rest.update' % base, '%s/{id:\d+}.json' % base, request_method='PUT')
    config.add_route('%s.rest.delete' % base, '%s/{id:\d+}.json' % base, request_method='DELETE')

    # create additional methods
    api = api or {}
    for method, request_method in api.items():
        config.add_route('{0}.api.{1}'.format(base, method),
                         '{0}/api/{1}'.format(base, method),
                         request_method=request_method)