from colorama import init, Fore
import pprint
import time

init(autoreset=True)


def perf_timer(argument, debug=True, limit=1):
    def real_decorator(fn):
        def wrapper(*args, **kwargs):
            if debug:
                s = time.perf_counter()
                result = fn(*args, **kwargs)
                ms = (time.perf_counter() - s) * 1000
                if ms > limit:  # 100 > 10
                    s = " ->\t{} - {:.6f} ms ".format(argument, ms)

                    if 0 <= ms < 5:
                        print(Fore.BLUE + 'T1' + s)
                    elif 5 <= ms < 10:
                        print(Fore.GREEN + 'T2' + s)
                    elif 10 <= ms < 50:
                        print(Fore.YELLOW + 'T3' + s)
                    elif 50 <= ms < 100:
                        print(Fore.LIGHTRED_EX + 'T4' + s)
                    else:
                        print(Fore.RED + 'T5' + s)

            else:
                result = fn(*args, **kwargs)

            return result

        return wrapper

    return real_decorator


def attach_timer(cls: type, limit=10) -> list:

    """ Attach performance timer to class

    Find only subclass's or override methods and
    print consumed times of the methods.

    Parameters
    ----------
    cls : class
        Class that we want to add timers.
    limit : int, optional
        Print limit timer (ms).

    Returns
    -------
    method_list : array
        Returning attached methods information.

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> class A(object):
    ...     pass

    >>> attach_timer(A)

    """

    parent = cls.mro()[1]  # get super class
    sub_methods = set(dir(cls)) - set(dir(parent))  # child - parent
    method_list = [
        (getattr(cls, func), func) for func in dir(cls) if
        callable(getattr(cls, func)) and
        (func in sub_methods or
            (hasattr(parent, func) and
             getattr(parent, func) != getattr(cls, func)))
    ]

    # pprint.pprint(method_list)

    for f, n in method_list:
        setattr(cls, n, perf_timer(cls.__name__ + '.' + n, limit=limit)(f))

    return method_list
