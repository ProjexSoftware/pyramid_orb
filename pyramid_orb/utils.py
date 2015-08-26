import orb

from orb import Query as Q
from projex.text import safe_eval


def collect_params(request):
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


def get_context(request, params=None):
    if params is None:
        params = collect_params(request)

    context_options = {
        'inflated': params.pop('inflated') == 'True' if 'inflated' in params else True,
        'locale': params.pop('locale', None),
        'timezone': params.pop('timezone', None),
        'request': request
    }

    return orb.ContextOptions(**context_options)


def get_lookup(request, model=None, params=None):
    if params is None:
        params = collect_params(request)

    # extract JSON lookup commands (using the orb javascript library for frontend querying)
    lookup = params.pop('lookup', None)
    if lookup:
        return orb.LookupOptions.fromJSON(lookup)
    else:
        # generate a simple query object
        if model:
            q_build = {col: params.pop(col) for col in params.keys() if model.schema().column(col)}
        else:
            q_build = None

        lookup_options = {
            'columns': params.pop('columns').split(',') if 'columns' in params else None,
            'where': Q.build(q_build) if q_build else None,
            'order': params.pop('order', params.pop('orderBy', None)) or None,
            'expand': params.pop('expand').split(',') if 'expand' in params else None,
            'start': int(params.pop('start')) if 'start' in params else None,
            'limit': int(params.pop('limit')) if 'limit' in params else None,
            'returning': params.pop('returning', None),
            'page': int(params.pop('page', -1)),
            'pageSize': int(params.pop('pageSize', 0))
        }

        return orb.LookupOptions(**lookup_options)


def collect_query_info(model, request):
    """
    Processes the inputted request object for search terms and parameters.

    :param      request | <pyramid.request.Request>

    :return     (<orb.LookupOptions>, <orb.ContextOptions>, <str> search terms, <dict> original options)
    """
    params = collect_params(request)

    # returns the lookup, database options, search terms and original options
    output = {
        'terms': params.pop('terms', ''),
        'lookup': get_lookup(request, model=model, params=params),
        'options': get_context(request, params=params)
    }
    output.update(params)
    return output