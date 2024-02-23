import inspect
def withcaller(f):
    '''
    调用时提供调用者
    :param f: 形如def func(caller, ...)的方法，_caller为调用该函数的类，如果在脚本中调用则_caller为脚本路径
    '''
    def wrapper(*args, **kwargs):
        callerenv = inspect.currentframe().f_back.f_locals
        if 'self' in callerenv and isinstance(callerenv['self'], object):
            caller = callerenv['self']
        else:
            caller = inspect.currentframe().f_back.f_code
        return f(caller, *args, **kwargs)
    return wrapper