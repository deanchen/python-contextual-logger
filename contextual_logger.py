import threading
import inspect
import time
import socket
import traceback
from functools import wraps

_ROOT = None
_INDEXES = ()
_IP_ADDRESS = socket.gethostbyname(socket.gethostname())

_LOCAL = threading.local()
_INTERNAL_INDEXES = ('_function', '_file', '_ip', '_priority',
                     '_timestamp', '_event')
_WRITE_FN = None

DEBUG = 7
INFO = 6
NOTICE = 5
WARNING = 4
ERROR = 3
CRITICAL = 2
ALERT = 1
EMERGENCY = 0


def configure(writeFn, indexes=None, root=None, force=False):
    global _WRITE_FN
    global _INDEXES
    global _ROOT

    if not force and (_WRITE_FN or _INDEXES or _ROOT):
        raise AttributeError("Module already configured.")

    _WRITE_FN = writeFn
    if indexes:
        _INDEXES = indexes
    if root:
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

            _log(priority, data)
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
    file_parts = filename.split('/')
    try:
        index = file_parts.index(_ROOT) + 1
        return '/'.join(file_parts[index:])
    except ValueError:
        return filename


def _log(priority, data, traceback=None):
    if data is None:
        data = {}
    elif isinstance(data, basestring):
        data = {'_event': data}

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
    return _log(log_level, data, traceback.format_exc())


def emergency(data=None):
    return _log(EMERGENCY, data)


def alert(data=None):
    return _log(ALERT, data)


def critical(data=None):
    return _log(CRITICAL, data)


def error(data=None):
    return _log(ERROR, data)


def warning(data=None):
    return _log(WARNING, data)


def notice(data=None):
    return _log(NOTICE, data)


def info(data=None):
    return _log(INFO, data)


def debug(data=None):
    return _log(DEBUG, data)
