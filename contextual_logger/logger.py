from __future__ import print_function
import threading
import inspect
import time
import socket
import traceback
from functools import wraps

_ROOT = ""
_INDEXES = ()
_IP_ADDRESS = socket.gethostbyname(socket.gethostname())

_LOCAL = threading.local()
_INTERNAL_INDEXES = ('_function', '_file', '_ip', '_priority',
                     '_timestamp', '_event')
_WRITE_FN = lambda row: print(row)
_CONFIGURED = False

DEBUG = 7
INFO = 6
NOTICE = 5
WARNING = 4
ERROR = 3
CRITICAL = 2
ALERT = 1
EMERGENCY = 0


def configure(write_fn, indexes=None, root=None, force=False):
    global _CONFIGURED

    global _WRITE_FN
    global _INDEXES
    global _ROOT

    if not force and _CONFIGURED:
        raise AttributeError("Module already configured.")

    _CONFIGURED = True

    if write_fn:
        _WRITE_FN = write_fn
    if indexes:
        _INDEXES = indexes
    if root:
        if root[-1] != '/':
            root += '/'
        _ROOT = root


def set_context(additional_context):
    try:
        _LOCAL.logging_context.update(additional_context)
    except AttributeError:
        _LOCAL.logging_context = additional_context


def clear_context():
    _LOCAL.logging_context = {}


def _get_context():
    try:
        return _LOCAL.logging_context
    except AttributeError:
        _LOCAL.logging_context = {}
        return _LOCAL.logging_context


def log_function(priority=INFO):
    def decorator(fn):

        @wraps(fn)
        def wrapped(*fn_args, **fn_kwargs):
            response = fn(*fn_args, **fn_kwargs)

            fn_name, file_name, line_number, args = \
                _function_data(fn, fn_args, fn_kwargs)
            data = {
                '_function': fn_name,
                '_file': file_name,
                '_line': line_number,
                '_args': args,
                '_response': str(response)

            }

            _log(priority, 'function', data)
            return response

        return wrapped
    return decorator


def _function_data(fn, fn_args, fn_kwargs):
    func_code = fn.func_code
    line_number = func_code.co_firstlineno

    arg_names = func_code.co_varnames
    arg_locals = dict(zip(arg_names, fn_args))
    arg_locals.update(fn_kwargs)

    arg_names = tuple(set(arg_names) & set(arg_locals.keys()))

    args = inspect.formatargvalues(arg_names, None, None, arg_locals)

    return fn.__name__, func_code.co_filename, line_number, args


def _truncate_filename(filename):
    if filename.startswith(_ROOT):
        filename = filename[len(_ROOT):]
    return filename


def _log(priority, event, data, traceback=None):
    global _WRITE_FN

    if data is None:
        data = {}

    data['_event'] = event

    timestamp = '{0:d}'.format(int(time.time() * 1000000))

    # go up 2 frames because of priority wrapper functions
    introspection = inspect.getouterframes(inspect.currentframe())[2]
    frame, filename, line_number, function_name, lines, index = introspection
    args = inspect.formatargvalues(*inspect.getargvalues(frame))

    dynamicContext = {
        '_priority': priority,
        '_timestamp': timestamp,
        '_ip': _IP_ADDRESS,

        '_function': function_name,
        '_file': filename,
        '_line': line_number,
        '_args': args
    }

    if traceback and traceback != 'None\n':
        dynamicContext['_tb'] = traceback

    raw_data = dict(
        dynamicContext.items() + _get_context().items() + data.items())
    row = {}

    keys_to_index = set(_INDEXES + _INTERNAL_INDEXES) & set(raw_data.keys())
    for key in keys_to_index:
        row[key] = raw_data.pop(key)

    row['_data'] = raw_data

    if row.get('_file'):
        row['_file'] = _truncate_filename(row['_file'])

    return _WRITE_FN(row)


def exception(data=None, log_level=3):
    event = 'exception'
    return _log(log_level, event, data, traceback.format_exc())


def emergency(event, data=None):
    return _log(EMERGENCY, event, data)


def alert(event, data=None):
    return _log(ALERT, event, data)


def critical(event, data=None):
    return _log(CRITICAL, event, data)


def error(event, data=None):
    return _log(ERROR, event, data)


def warning(event, data=None):
    return _log(WARNING, event, data)


def notice(event, data=None):
    return _log(NOTICE, event, data)


def info(event, data=None):
    return _log(INFO, event, data)


def debug(event, data=None):
    return _log(DEBUG, event, data)
