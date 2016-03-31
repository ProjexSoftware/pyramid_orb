import pytest

def test_get_invalid_user(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/users/-1', expect_errors=True)
    assert r.json['type'] == 'record_not_found'
    assert r.status_code == 410

def test_invalid_patch_on_root(db, schema, pyramid_app):
    r = pyramid_app.patch('/api/v1/users', expect_errors=True)
    assert r.status_code == 400

def test_cannot_delete_in_bulk(db, schema, bob, pyramid_app):
    r = pyramid_app.delete('/api/v1/addresses?city=Somewhere', expect_errors=True)
    assert r.status_code == 400

    from orb import Query as Q
    schema['Address'].select(where=Q('city') == 'Somewhere').delete()

def test_cannot_patch_a_root(db, schema, pyramid_app):
    r = pyramid_app.patch('/api/v1/users', expect_errors=True)
    assert r.status_code == 400

    r = pyramid_app.put('/api/v1/users', expect_errors=True)
    assert r.status_code == 400

def test_cannot_post_to_a_record(db, schema, bob, pyramid_app):
    r = pyramid_app.post('/api/v1/users/{0}'.format(bob.id()), expect_errors=True)
    assert r.status_code == 400

def test_get_invalid_path_from_address(db, schema, bob, main_street, pyramid_app):
    r = pyramid_app.get('/api/v1/addresses/{0}/blah'.format(main_street.id()), expect_errors=True)
    assert r.status_code == 404

def test_group_users_not_exposed(db, pyramid_app):
    r = pyramid_app.get('/api/v1/group_users', expect_errors=True)
    assert r.status_code == 404

def test_cannot_select_non_reference_column(db, schema, bob, pyramid_app):
    r = pyramid_app.get('/api/v1/users/{0}/username'.format(bob.id()), expect_errors=True)
    assert r.status_code == 404