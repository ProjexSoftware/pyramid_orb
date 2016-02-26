import orb
from pyramid_restful.services import RestfulService


class OrbService(RestfulService):
    def process(self):
        output = super(OrbService, self).process()

        # store additional information in the response header for record sets
        if isinstance(output, orb.Collection):
            new_output = output.__json__()

            if self.request.params.get('paged'):
                self.request.response.headers['X-Orb-Page'] = str(output.currentPage())
                self.request.response.headers['X-Orb-Page-Size'] = str(output.pageSize())
                self.request.response.headers['X-Orb-Start'] = str(output.context().start)
                self.request.response.headers['X-Orb-Limit'] = str(output.context().limit)
                self.request.response.headers['X-Orb-Page-Count'] = str(output.pageCount())
                self.request.response.headers['X-Orb-Total-Count'] = str(output.totalCount())

            return new_output
        else:
            return output