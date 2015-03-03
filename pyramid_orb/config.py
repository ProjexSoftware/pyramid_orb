import projex.text


def add_routes(config, model, base=None):
    if base is None:
        base = projex.text.pluralize(projex.text.underscore(model.schema().name()))

    # create the index route
    config.add_route(base, base + '/')

    # create the CRUD routes for the web
    config.add_route('%s.create' % base, '%s/create/' % base)
    config.add_route('%s.show' % base, '%s/{id:\d+}/' % base)
    config.add_route('%s.edit' % base, '%s/{id:\d+}/edit/' % base)
    config.add_route('%s.remove' % base, '%s/{id:\d+}/remove/' % base)
