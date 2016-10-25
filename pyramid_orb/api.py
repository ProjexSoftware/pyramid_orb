import orb
import projex.text
import projex.rest
import textwrap

from collections import OrderedDict
from pyramid_restful.api import ApiFactory
from pyramid_restful.documentation import Section
from .services import ModelService

MODEL_EXAMPLES = """
# {model} Example

##### API Endpoint

    '{{{{ url }}}}/{dbname}'

##### Python Code

    import requests
    url = '{{{{ url }}}}/{dbname}'
    r = requests.get(url)
    if r.status_code == 200:
        print r.json()
    else:
        raise StandardError(r.json()['error'])


##### Sample Output


```javascript
[
    {object},
    ...
]
```

"""


class OrbApiFactory(ApiFactory):
    def collect_documentation(self, name, service_info):
        service, service_object = service_info

        if issubclass(service, ModelService):
            group_name = getattr(service_object, '__group__', 'Core Resources')
            section_id = service_object.schema().dbname()
            section_name = service_object.schema().name()

            # include the default documentation
            docs = textwrap.dedent(getattr(service_object, '__doc__', '') or '')

            # generate the object documentation
            object_docs = []
            object_docs.append('### The {0} object'.format(section_name))
            object_docs.append('##### Attributes')

            expandable = []
            columns = service_object.schema().columns().values()
            changes = {}
            obj = OrderedDict()
            for column in sorted(columns, key=lambda x: -1 if isinstance(x, orb.IdColumn) else x.name()):
                if column.testFlag(column.Flags.Private):
                    continue

                if isinstance(column, orb.ReferenceColumn):
                    opts = (column.reference(),
                            column.referenceModel().schema().dbname())
                    text = '* __{0}__ : _Reference to [{1} object](#{2})_'
                    text = text.format(column.field(), *opts)
                    expandable.append('* __{0}__ : _[{1} object](#{2})_'.format(column.name(), *opts))
                else:
                    text = '* __{0}__ : _{1}_'.format(column.field(), type(column).__name__.replace('Column', ''))

                object_docs.append(text)
                if column == service_object.schema().idColumn():
                    obj[column.field()] = '1234'
                else:
                    change = column.random()
                    obj[column.field()] = column.random()
                    if obj[column.field()] != change and len(changes) < 3:
                        changes[column.field()] = change

            if expandable:
                object_docs.append('##### References [Expand Required]')
                object_docs.append('\n'.join(expandable))

            collectors = service_object.schema().collectors().values()
            if collectors:
                object_docs.append('##### Collections [Expand Required]')
                for collector in sorted(collectors, key=lambda x: x.name()):
                    if isinstance(collector, orb.Pipe):
                        text = '* __{0}__ : _Collection of [{1} objects](#{2})_'
                        text = text.format(collector.name(),
                                           collector.toModel().schema().name(),
                                           collector.toModel().schema().dbname(),
                                           collector.throughModel().schema().name(),
                                           collector.throughModel().schema().dbname())

                    elif isinstance(collector, orb.ReverseLookup):
                        text = '* __{0}__: _Collection of [{1} objects](#{2})_'
                        text = text.format(collector.name(),
                                           collector.referenceModel().schema().name(),
                                           collector.referenceModel().schema().dbname(),
                                           collector.targetColumn().name())
                    else:
                        continue
                    object_docs.append(text)

            changed_object = obj.copy()
            changed_object.update(changes)

            kwds = {
                'dbname': service_object.schema().dbname(),
                'model': service_object.schema().name(),
                'object': projex.rest.jsonify(obj).replace('\n', '\n    '),
                'changes': projex.rest.jsonify(changes).replace('\n', '\n    '),
                'changed_object': projex.rest.jsonify(changed_object).replace('\n', '\n    ')
            }

            # example_docs = [
            #     '### {0} Endpoint'.format(service_object.schema().name()),
            #     '',
            #     '    '
            # ]
            #
            # example_docs = ['### Query Records', '']
            # example_docs.append('```python')
            #
            # model = service_object()
            # example_docs.append('>>> import requests')
            # example_docs.append('>>> requests.get("{{ url }}/' + service_object.schema().dbname() + '/:id")')
            # example_docs.append(projex.rest.jsonify(model))
            #
            # example_docs.append('```')

            docs += '\n' + '\n'.join(object_docs)

            section = Section(
                id=section_id,
                name=section_name,
                methods=[
                    (docs, MODEL_EXAMPLES.format(**kwds))
                ]
            )
            yield group_name, section
        else:
            for group_name, section in super(OrbApiFactory, self).collect_documentation(name, service_info):
                yield group_name, section

    def process(self, request):
        is_root = bool(not request.traversed)
        is_json = 'application/json' in request.accept
        is_get = request.method.lower() == 'get'
        returning = request.params.get('returning')
        # return the schema information for this API
        if is_root and is_json and is_get and returning == 'schema':
            schemas = [s.__json__() for s in sorted(orb.system.schemas().values(), key=lambda x: x.name()) if getattr(s.model(), '__resource__', False)]
            output = {x['dbname']: x for x in schemas}
            return output

        else:
            return super(OrbApiFactory, self).process(request)

    def register(self, service, name=''):
        """
        Exposes a given service to this API.
        """
        try:
            is_model = issubclass(service, orb.Model)
        except StandardError:
            is_model = False

        # expose an ORB table dynamically as a service
        if is_model:
            self.services[service.schema().dbname()] = (ModelService, service)

        else:
            super(OrbApiFactory, self).register(service, name=name)

