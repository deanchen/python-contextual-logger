import contextual_logger.logger as logger


def func(arg1, arg2='default', arg3='default'):
    return logger.debug('event', {'data': 'some_data'})


@logger.log_function(logger.INFO)
def decorated_func(arg1, arg2='default', arg3='default'):
    return "response"
