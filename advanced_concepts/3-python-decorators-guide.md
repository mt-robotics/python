# Comprehensive Guide to Python Decorators

## 1. Understanding Decorators: The Fundamentals

### 1.1 What Are Decorators?

Decorators are a powerful and expressive feature in Python that allows you to modify or enhance functions or methods without changing their definition. At their core, decorators are simply functions that take another function as an argument, add some functionality, and return the modified function.

The key concept is that decorators "wrap" a function, modifying its behavior by adding code that executes before and/or after the wrapped function runs.

### 1.2 Basic Decorator Syntax

```python
@decorator_function
def target_function():
    pass
```

This is equivalent to:

```python
def target_function():
    pass

target_function = decorator_function(target_function)
```

The `@decorator_function` syntax is simply syntactic sugar that makes the code more readable.

### 1.3 A Simple Decorator Example

```python
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

# Call the decorated function
say_hello()
```

Output:
```
Something is happening before the function is called.
Hello!
Something is happening after the function is called.
```

## 2. How Decorators Work: Under the Hood

### 2.1 Functions as First-Class Objects

In Python, functions are first-class objects, which means they can be:
- Assigned to variables
- Passed as arguments to other functions
- Returned from other functions
- Stored in data structures

This property enables decorators to work.

### 2.2 Nested Functions

Decorators typically use nested functions (functions defined inside other functions) to modify behavior:

```python
def outer_function(param):
    # This is a closure - it "remembers" the outer function's environment
    def inner_function():
        # Can access param from the outer scope
        print(f"Parameter was: {param}")
    
    return inner_function

# Create a function that remembers the parameter
my_func = outer_function("Hello")

# Call the function later
my_func()  # Prints: Parameter was: Hello
```

### 2.3 Function Decoration Step by Step

When you use a decorator, Python goes through these steps:

1. Define the decorator function
2. Apply the decorator to a target function
3. When the decorated function is called, the wrapper function executes

```python
# Step 1: Define the decorator
def timing_decorator(func):
    import time
    
    def wrapper():
        start_time = time.time()
        func()
        end_time = time.time()
        print(f"Function took {end_time - start_time:.4f} seconds to run")
    
    return wrapper

# Step 2: Apply the decorator
@timing_decorator
def slow_function():
    import time
    time.sleep(1)
    print("Function executed")

# Step 3: Call the decorated function
slow_function()
```

## 3. Decorators with Arguments

### 3.1 Decorating Functions with Arguments

To create decorators that work with functions that take arguments, use `*args` and `**kwargs`:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

print(add(3, 5))  # Correctly passes arguments to the decorated function
```

Output:
```
Before function call
After function call
8
```

### 3.2 Preserving Function Metadata

When you decorate a function, its metadata (like name, docstring, etc.) gets lost. Use `functools.wraps` to preserve it:

```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # Preserves metadata of the decorated function
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper

@my_decorator
def add(a, b):
    """Add two numbers and return the result."""
    return a + b

# Now metadata is preserved
print(add.__name__)  # Outputs: "add" instead of "wrapper"
print(add.__doc__)   # Outputs: "Add two numbers and return the result."
```

### 3.3 Decorators that Take Arguments

You can also create decorators that accept their own arguments:

```python
def repeat(num_times):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_repeat

@repeat(3)
def greet(name):
    print(f"Hello {name}")

greet("World")  # Calls greet("World") 3 times
```

Note the structure: it's a function returning a decorator, which then decorates the target function.

## 4. Practical Decorator Use Cases

### 4.1 Timing Functions

```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds to run")
        return result
    return wrapper

@timer
def slow_function(delay):
    time.sleep(delay)
    return "Function completed"

slow_function(1.5)  # Output: slow_function took 1.5XXX seconds to run
```

### 4.2 Logging

```python
import functools
import logging

logging.basicConfig(level=logging.INFO)

def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        
        logging.info(f"Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__!r} returned {result!r}")
        
        return result
    return wrapper

@log_function_call
def compute_power(base, exponent=2):
    return base ** exponent

compute_power(4)        # Logs: Calling compute_power(4) and 'compute_power' returned 16
compute_power(2, 3)     # Logs: Calling compute_power(2, 3) and 'compute_power' returned 8
```

### 4.3 Caching/Memoization

```python
import functools

def memoize(func):
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        
        result = func(*args)
        cache[args] = result
        return result
    
    return wrapper

@memoize
def fibonacci(n):
    """Compute the nth Fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Without memoization, this would be very slow
print(fibonacci(35))  # Fast computation with caching
```

Note: For production code, use `functools.lru_cache` which provides a more robust implementation.

### 4.4 Input Validation

```python
import functools

def validate_inputs(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Example: validate all arguments are positive
        for arg in args:
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError(f"Argument {arg} is negative")
        
        for name, value in kwargs.items():
            if isinstance(value, (int, float)) and value < 0:
                raise ValueError(f"Keyword argument {name}={value} is negative")
        
        return func(*args, **kwargs)
    return wrapper

@validate_inputs
def calculate_area(length, width):
    """Calculate the area of a rectangle."""
    return length * width

print(calculate_area(5, 3))     # Works fine, outputs: 15
try:
    print(calculate_area(-5, 3))  # Raises ValueError
except ValueError as e:
    print(e)  # Outputs: Argument -5 is negative
```

### 4.5 Retry Logic

```python
import functools
import time
import random

def retry(max_attempts=3, delay=1):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e
                    
                    print(f"Attempt {attempts} failed, retrying in {delay} seconds...")
                    time.sleep(delay)
            
            return None  # Should not reach here due to raised exception
        return wrapper
    return decorator_retry

@retry(max_attempts=3, delay=0.5)
def unstable_function():
    """Simulate an unstable function that sometimes fails."""
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("Network error")
    return "Success!"

try:
    result = unstable_function()
    print(result)
except ConnectionError:
    print("Function ultimately failed after multiple attempts")
```

### 4.6 Authentication and Access Control

```python
import functools

# Simplified user authentication example
def authenticated_only(func):
    @functools.wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.is_authenticated:
            raise PermissionError("User is not authenticated")
        return func(user, *args, **kwargs)
    return wrapper

class User:
    def __init__(self, name, is_authenticated=False):
        self.name = name
        self.is_authenticated = is_authenticated

@authenticated_only
def view_private_data(user):
    """View data that only authenticated users should see."""
    return f"Private data for {user.name}"

# Example usage
authenticated_user = User("Alice", is_authenticated=True)
unauthenticated_user = User("Bob", is_authenticated=False)

print(view_private_data(authenticated_user))  # Works fine

try:
    print(view_private_data(unauthenticated_user))  # Raises PermissionError
except PermissionError as e:
    print(e)  # Outputs: User is not authenticated
```

## 5. Decorating Classes and Methods

### 5.1 Class Method Decorators

```python
import functools

def trace_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

class Calculator:
    @trace_call
    def add(self, a, b):
        return a + b
    
    @trace_call
    def multiply(self, a, b):
        return a * b

calc = Calculator()
calc.add(3, 5)        # Outputs: "Calling add" then returns 8
calc.multiply(3, 5)   # Outputs: "Calling multiply" then returns 15
```

### 5.2 Class Decorators

You can also decorate entire classes:

```python
def add_greeting(cls):
    """Class decorator that adds a greeting method."""
    def greet(self, name):
        return f"Hello, {name}! I'm {self.__class__.__name__}."
    
    cls.greet = greet
    return cls

@add_greeting
class Person:
    def __init__(self, name):
        self.name = name

person = Person("Alice")
print(person.greet("Bob"))  # Outputs: Hello, Bob! I'm Person.
```

### 5.3 Property Decorators

Python has built-in decorators for class properties:

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Get the current celsius value."""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Set the celsius value."""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Get the current value in fahrenheit."""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Set the value in fahrenheit."""
        self.celsius = (value - 32) * 5/9

# Example usage
temp = Temperature()
print(temp.celsius)    # 0
temp.celsius = 25
print(temp.fahrenheit) # 77.0
temp.fahrenheit = 86
print(temp.celsius)    # 30.0

try:
    temp.celsius = -300  # Raises ValueError
except ValueError as e:
    print(e)  # Temperature below absolute zero is not possible
```

## 6. Advanced Decorator Patterns

### 6.1 Stacking Decorators

You can apply multiple decorators to a function. They are applied from bottom to top:

```python
import functools

def decorator1(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Decorator 1 - Start")
        result = func(*args, **kwargs)
        print("Decorator 1 - End")
        return result
    return wrapper

def decorator2(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Decorator 2 - Start")
        result = func(*args, **kwargs)
        print("Decorator 2 - End")
        return result
    return wrapper

@decorator1
@decorator2
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
```

Output:
```
Decorator 1 - Start
Decorator 2 - Start
Hello, Alice!
Decorator 2 - End
Decorator 1 - End
```

### 6.2 Decorators with State

Decorators can maintain state between function calls:

```python
import functools

def counter(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        print(f"{func.__name__} has been called {wrapper.count} times")
        return func(*args, **kwargs)
    
    # Initialize the counter
    wrapper.count = 0
    return wrapper

@counter
def say_hello():
    print("Hello!")

say_hello()  # Output: say_hello has been called 1 times
say_hello()  # Output: say_hello has been called 2 times
say_hello()  # Output: say_hello has been called 3 times
```

### 6.3 Class-Based Decorators

Using classes as decorators for more complex cases:

```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} has been called {self.count} times")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")

say_hello()  # Output: say_hello has been called 1 times
say_hello()  # Output: say_hello has been called 2 times
```

### 6.4 Decorator Factories with Parameters

More advanced decorator factories that take arguments and return decorators:

```python
import functools
import time

def rate_limit(max_calls, period):
    """
    Decorator factory that limits the number of calls to a function within a time period.
    
    Args:
        max_calls: Maximum number of calls allowed in the time period
        period: Time period in seconds
    """
    def decorator(func):
        # Keep track of calls and timestamps
        calls = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls outside the time window
            while calls and calls[0] < now - period:
                calls.pop(0)
            
            # Check if we've hit the limit
            if len(calls) >= max_calls:
                time_to_wait = calls[0] + period - now
                raise Exception(f"Rate limit exceeded. Try again in {time_to_wait:.2f} seconds.")
            
            # Add current call and execute function
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

@rate_limit(max_calls=3, period=10)
def api_request(endpoint):
    print(f"Requesting data from {endpoint}")
    return {"data": "response"}

# Example: Make several API calls
for i in range(5):
    try:
        result = api_request(f"/api/endpoint/{i}")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Pause to demonstrate
    time.sleep(1)
```

## 7. Built-in Decorators in Python

Python provides several built-in decorators:

### 7.1 `@property`, `@classmethod`, and `@staticmethod`

```python
class MyClass:
    def __init__(self, value):
        self._value = value
    
    @property
    def value(self):
        """Getter for value."""
        return self._value
    
    @value.setter
    def value(self, new_value):
        """Setter for value."""
        if new_value < 0:
            raise ValueError("Value cannot be negative")
        self._value = new_value
    
    @classmethod
    def from_string(cls, value_str):
        """Create a MyClass instance from a string."""
        return cls(int(value_str))
    
    @staticmethod
    def is_valid(value):
        """Check if a value is valid."""
        return value >= 0

# Using property
obj = MyClass(10)
print(obj.value)       # 10
obj.value = 20
print(obj.value)       # 20

# Using class method
obj2 = MyClass.from_string("30")
print(obj2.value)      # 30

# Using static method
print(MyClass.is_valid(5))   # True
print(MyClass.is_valid(-5))  # False
```

### 7.2 `@functools.lru_cache`

```python
import functools
import time

# Memoize with a Least Recently Used (LRU) cache
@functools.lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Measure the time it takes to calculate fibonacci(35)
start = time.time()
result = fibonacci(35)
end = time.time()

print(f"fibonacci(35) = {result}, calculated in {end - start:.6f} seconds")
print(f"Cache info: {fibonacci.cache_info()}")

# Calculate again (should be instant thanks to caching)
start = time.time()
result = fibonacci(35)
end = time.time()

print(f"fibonacci(35) = {result}, calculated in {end - start:.6f} seconds (cached)")
print(f"Cache info: {fibonacci.cache_info()}")
```

### 7.3 `@functools.wraps` and `@functools.partial`

```python
import functools

# We've seen wraps already - it preserves the metadata of the decorated function

# Partial functions create a new function with some arguments fixed
def multiply(a, b):
    return a * b

# Create a function that always multiplies by 2
double = functools.partial(multiply, b=2)
print(double(5))  # Outputs: 10
```

## 8. Common Decorator Pitfalls and Solutions

### 8.1 Losing Function Metadata

**Problem**: Without `@functools.wraps`, decorated functions lose their original identity.

```python
def simple_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@simple_decorator
def my_function():
    """This is my function's docstring."""
    pass

print(my_function.__name__)  # Outputs: "wrapper" instead of "my_function"
print(my_function.__doc__)   # Outputs: None instead of the docstring
```

**Solution**: Always use `@functools.wraps`:

```python
import functools

def better_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@better_decorator
def my_function():
    """This is my function's docstring."""
    pass

print(my_function.__name__)  # Outputs: "my_function"
print(my_function.__doc__)   # Outputs: "This is my function's docstring."
```

### 8.2 Decorating Methods

**Problem**: Regular decorators applied to methods don't handle `self` correctly.

**Solution**: Design decorators to account for instance methods:

```python
import functools

def method_decorator(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):  # Include self parameter
        print(f"Calling method {func.__name__} on {self}")
        return func(self, *args, **kwargs)
    return wrapper

class MyClass:
    @method_decorator
    def my_method(self, x):
        return x * 2

obj = MyClass()
print(obj.my_method(5))  # Works correctly
```

### 8.3 Overusing Decorators

**Problem**: Applying too many decorators makes code hard to understand and debug.

**Solution**: Use decorators judiciously and consider alternative approaches when decorator stacking becomes excessive.

## 9. Real-World Decorator Examples

### 9.1 Flask Route Decorators

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to my website!'

@app.route('/about')
def about():
    return 'About me'

# With parameters
@app.route('/user/<username>')
def show_user(username):
    return f'User profile: {username}'

# With multiple routes
@app.route('/posts')
@app.route('/articles')
def show_posts():
    return 'Here are all posts'

# With methods
@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'Login page'

if __name__ == '__main__':
    app.run(debug=True)
```

### 9.2 Django View Decorators

```python
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse

@login_required
def profile(request):
    """View a user's profile - requires login."""
    return HttpResponse(f"Profile for {request.user.username}")

@require_POST
def submit_form(request):
    """Handle form submission - only accepts POST requests."""
    # Process the form data
    return HttpResponse("Form submitted")

# Combining decorators
@login_required
@require_POST
def change_password(request):
    """Change user's password - requires login and POST method."""
    # Process password change
    return HttpResponse("Password changed")
```

### 9.3 Pytest Fixtures

```python
import pytest

@pytest.fixture
def database_connection():
    """Fixture that sets up a test database connection."""
    # Setup code
    print("Setting up database connection")
    connection = {"connected": True}
    
    # Provide the fixture value
    yield connection
    
    # Teardown code
    print("Closing database connection")

def test_database(database_connection):
    """Test using the database fixture."""
    assert database_connection["connected"] is True
    print("Running test with database")
```

### 9.4 Click Command-Line Interfaces

```python
import click

@click.group()
def cli():
    """Command line tool for processing files."""
    pass

@cli.command()
@click.argument('filename')
@click.option('--verbose', is_flag=True, help='Enable verbose mode')
def process(filename, verbose):
    """Process a file."""
    if verbose:
        click.echo(f"Processing {filename} with verbose mode")
    else:
        click.echo(f"Processing {filename}")

@cli.command()
@click.argument('directory')
@click.option('--recursive', '-r', is_flag=True, help='Process recursively')
def scan(directory, recursive):
    """Scan a directory for files."""
    click.echo(f"Scanning {directory} {'recursively' if recursive else ''}")

if __name__ == '__main__':
    cli()
```

## 10. Custom Decorator Libraries

Several libraries exist to simplify creating and using decorators:

### 10.1 functools and wrapt

```python
import functools
import wrapt

# Using functools.wraps (standard library)
def func_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# Using wrapt (third-party library)
@wrapt.decorator
def wrapt_decorator(wrapped, instance, args, kwargs):
    return wrapped(*args, **kwargs)
```

### 10.2 decorator.py

```python
from decorator import decorator

# Simplified decorator creation
@decorator
def trace(func, *args, **kwargs):
    """Trace function calls."""
    print(f"Calling {func.__name__}")
    return func(*args, **kwargs)

@trace
def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))
```

## 11. When to Use Decorators

Decorators are best used when:

1. You want to add the same functionality to multiple functions
2. The added functionality is auxiliary and not central to the function's purpose
3. You want to separate cross-cutting concerns from business logic
4. You need to modify function behavior without changing its code

Common use cases include:
- Logging, timing, and debugging
- Input validation and type checking
- Caching and memoization
- Authentication and authorization
- Rate limiting and throttling
- Transaction management
- Error handling and retry logic

## 12. Conclusion: Putting It All Together

### 12.1 A Comprehensive Example

Let's create a complete example that combines multiple decorator concepts:

```python
import functools
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Decorator factory for timing functions
def timer(name=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timer_name = name or func.__name__
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                logger.info(f"{timer_name} completed in {elapsed:.4f} seconds")
                return result
            except Exception as e:
                elapsed = time.time() - start
                logger.error(f"{timer_name} failed after {elapsed:.4f} seconds with error: {e}")
                raise
        return wrapper
    return decorator

# Decorator for retry logic
def retry(max_attempts=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logger.error(f"All {max_attempts} attempts failed. Giving up.")
                        raise
                    logger.warning(f"Attempt {attempts} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
            return None  # Should not reach here
        return wrapper
    return decorator

# Decorator for validation
def validate(validator):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            validator(*args, **kwargs)  # Run validation logic
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Some validation functions
def validate_positive_numbers(*args, **kwargs):
    for arg in args:
        if isinstance(arg, (int, float)) and arg < 0:
            raise ValueError(f"Expected positive number, got {arg}")
    
    for key, value in kwargs.items():
        if isinstance(value, (int, float)) and value < 0:
            raise ValueError(f"Expected positive number for {key}, got {value}")

# Create a class with decorated methods
class DataProcessor:
    def __init__(self, name):
        self.name = name
    
    @timer()
    @retry(max_attempts=2, delay=0.5)
    @validate(validate_positive_numbers)
    def process_data(self, data_size, iterations=1):
        """Process a specified amount of data with retries and timing."""
        logger.info(f"Processing {data_size} units of data with {iterations} iterations")
        
        # Simulate processing with occasional failures
        if data_size > 100 and iterations > 3:
            # Simulate a transient error that can be retried
            raise ConnectionError("Simulated connection error")
        
        # Simulate actual work
        time.sleep(data_size * iterations * 0.01)
        
        return f"Processed {data_size * iterations} data points"
    
    @classmethod
    @timer("Class Method Timer")
    def create_processor(cls, name):
        """Create a new processor with timing."""
        time.sleep(0.5)  # Simulate setup work
        return cls(name)

# Example usage
try:
    # Create processor using decorated class method
    processor = DataProcessor.create_processor("Main Processor")
    
    # Process data with decorated instance method
    result1 = processor.process_data(50, iterations=2)
    print(f"Result 1: {result1}")
    
    # This will cause a validation error
    result2 = processor.process_data(-10)
    print(f"Result 2: {result2}")  # This won't execute
    
except Exception as e:
    print(f"Error: {e}")
```

### 12.2 Best Practices Summary

1. **Use `functools.wraps`** to preserve the original function's metadata
2. **Keep decorators simple and focused** on a single responsibility
3. **Document decorators well**, explaining what they do and how they modify function behavior
4. **Handle exceptions** properly within decorators
5. **Design for compatibility** with different function signatures using `*args` and `**kwargs`
6. **Consider the execution order** when stacking multiple decorators
7. **Test decorated functions** thoroughly to ensure they behave as expected
8. **Don't overuse decorators** - they add a layer of indirection that can make code harder to understand

Decorators are a powerful Python feature that, when used correctly, can make your code more elegant, maintainable, and DRY (Don't Repeat Yourself). They enable you to modify function behavior without changing its core implementation, creating a clean separation of concerns.

### 12.3 Quick Reference Cheat Sheet

Here's a quick reference guide for common decorator patterns:

#### Basic Decorator
```python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Do something before
        result = func(*args, **kwargs)
        # Do something after
        return result
    return wrapper
```

#### Decorator with Arguments
```python
def decorator_with_args(param1, param2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use param1, param2
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
```

#### Class Method Decorator
```python
def method_decorator(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Note the 'self' parameter
        result = func(self, *args, **kwargs)
        return result
    return wrapper
```

#### Class-Based Decorator
```python
class ClassDecorator:
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        # Behavior when decorated function is called
        return self.func(*args, **kwargs)
```

#### Stateful Decorator
```python
def stateful_decorator(func):
    counter = [0]  # Using list for mutable state
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        counter[0] += 1
        print(f"Call count: {counter[0]}")
        return func(*args, **kwargs)
    
    return wrapper
```

By understanding and applying these patterns, you can harness the full power of decorators in your Python code, making it more modular, readable, and maintainable.