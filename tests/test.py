import time
import contextual_logger.logger as logger
from tests import test_helper


def test_set_write_function():
    def write(row):
        return row

    indexes = ('index1', 'index2')
    logger.configure(write, indexes, 'contextual_logger')


def test_log_dict():
    row = logger.debug('event', {'data': 'some_data'})
    assert row['_data']['data'] == 'some_data'


def test_log_string():
    row = logger.debug('event')
    assert row['_event'] == 'event'


def test_log_exception_without_exception():
    row = logger.exception()

    print row
    assert not row['_data'].get('_tb')
    assert row['_priority'] == 3


def test_log_exception():
    dictionary = {}
    row = None
    try:
        dictionary['non-existent key']
    except KeyError:
        row = logger.exception()

    assert 'Traceback' in row['_data']['_tb']
    assert row['_priority'] == 3


def test_decorator():
    def write(row):
        timestamp = '{0:d}'.format(int(time.time() * 1000000))

        row['_timestamp'] = row['_timestamp'][:11]

        expected = {
            '_event': 'function',
            '_file': 'tests/test_helper.py',
            '_priority': logger.INFO,
            '_function': 'decorated_func',
            '_ip': '127.0.0.1',
            '_timestamp': timestamp[:11],
            '_data': {
                '_line': 8,
                '_response': 'response',
                '_args': "(arg1=1, arg2=2)"
            }
        }
        assert sorted(row.items()) == sorted(expected.items())

    logger.configure(write, force=True)
    test_helper.decorated_func(1, arg2=2)

    indexes = ('index1', 'index2')
    logger.configure(lambda x: x, indexes, 'contextual_logger', force=True)


def test_context():
    logger.set_context({'var1': 1})
    row = logger.debug('event', {'data': 'some_data'})
    assert row['_data']['var1'] == 1
    assert row['_data']['data'] == 'some_data'

    logger.clear_context()
    row = logger.debug('event', {'data': 'some_data'})
    assert not row['_data'].get('var1')
    assert row['_data']['data'] == 'some_data'


def test_dynamic_context():
    timestamp = '{0:d}'.format(int(time.time() * 1000000))
    row = test_helper.func(1, arg2=2)
    row['_timestamp'] = row['_timestamp'][:11]
    assert sorted(row.items()) == sorted({
        '_event': 'event',
        '_file': 'tests/test_helper.py',
        '_priority': 7,
        '_function': 'func',
        '_ip': '127.0.0.1',
        '_timestamp': timestamp[:11],
        '_data': {
            '_line': 5,
            '_args': "(arg1=1, arg2=2, arg3='default')",
            'data': 'some_data'
        }
    }.items())


def test_index():
    row = logger.debug('event', {'index1': 1, 'index2': 2, 'data': 'data'})
    assert row['index1'] == 1
    assert row['index2'] == 2
    assert row['_data']['data'] == 'data'


def test_levels():
    row = logger.debug('event', {'data': 'data'})
    assert row['_priority'] == logger.DEBUG
    assert row['_data']['data'] == 'data'

    row = logger.info('event', {'data': 'data'})
    assert row['_priority'] == logger.INFO
    assert row['_data']['data'] == 'data'

    row = logger.notice('event', {'data': 'data'})
    assert row['_priority'] == logger.NOTICE
    assert row['_data']['data'] == 'data'

    row = logger.warning('event', {'data': 'data'})
    assert row['_priority'] == logger.WARNING
    assert row['_data']['data'] == 'data'

    row = logger.error('event', {'data': 'data'})
    assert row['_priority'] == logger.ERROR
    assert row['_data']['data'] == 'data'

    row = logger.critical('event', {'data': 'data'})
    assert row['_priority'] == logger.CRITICAL
    assert row['_data']['data'] == 'data'

    row = logger.alert('event', {'data': 'data'})
    assert row['_priority'] == logger.ALERT
    assert row['_data']['data'] == 'data'

    row = logger.emergency('event', {'data': 'data'})
    assert row['_priority'] == logger.EMERGENCY
    assert row['_data']['data'] == 'data'
