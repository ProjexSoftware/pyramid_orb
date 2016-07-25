import pytest

def assert_equals(object_a, object_b, columns=None):
    if not columns:
        assert len(object_a) == len(object_b)
        assert set(dict(object_a).keys()) == set(dict(object_b).keys())
        columns = dict(object_a).keys()

    for column in columns:
        assert object_a[column] == object_b[column]

def test_get_user_by_id(db, bob, pyramid_app):
    r = pyramid_app.get('/api/v1/users/{0}'.format(bob.id()))
    assert_equals(r.json, bob, columns=['id', 'username'])
    assert 'password' not in r.json

def test_get_all_users(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users')
    assert len(r.json) == len(schema['User'].all())

def test_get_user_by_username(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users', params='username=bob')
    assert len(r.json) == 1

def test_create_sally(db, schema, pyramid_app):
    r = pyramid_app.post('/api/v1/users', params='username=sally&password=pass123')
    assert r.json['username'] == 'sally'
    assert r.json['id'] is not None

def test_change_sally_to_sarah(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users', params='username=sally')
    s = r.json[0]
    id = s['id']

    r = pyramid_app.put('/api/v1/users/{0}'.format(id), params={'username': 'sarah'})
    assert r.json['id'] == id
    assert r.json['username'] == 'sarah'

    r = pyramid_app.patch('/api/v1/users/{0}'.format(id), params={'username': 'sally'})
    assert r.json['id'] == id
    assert r.json['username'] == 'sally'

def test_delete_sally(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users', params={'username': 'sally'})
    s = r.json[0]
    id = s['id']

    r = pyramid_app.delete('/api/v1/users/{0}'.format(id))
    assert r.json['id'] is None

    r = pyramid_app.get('/api/v1/users/{0}'.format(id), expect_errors=True)
    assert r.status_code == 404
    assert r.json['type'] == 'httpnot_found'

def test_add_group_to_bob(db, schema, bob, admins, pyramid_app):
    r = pyramid_app.post('/api/v1/users/{0}/groups'.format(bob.id()), params={'group_id':admins.id()})
    assert r.json['id'] == admins.id()

def test_expand_bob_groups(db, schema, bob, pyramid_app):
    r = pyramid_app.get('/api/v1/users/{0}'.format(bob.id()), params='expand=groups')
    assert len(r.json['groups']) == 1
    assert len(schema['GroupUser'].all()) == 1

def test_delete_bob_groups(db, schema, bob, admins, pyramid_app):
    r = pyramid_app.delete('/api/v1/users/{0}/groups/{1}'.format(bob.id(), admins.id()))
    assert r.json == 1

    assert len(schema['GroupUser'].all()) == 0

def test_get_addresses(db, schema, bob, main_street, pyramid_app):
    r = pyramid_app.get('/api/v1/users/{0}/addresses'.format(bob.id()))
    assert len(r.json) == 1
    assert_equals(r.json[0], main_street)

def test_expand_addresses(db, schema, bob, main_street, pyramid_app):
    r = pyramid_app.get('/api/v1/users/{0}'.format(bob.id()), params='expand=addresses')
    assert len(r.json['addresses']) == 1

    address = r.json['addresses'][0]
    assert_equals(address, main_street)

def test_filter_addresses(db, schema, bob, pyramid_app):
    r = pyramid_app.get('/api/v1/users/{0}/addresses'.format(bob.id()), params={'state': 'USA'})
    assert len(r.json) == 1

def test_create_new_address_through_scoping(db, schema, bob, with_scope, pyramid_app):
    r = pyramid_app.post('/api/v1/addresses', params='street=123 Second St.&city=LA&state=CA&zipcode=54321')
    assert r.json['id'] is not None
    assert r.json['user_id'] == 1

    r = pyramid_app.delete('/api/v1/addresses/{0}'.format(r.json['id']))
    assert r.status_code == 200

def test_create_new_address_through_path(db, schema, bob, pyramid_app):
    r = pyramid_app.post('/api/v1/users/{0}/addresses'.format(bob.id()), params='street=456 Third St.&city=SF&state=CA&zipcode=43215')
    assert r.json['id'] is not None
    assert r.json['user_id'] == 1

    r = pyramid_app.delete('/api/v1/addresses/{0}'.format(r.json['id']))
    assert r.status_code == 200

def test_expand_user_from_address(db, schema, bob, main_street, pyramid_app):
    r = pyramid_app.get('/api/v1/addresses/{0}'.format(main_street.id()), params='expand=user')
    assert_equals(r.json['user'], bob, columns=['id', 'username'])
    assert 'password' not in r.json['user']

def test_get_user_from_address(db, schema, bob, main_street, pyramid_app):
    r = pyramid_app.get('/api/v1/addresses/{0}/user'.format(main_street.id()))
    assert_equals(r.json, bob, columns=['id', 'username'])
    assert 'password' not in r.json

def test_get_address_by_user(db, schema, bob, pyramid_app):
    r = pyramid_app.get('/api/v1/users/{0}/addresses'.format(bob.id()), params={'state': 'USA'})
    assert len(r.json) == 1

def test_get_paged_users(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users', params={'paged': True, 'page': 1, 'pageSize': 100})
    headers = r.headers

    assert len(r.json) == 1
    assert headers['X-Orb-Page'] == '1'
    assert headers['X-Orb-Page-Size'] == '100'
    assert headers['X-Orb-Start'] == '0'
    assert headers['X-Orb-Limit'] == '100'
    assert headers['X-Orb-Page-Count'] == '1'
    assert headers['X-Orb-Total-Count'] == '1'

def test_add_address_to_user(db, schema, bob, pyramid_app):
    import projex.rest
    r = pyramid_app.get('/api/v1/users/{0}/addresses'.format(bob.id()))

    new_record = schema['Address'].create({
        'street': '567 Fourth St.',
        'city': 'Somehere',
        'state': 'CA',
        'zipcode': 123455
    })

    addresses = r.json
    addresses.append(new_record.__json__())

    r = pyramid_app.put_json('/api/v1/users/{0}/addresses'.format(bob.id()), params={'records': addresses})
    assert r.status_code == 200

def test_validate_user_schema(db, schema, pyramid_app):
    import orb
    r = pyramid_app.get('/api/v1/users', params={'returning': 'schema'})
    assert len(r.json['columns']) == len(schema['User'].schema().columns(flags=~orb.Column.Flags.Private))
