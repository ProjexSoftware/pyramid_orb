from ..base import Widget

import projex.text


class DataGrid(Widget):
    def __init__(self, request, table, **options):
        options.setdefault('id', '{0}_table'.format(projex.text.underscore(table.schema().name())))

        templates = options.get('templates') or {}
        templates.setdefault('html', 'pyramid_orb:widgets/datagrid/templates/datagrid.html.mako')
        templates.setdefault('javascript', 'pyramid_orb:widgets/datagrid/templates/datagrid.js.mako')
        options['templates'] = templates

        super(DataGrid, self).__init__(request, **options)

        schema = table.schema()
        self._table = table
        self._schema = table.schema()
        self._columns = [schema.column(col) for col in options.get('columns', schema.columns())]
        self._datasource = options.get('datasource', '')

    def columns(self):
        return self._columns

    def datasource(self):
        return self._datasource

    def setDatasource(self, datasource):
        self._datasource = datasource

    def setColumns(self, columns):
        self._columns = columns

    def schema(self):
        return self._schema

