import logging
import pytest

from pyramid_orb import action

logging.basicConfig()


def test_get_run_record(db, bob, pyramid_app):
    r = pyramid_app.get('/api/v1/users/{0}?action=run'.format(bob.id()))
    assert r.body == '"user run record"'


def test_get_run_model(db, pyramid_app):
    r = pyramid_app.get('/api/v1/users?action=run')
    assert r.body == '"user run model"'


def test_post_exec_model(db, pyramid_app):
    r = pyramid_app.post_json('/api/v1/users?action=exec',
                              {'username': 'sally'})
    assert r.body == '"user exec post model"'


def test_delete_run_record(db, bob, pyramid_app):
    r = pyramid_app.delete('/api/v1/users/{0}?action=run'.format(bob.id()))
    assert r.body == '"user run delete record"'


def test_put_run_record(db, bob, pyramid_app):
    r = pyramid_app.put('/api/v1/users/{0}?action=run'.format(bob.id()))
    assert r.body == '"user run put record"'


def test_patch_run_record(db, bob, pyramid_app):
    r = pyramid_app.patch('/api/v1/users/{0}?action=run'.format(bob.id()))
    assert r.body == '"user run patch record"'


def test_is_model_action():

    class Foo(object):

        @classmethod
        def bar(cls):
            pass

        def baz(self):
            pass

    assert action.is_model_action(Foo.bar, Foo)

    foo = Foo()
    assert not action.is_model_action(foo.baz, Foo)


def test_has_action():

    def bar():
        pass

    bar.action = action.Action('run', 'get')
    assert action.has_action(bar)

    def foo():
        pass
    foo.action = object()
    assert not action.has_action(foo)


def test_iter_actions():

    class Foo(object):

        @action.action(name='bar', method='post')
        def run_bar(self):
            pass

        @classmethod
        @action.action(name='baz', method='patch')
        def run_baz(cls):
            pass

    actions = list(action.iter_actions(Foo))
    assert actions == [(action.Action('bar', 'post', False), Foo.run_bar),
                       (action.Action('baz', 'patch', True), Foo.run_baz)]
