import inspect
import traceback

def withcallerenv(f):
    def wrapper(*args, **kwargs):
        callerenv = inspect.currentframe().f_back.f_locals
        return f(*args, **kwargs, callerenv=callerenv)
    return wrapper



def print_caller():
    # 获取当前调用者的信息
    caller_frame = inspect.stack()[1]
    caller_info = inspect.getframeinfo(caller_frame[0])
    caller_file = caller_info.filename
    caller_line = caller_info.lineno
    caller_function = caller_frame[3]

    # 获取调用栈的文本表示
    traceback_str = traceback.format_stack()
    #print(inspect.stack())
    callerenv = inspect.currentframe().f_back.f_locals
    #print(callerenv)
    print(f"{caller_function} was called from {caller_file} at line {caller_line}")
    return callerenv
    #print("Traceback:\n" )
    #print(traceback_str)

#def outer_function():
#    print_caller()

# 调用outer_function，它会调用print_caller
#outer_function()
