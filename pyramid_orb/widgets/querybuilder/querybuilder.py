from ..base import Widget

import projex.text


class QueryBuilder(Widget):
    def __init__(self, request, table, **options):
        templates = options.get('templates', {})
        templates.setdefault('html', 'pyramid_orb:widgets/querybuilder/templates/querybuilder.html.mako')
        templates.setdefault('javascript', 'pyramid_orb:widgets/querybuilder/templates/querybuilder.js.mako')
        options['templates'] = templates

        options.setdefault('id', projex.text.underscore(table.schema().name()) + '_querybuilder')

        super(QueryBuilder, self).__init__(request, **options)

        self._table = table

    def table(self):
        return self._table