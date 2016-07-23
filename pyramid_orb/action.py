'''
Actions allow callbacks to be run upon an action query.

e.g. POST /networks?action=run
'''
from collections import namedtuple
import inspect

ACTION = 'action'
METHOD = 'method'
NAME = 'name'

Action = namedtuple('Action', [NAME, METHOD])


def has_action(func):
    if not callable(func) or not hasattr(func, ACTION):
        return False
    return (hasattr(func.action, NAME) and
            hasattr(func.action, METHOD))


def iter_actions(instance):
    for key, value in inspect.getmembers(instance):
        if has_action(value):
            yield value.action, value


def action(name=None, method='get'):
    def action_(func):
        setattr(func, ACTION, Action(name or func.__name__, method))
        return func
    return action_
