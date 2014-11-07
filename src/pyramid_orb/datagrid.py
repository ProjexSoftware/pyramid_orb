import projex.text
from pyramid.renderers import render

class DataGrid(object):
    def __init__(self, request, table, **options):
        schema = table.schema()
        self._request = request
        self._table = table
        self._schema = table.schema()
        self._columns = [schema.column(col) for col in options.get('columns', schema.columns())]
        self._id = options.get('id', projex.text.underscore(table.schema().name()) + '_table')
        self._datasource = options.get('datasource', '')
        self._template = options.get('template', 'pyramid_orb:templates/datagrid/datagrid.html.mako')
        self._jsTemplate = options.get('jsTemplate', 'pyramid_orb:templates/datagrid/datagrid.js.mako')
        self._jsOptions = options.get('jsOptions', '')

    def columns(self):
        return self._columns

    def datasource(self):
        return self._datasource

    def id(self):
        return self._id

    def render(self, **options):
        options['grid'] = self
        return render(options.get('template', self._template), options, self._request)

    def javascript(self, **options):
        options['grid'] = self
        self._jsOptions = options.get('options', self._jsOptions)

        return render(options.get('template', self._jsTemplate), options, self._request)

    def javascriptOptions(self, **options):
        options['grid'] = self
        if callable(self._jsOptions):
            return self._jsOptions()
        elif 'template' in options:
            return render(options.get('template', ''), options, self._request)
        else:
            return self._jsOptions or ''

    def jsOptions(self):
        return self._jsOptions

    def jsTemplate(self):
        return self._jsTemplate

    def setDatasource(self, datasource):
        self._datasource = datasource

    def setColumns(self, columns):
        self._columns = columns

    def schema(self):
        return self._schema

    def setJsOptions(self, options):
        self._jsOptions = options

    def setJsTemplate(self, template):
        self._jsTemplate = template

    def setId(self, id):
        self._id = id

    def setTemplate(self, template):
        self._template = template

    def template(self):
        return self._template