"""Your Task:
Create a decorator called @monitor that:

1. Takes an argument log_level (either "basic" or "detailed")
2. Times how long the function takes to execute
3. Logs different information based on the log_level:
    - "basic": Just prints function name and execution time
    - "detailed": Prints function name, arguments, return value, and execution time
4. Works with any function (handles arguments properly)
5. Preserves the original function's metadata

Requirements:
- Use time.time() for timing
- Use proper decorator factory structure
- Use functools.wraps
- Handle *args and **kwargs"""

import functools
from time import time


def monitor(log_level):
    if log_level not in ["basic", "detailed"]:
        raise ValueError(
            f"Invalid log_level: {log_level}. Must be 'basic' or detailed'"
        )

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time()
            result = func(*args, **kwargs)
            exec_time = time() - start_time

            if log_level == "basic":
                print(f"{func.__name__} executed in {exec_time:.6f} seconds")
            elif log_level == "detailed":
                print(
                    f"{func.__name__} called with args: {args}, kwargs: {kwargs}, returned: {result}, executed in {exec_time:.6f} seconds"
                )
                return result

            return result

        return wrapper

    return decorator


@monitor("basic")
def add(a, b):
    """Adds two numbers."""
    return a + b


@monitor("detailed")
def multiply(x, y):
    """Multiplies two numbers."""
    return x * y


if __name__ == "__main__":
    add(3, 5)
    multiply(4, 6)
