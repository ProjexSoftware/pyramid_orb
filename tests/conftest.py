import pytest


@pytest.fixture()
def logged_out(authenticated, pyramid_config):
    from pyramid.testing import DummySecurityPolicy

    class CustomDummySecurityPolicy(DummySecurityPolicy):
        def permits(self, context, principals, permission):
            return permission in principals

    policy = CustomDummySecurityPolicy()

    pyramid_config.set_authentication_policy(policy)
    pyramid_config.set_authorization_policy(policy)

    return policy

@pytest.fixture()
def logged_in(logged_out):
    logged_out.userid = 1
    return logged_out

@pytest.fixture()
def schema():
    import orb

    class User(orb.Table):
        __resource__ = True

        id = orb.IdColumn()
        username = orb.StringColumn(flags={'Required'})
        password = orb.StringColumn(flags={'Required', 'Private'})

        groups = orb.Pipe(through_path='GroupUser.user.group')
        addresses = orb.ReverseLookup(from_column='Address.user')

        byUsername = orb.Index(columns=['username'], flags={'Unique'})

    class Address(orb.Table):
        __resource__ = True

        id = orb.IdColumn()
        user = orb.ReferenceColumn(reference='User')
        street = orb.StringColumn(flags={'Required'})
        city = orb.StringColumn(flags={'Required'})
        state = orb.StringColumn(flags={'Required'})
        zipcode = orb.IntegerColumn()

        def onInit(self, event):
            context = self.context()
            self.set('user', context.scope.get('user'))

    class Group(orb.Table):
        __resource__ = True

        id = orb.IdColumn()
        name = orb.StringColumn(flags={'Required'})

        users = orb.Pipe(through_path='GroupUser.group.user')

        byName = orb.Index(columns=['name'], flags={'Unique'})

    class GroupUser(orb.Table):
        id = orb.IdColumn()
        group = orb.ReferenceColumn(reference='Group')
        user = orb.ReferenceColumn(reference='User')

    return {'Group': Group, 'User': User, 'GroupUser': GroupUser, 'Address': Address}

@pytest.fixture()
def api(pyramid_config, schema):
    import pyramid_orb
    pyramid_config.include('pyramid_orb')

    api = pyramid_config.registry.rest_api
    pyramid_orb.register(pyramid_config)

    return api

@pytest.fixture()
def db(api, schema):
    import orb

    db = orb.system.database('testing')
    db.activate()

    return db

@pytest.fixture()
def main_street(db, schema):
    return schema['Address'].ensureExists({
        'user': 1,
        'street': '123 Main St.',
        'city': 'Anywhere',
        'state': 'USA',
        'zipcode': 12345
    })

@pytest.fixture()
def bob(db, schema):
    return schema['User'].ensureExists({'username': 'bob'}, defaults={'password': 'testing'})

@pytest.fixture()
def admins(db, schema):
    return schema['Group'].ensureExists({'name': 'admins'})

@pytest.fixture()
def with_scope(bob, pyramid_config):
    def orb_scope(request):
        return {'user': bob}

    pyramid_config.add_request_method(orb_scope, property=True)