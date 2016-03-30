import orb

from projex.text import safe_eval


def get_param_values(request):
    if type(request) == dict:
        return request

    try:
        params = dict(request.json_body)
    except ValueError:
        params = dict(request.params)

    try:
        params.setdefault('id', int(request.matchdict['id']))
    except KeyError:
        pass

    def extract(k, v):
        if k.endswith('[]'):
            return [safe_eval(v) for v in request.params.getall(k)]
        else:
            return safe_eval(v)

    return {k.rstrip('[]'): extract(k, v) for k, v in params.items()}


def get_context(request, model=None):
    param_values = get_param_values(request)

    context = orb.Context(**param_values.pop('context', {}))

    # build up context information from the request params
    query_context = {}
    for key in orb.Context.Defaults:
        if key in param_values:
            query_context[key] = param_values.pop(key)

    # generate a simple query object
    values = {}
    if model:
        for key, value in param_values.items():
            col = model.schema().column(key, raise_=False)
            if col:
                values[key] = param_values.pop(key)
            else:
                coll = model.schema().collector(key)
                if coll:
                    values[key] = param_values.pop(key)

    # generate the base context information
    query_context['scope'] = {
        'request': request
    }

    # include any request specific scoping information
    try:
        query_context['scope'].update(request.orb_scope)
    except AttributeError:
        pass

    context.update(query_context)
    return values, context
