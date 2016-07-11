import orb
import projex.rest

from projex.text import safe_eval

DEFAULT_MAX_LIMIT = 1000

def get_payload(request):
    """
    Extracts the request's payload information.  This will check both
    the JSON body and the main body.

    :param request: <pyramid.request.Request>

    :return: <dict>
    """
    # extract the request payload
    try:
        return request.json_body.mixed()
    except ValueError:
        return request.params.mixed()


def get_param_values(request, model=None):
    """
    Converts the request parameters to Python.

    :param request: <pyramid.request.Request> || <dict>

    :return: <dict>
    """
    if type(request) == dict:
        return request

    params = get_payload(request)

    # support in-place editing formatted request
    try:
        del params['pk']
        params[params.pop('name')] = params.pop('value')
    except KeyError:
        pass

    return {
        k.rstrip('[]'): safe_eval(v) if not type(v) == list else [safe_eval(sv) for sv in v]
        for k, v in params.items()
    }


def get_context(request, model=None):
    """
    Extracts ORB context information from the request.

    :param request: <pyramid.request.Request>
    :param model: <orb.Model> || None

    :return: {<str> key: <variant> value} values, <orb.Context>
    """
    # convert request parameters to python
    param_values = get_param_values(request, model=model)

    # extract the full orb context if provided
    context = param_values.pop('orb_context', {})
    if isinstance(context, (unicode, str)):
        context = projex.rest.unjsonify(context)

    # otherwise, extract the limit information
    has_limit = 'limit' in context or 'limit' in param_values

    # create the new orb context
    orb_context = orb.Context(**context)

    # build up context information from the request params
    used = set()
    query_context = {}
    for key in orb.Context.Defaults:
        if key in param_values:
            used.add(key)
            query_context[key] = param_values.get(key)

    # generate a simple query object
    schema_values = {}
    if model:
        # extract match dict items
        for key, value in request.matchdict.items():
            if model.schema().column(key, raise_=False):
                schema_values[key] = value

        # extract payload items
        for key, value in param_values.items():
            schema_object = model.schema().column(key, raise_=False) or model.schema().collector(key)
            if schema_object:
                value = param_values.pop(key)
                if isinstance(schema_object, orb.Collector) and type(value) not in (tuple, list):
                    value = [value]
                schema_values[key] = value

    # generate the base context information
    query_context['scope'] = {
        'request': request
    }

    # include any request specific scoping information
    try:
        query_context['scope'].update(request.orb_scope)
    except AttributeError:
        pass

    orb_context.update(query_context)

    # set the default limit if none is provided
    if not has_limit and orb_context.returning == 'records':
        orb_context.limit = DEFAULT_MAX_LIMIT

    return schema_values, orb_context
