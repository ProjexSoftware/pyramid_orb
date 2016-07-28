'''
Actions allow callbacks to be run upon an action query.

e.g. POST /networks?action=run
'''
from collections import namedtuple
import inspect

ACTION = 'action'
METHOD = 'method'
MODEL_ACTION = 'model_action'
NAME = 'name'


class Action(object):

    def __init__(self, name, method, model_action=None):
        self.name = str(name)  # Convert from unicode.
        self.method = str(method)  # Convert from unicode.
        self.model_action = model_action

    def __eq__(self, other):
        return self.as_tuple() == other

    def __hash__(self):
        return hash(self.as_tuple())

    def __repr__(self):
        return repr(self.as_tuple())

    def as_tuple(self):
        return (self.name, self.method, self.model_action)


def is_model_action(func, obj):
    return (inspect.ismethod(func) and
            hasattr(func, '__self__') and
            func.__self__ is obj)


def ensure_model_action(func, obj):
    if func.action.model_action is not None:
        return
    func.action.model_action = is_model_action(func, obj)


def has_action(func):
    if not callable(func) or not hasattr(func, ACTION):
        return False
    return (hasattr(func.action, NAME) and
            hasattr(func.action, METHOD))


def iter_actions(obj):
    for key, value in inspect.getmembers(obj):
        if has_action(value):
            # We can't determine if actions are classmethods until the object
            # they're attached to has been fully defined. i.e. we can't run
            # the following line within the action decorator itself.
            # Unfortunately, this is an unavoidable side-effect because
            # Python evaluates decorators on methods before the associated
            # class is fully defined.
            ensure_model_action(value, obj)
            yield value.action, value


def action(name=None, method='get'):
    def action_(func):
        setattr(func, ACTION, Action(name or func.__name__, method))
        return func
    return action_
