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


def get_context(request, model=None, params=None):
    if params is None:
        params = collect_params(request)

    # generate a simple query object
    if model:
        q_build = {col: params.pop(col) for col in params.keys() if model.schema().column(col)}
    else:
        q_build = None


    context_options = {
        'inflated': params.pop('inflated', 'True') == 'True',
        'locale': params.pop('locale', None),
        'timezone': params.pop('timezone', None),
        'columns': params.pop('columns').split(',') if 'columns' in params else None,
        'where': Q.build(q_build) if q_build else None,
        'order': params.pop('order', params.pop('orderBy', None)) or None,
        'expand': params.pop('expand').split(',') if 'expand' in params else None,
        'returning': params.pop('returning', None),
        'start': int(params.pop('start', 0)) or None,
        'limit': int(params.pop('limit', 0)) or None,
        'page': int(params.pop('page', 0)) or None,
        'pageSize': int(params.pop('pageSize', 0)) or None
    }

    # extract JSON lookup commands (using the orb javascript library for frontend querying)
    lookup = params.pop('lookup', None)
    if lookup:
        context_options.update(lookup)

    return orb.Context(**context_options)


def collect_query_info(model, request):
    """
    Processes the inputted request object for search terms and parameters.

    :param      request | <pyramid.request.Request>

    :return     (<orb.Context>, <str> search terms, <dict> original options)
    """
    params = collect_params(request)

    # returns the lookup, database options, search terms and original options
    output = {
        'terms': params.pop('terms', ''),
        'context': get_context(request, model=model, params=params)
    }
    output.update(params)
    return output