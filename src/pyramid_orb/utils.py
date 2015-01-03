import ast
import orb

from orb import Query as Q

CONSTANT_EVALS = {
    'true': True,
    'false': False,
    'null': None
}

def safe_eval(value):
    try:
        return CONSTANT_EVALS[value]
    except KeyError:
        try:
            return ast.literal_eval(value)
        except StandardError:
            return value

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

def collect_query_info(model, request):
    """
    Processes the inputed request object for search terms and parameters.

    :param      request | <pyramid.request.Request>

    :return     (<orb.LookupOptions>, <orb.DatabaseOptions>, <str> search terms, <dict> orignal options)
    """
    params = collect_params(request)

    # create the lookup information
    terms = params.pop('terms', '')

    options = {
        'columns': params.pop('columns').split(',') if 'columns' in params else None,
        'limit': int(params.pop('limit')) if 'limit' in params else None,
        'start': int(params.pop('start')) if 'start' in params else None,
        'inflated': params.pop('inflated') == 'True' if 'inflated' in params else True,
        'page': int(params.pop('page', -1)),
        'pageSize': int(params.pop('pageSize', 0)),
        'expand': params.pop('expand').split(',') if 'expand' in params else None,
        'order': params.pop('order', None) or None,
        'locale': params.pop('locale', orb.system.locale())
    }

    # generate a simple query object
    q_build = {col: params[col] for col in params if model.schema().column(col)}
    if q_build:
        options['where'] = Q.build(q_build)

    db_options = orb.DatabaseOptions(**options)
    lookup = orb.LookupOptions(**options)

    # returns the lookup, database options, search terms and original options
    output = {'lookup': lookup, 'options': db_options, 'terms': terms}
    output.update(params)
    return output