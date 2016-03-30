import pytest

def test_db_sync(db):
    db.sync()
    assert db.connection() is not None

def test_get_docs(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1', headers={'Accept': 'text/html'})
    assert r.html is not None

def test_get_schema(db, schema, pyramid_app):
    r = pyramid_app.get('/api/v1/', params='returning=schema')
    schema = r.json

    assert 'users' in schema
    assert 'groups' in schema
    assert 'group_users' not in schema