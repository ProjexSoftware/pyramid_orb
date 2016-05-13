import orb
import projex.rest

from projex.text import safe_eval

DEFAULT_MAX_LIMIT = 1000


def get_param_values(request):
    if type(request) == dict:
        return request

    try:
        params = dict(request.json_body)
    except ValueError:
        params = dict(request.params)

    # support in-place editing formatted request
    if 'pk' in params:
        pk = params.pop('pk')
        editable_name = params.pop('name')
        editable_value = params.pop('value')
        params[editable_name] = editable_value

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
    context = param_values.pop('orb_context', {})
    if isinstance(context, (unicode, str)):
        context = projex.rest.unjsonify(context)

    has_limit = 'limit' in context or 'limit' in param_values

    context = orb.Context(**context)

    # build up context information from the request params
    used = set()
    query_context = {}
    for key in orb.Context.Defaults:
        if key in param_values:
            used.add(key)
            query_context[key] = param_values.get(key)

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

    param_values = {k: v for k, v in param_values.items() if k not in used}

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

    if not has_limit and context.returning == 'records':
        context.limit = DEFAULT_MAX_LIMIT

    return values, context
