import functools
import line_profiler


def line_profile():
    """
    Decorator for line profiling any callable.

    @line_profile()
    def search(request):
        ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = line_profiler.LineProfiler()
            profiler.add_function(func)
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.print_stats()

            return result

        return wrapper

    return decorator