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

def test_group_users_not_exposed(db, pyramid_app):
    r = pyramid_app.get('/api/v1/group_users', expect_errors=True)
    assert r.status_code == 404

def test_get_all_users(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users')
    assert len(r.json) == len(schema['User'].all())

def test_get_user_by_username(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users', params='username=bob')
    assert len(r.json) == 1

def test_get_invalid_user(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users/-1', expect_errors=True)
    assert r.json['type'] == 'record_not_found'
    assert r.status_code == 410

def test_create_sally(db, schema, pyramid_app):
    r = pyramid_app.post('/api/v1/users', params='username=sally&password=pass123')
    assert r.json['username'] == 'sally'
    assert r.json['id'] is not None

def test_change_sally_to_sarah(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users', params='username=sally')
    s = r.json[0]
    id = s['id']
    r = pyramid_app.put('/api/v1/users/{0}'.format(id), params='username=sarah')
    assert r.json['id'] == id
    assert r.json['username'] == 'sarah'

def test_delete_sarah(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users', params='username=sarah')
    s = r.json[0]
    id = s['id']

    r = pyramid_app.delete('/api/v1/users/{0}'.format(id))
    assert r.json['id'] is None

    r = pyramid_app.get('/api/v1/users/{0}'.format(id), expect_errors=True)
    assert r.status_code == 410
    assert r.json['type'] == 'record_not_found'

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