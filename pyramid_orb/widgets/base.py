from pyramid.renderers import render


class Widget(object):
    def __init__(self, request, **options):
        self._request = request
        self._templates = options.get('templates') or {'html': '', 'javascript': ''}
        self._configs = options.get('configs') or {'html': '', 'javascript': ''}
        self._id = options.get('id', '')
        self._title = options.get('title', '')

    def config(self, context='html'):
        return self._configs.get(context) or self._configs['html']

    def id(self):
        return self._id

    def request(self):
        return self._request

    def render(self, **options):
        context = options.pop('context', 'html')

        conf = options.get('config') or self.config(context)

        options['widget'] = self
        options['config'] = conf() if callable(conf) else conf

        template = options.get('template') or self.template(context=context)
        return render(template, options, self._request)

    def template(self, context='html'):
        return self._templates.get(context) or self._templates['html']

    def title(self):
        return self._title