import orb
from orb import Query as Q

def collect_params(request):
    try:
        params = dict(request.json_body)
    except ValueError:
        params = dict(request.params)

    try:
        params.setdefault('id', int(request.matchdict['id']))
    except KeyError:
        pass

    return params

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
        'inflated': params.pop('inflated') == 'True' if 'inflated' in params else False,
        'expand': params.pop('expand').split(',') if 'expand' in params else None,
        'order': [k.split(':') for k in params.pop('order').split(',')] if 'order' in params else None,
        'locale': params.pop('locale', orb.system.locale())
    }

    # generate a simple query object
    q_build = {col: params[col] for col in params if model.schema().column(col)}
    if q_build:
        for k, v in q_build.items():
            try:
                q_build[k] = eval(v)
            except StandardError:
                pass

        options['where'] = Q.build(q_build)

    db_options = orb.DatabaseOptions(**options)
    lookup = orb.LookupOptions(**options)

    # returns the lookup, database options, search terms and original options
    return {'lookup': lookup, 'options': db_options, 'terms': terms}