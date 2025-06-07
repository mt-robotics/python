# Comprehensive Guide to Python Exception Handling

## 1. Core Concepts of Exception Handling

Exception handling is a mechanism to deal with errors that occur during program execution without crashing. Python's exceptions are objects that represent errors.

### 1.1 Basic Structure

```python
try:
    # Code that might raise exceptions
    result = risky_operation()
except SomeException:
    # Code to handle the exception
```

### 1.2 The Complete Framework

```python
try:
    # Potentially problematic code
    result = 10 / user_input
except ZeroDivisionError as e:
    # Run if a specific exception occurs
    print(f"Error: {e}")
except (TypeError, ValueError) as e:
    # Handle multiple exception types
    print(f"Input error: {e}")
except Exception as e:
    # Catch any other exceptions
    print(f"Unexpected error: {e}")
else:
    # Run only if NO exceptions were raised
    print(f"Result: {result}")
finally:
    # Always runs, with or without exceptions
    print("Operation attempt completed")
```

## 2. Raising Exceptions

You can trigger exceptions intentionally using the `raise` statement.

### 2.1 Basic Usage

```python
def withdraw(account, amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    if amount > account['balance']:
        raise ValueError("Insufficient funds")
    
    account['balance'] -= amount
    return account['balance']
```

### 2.2 Re-raising Exceptions

You can catch an exception, do something, then re-raise it:

```python
try:
    process_data()
except ValueError as e:
    log_error("Data processing failed", e)
    raise  # Re-raises the caught exception
```

### 2.3 Raising Different Exceptions

You can also raise a different exception:

```python
try:
    data = get_user_data(user_id)
except FileNotFoundError:
    # Convert the exception type to something more meaningful
    raise UserNotFoundError(f"User {user_id} does not exist") from None
```

### 2.4 Exception Chaining

You can chain exceptions to maintain the original cause:

```python
try:
    process_file("data.csv")
except FileNotFoundError as e:
    # Raise a new exception while preserving the original cause
    raise DataProcessingError("Processing failed due to missing file") from e
```

## 3. Custom Exceptions

You can create your own exception types:

```python
class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        self.deficit = amount - balance
        super().__init__(f"Insufficient funds: {balance} available, tried to withdraw {amount}")

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount

# Usage
try:
    new_balance = withdraw(100, 150)
except InsufficientFundsError as e:
    print(f"Transaction failed! You need {e.deficit} more dollars")
```

## 4. Context Managers and Exceptions

The `with` statement creates a context and automatically handles exceptions:

```python
def process_file(filename):
    try:
        with open(filename, 'r') as file:  # Resource automatically cleaned up
            data = file.read()
            return process_data(data)
    except FileNotFoundError:
        logger.error(f"File {filename} not found")
        return None
```

## 5. Exception Hierarchies

Python exceptions form a hierarchy. Here's a simplified view:

```
BaseException
 ├── SystemExit                # Raised by sys.exit()
 ├── KeyboardInterrupt         # Raised when user presses Ctrl+C
 ├── Exception                 # Base class for most exceptions
     ├── StopIteration         # Raised by next() when iterator is exhausted
     ├── ArithmeticError       # Base for arithmetic errors
     │    ├── ZeroDivisionError
     │    ├── OverflowError
     │    └── FloatingPointError
     ├── LookupError           # Base for lookup errors
     │    ├── IndexError       # Sequence index out of range
     │    └── KeyError         # Dictionary key not found
     ├── OSError               # Operating system error
     │    ├── FileNotFoundError
     │    ├── PermissionError
     │    └── ConnectionError
     │         ├── ConnectionRefusedError
     │         ├── ConnectionAbortedError
     │         └── ConnectionResetError
     ├── TypeError             # Wrong type of argument
     ├── ValueError            # Correct type but inappropriate value
     ├── SyntaxError           # Parsing error
     └── RuntimeError          # Generic runtime error
```

Understanding this hierarchy helps you catch exceptions at the appropriate level of specificity.

## 6. Real-World Examples

### 6.1 Database Operations

```python
def get_user(user_id):
    try:
        connection = database.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        
        if result is None:
            raise UserNotFoundError(f"User {user_id} not found")
            
        return User(*result)
        
    except database.ConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        raise ServiceUnavailableError("Database is currently unavailable") from e
        
    except database.SQLError as e:
        logger.error(f"SQL query failed: {e}")
        raise InternalError("An internal error occurred") from e
        
    finally:
        if 'connection' in locals() and connection:
            connection.close()
```

### 6.2 API Requests

```python
def fetch_user_data(user_id, api_key):
    try:
        response = requests.get(
            f"https://api.example.com/users/{user_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )
        
        # Raise an exception for HTTP errors
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        return data
        
    except requests.ConnectionError:
        logger.error("Failed to connect to API server")
        raise ApiConnectionError("Cannot connect to the API server")
        
    except requests.Timeout:
        logger.error("API request timed out")
        raise ApiTimeoutError("API request timed out")
        
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif e.response.status_code == 404:
            raise ResourceNotFoundError(f"User {user_id} not found")
        else:
            logger.error(f"HTTP error: {e}")
            raise ApiError(f"API error: {e}")
            
    except ValueError:  # For .json() parsing errors
        logger.error("Invalid JSON response from API")
        raise DataFormatError("API returned invalid data")
```

### 6.3 File Processing with Error Recovery

```python
def process_data_files(directory):
    results = []
    errors = []
    
    for filename in os.listdir(directory):
        if not filename.endswith('.csv'):
            continue
            
        try:
            data = process_file(os.path.join(directory, filename))
            results.append((filename, data))
            
        except PermissionError:
            errors.append((filename, "Permission denied"))
            continue  # Skip this file, try the next one
            
        except (csv.Error, UnicodeDecodeError) as e:
            logger.warning(f"Error processing {filename}: {e}")
            errors.append((filename, f"Format error: {e}"))
            continue
            
        except Exception as e:
            logger.exception(f"Unexpected error processing {filename}")
            errors.append((filename, f"Unknown error: {e}"))
            continue
    
    # Report on overall success
    if not results and errors:
        raise BatchProcessingError(f"All files failed: {errors}")
        
    return {
        'successful': results,
        'failed': errors
    }
```

## 7. Advanced Techniques

### 7.1 Defining Clean-up Actions

```python
def process_large_file(filename):
    temp_files = []
    
    try:
        # Create temporary files
        temp_files.append(create_temp_file())
        temp_files.append(create_temp_file())
        
        # Process data
        with open(filename, 'r') as f:
            for line in f:
                process_line(line, temp_files)
                
        return compile_results(temp_files)
        
    finally:
        # Clean up regardless of success or failure
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass  # Silently continue if cleanup fails
```

### 7.2 Exception Filtering with `except*` (Python 3.11+)

```python
def process_transaction(amount):
    try:
        validate_amount(amount)
        deduct_from_account(amount)
        record_transaction(amount)
    except* ValueError as exc_group:
        # Handle all ValueError exceptions
        for exc in exc_group.exceptions:
            print(f"Validation error: {exc}")
    except* ConnectionError as exc_group:
        # Handle all connection-related errors
        for exc in exc_group.exceptions:
            print(f"Connection issue: {exc}")
```

### 7.3 Contextlib for Creating Context Managers

```python
from contextlib import contextmanager

@contextmanager
def transaction(session):
    """Context manager for database transactions with automatic rollback."""
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
        
# Usage
with transaction(database.session) as session:
    user = session.query(User).get(user_id)
    user.balance -= amount
    # Transaction automatically committed if no exceptions,
    # or rolled back if any exception occurs
```

## 8. Best Practices

### 8.1 Be Specific

Catch specific exceptions instead of using a bare `except:` clause:

```python
# Bad
try:
    process_data()
except:  # Catches absolutely everything, including KeyboardInterrupt
    handle_error()

# Good
try:
    process_data()
except (ValueError, TypeError) as e:
    handle_specific_error(e)
```

### 8.2 Don't Silence Exceptions

Avoid empty `except` blocks that hide errors:

```python
# Bad
try:
    process_data()
except Exception:
    pass  # Silently continues, hiding the error

# Good
try:
    process_data()
except Exception as e:
    logger.error(f"Data processing failed: {e}")
    # Handle the error or re-raise it
```

### 8.3 Use Exceptions for Exceptional Cases

Exceptions should be used for exceptional conditions, not for normal flow control:

```python
# Bad: Using exceptions for control flow
def get_user_setting(user_id, setting_name):
    try:
        return database.query(f"SELECT value FROM settings WHERE user_id={user_id} AND name='{setting_name}'")[0]
    except IndexError:
        return "default_value"

# Good: Check for the condition explicitly
def get_user_setting(user_id, setting_name):
    result = database.query(f"SELECT value FROM settings WHERE user_id={user_id} AND name='{setting_name}'")
    if result:
        return result[0]
    else:
        return "default_value"
```

### 8.4 Clean Up Resources

Always clean up resources, preferably using `with` statements:

```python
# Bad
f = open("data.txt", "r")
try:
    data = f.read()
finally:
    f.close()

# Good
with open("data.txt", "r") as f:
    data = f.read()
```

### 8.5 Log Exceptions

Log exceptions with enough context to understand what happened:

```python
import logging

try:
    process_order(order_id, user_id)
except Exception as e:
    logging.exception(f"Failed to process order {order_id} for user {user_id}")
    # The exception() method automatically includes the traceback
```

## 9. Tracebacks and Debugging

### 9.1 Preserving Tracebacks

The `traceback` module lets you work with exception traces:

```python
import traceback

try:
    # Some risky code
    problematic_function()
except Exception as e:
    # Get traceback as a string
    error_traceback = traceback.format_exc()
    
    # Log the full traceback
    with open("error_log.txt", "a") as log:
        log.write(f"Error occurred: {e}\n")
        log.write(error_traceback)
        log.write("\n---\n")
```

### 9.2 Printing Exception Information

```python
try:
    complex_operation()
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print(f"Error occurred on line: {sys.exc_info()[2].tb_lineno}")
```

## 10. Exception Safety Guarantees

When designing functions that may raise exceptions, consider providing these guarantees:

### 10.1 Basic Guarantee

If an exception occurs, no resources are leaked and the program remains in a valid state:

```python
def process_data(data):
    temp_file = create_temp_file()
    try:
        # Process data, may raise exceptions
        result = transform_data(data)
        write_to_file(temp_file, result)
        return read_from_file(temp_file)
    finally:
        # Always clean up
        os.remove(temp_file)
```

### 10.2 Strong Guarantee

If an exception occurs, the operation has no effect (like a transaction rollback):

```python
def update_user(user, new_data):
    # Save the original state
    original_data = user.data.copy()
    
    try:
        # Update user data
        for key, value in new_data.items():
            validate_field(key, value)  # May raise ValueError
            user.data[key] = value
            
        # Save changes
        user.save()  # May raise DatabaseError
        
    except Exception:
        # Restore original state on any error
        user.data = original_data
        raise  # Re-raise the exception
```

## 11. Exception Handling in Asynchronous Code

With async/await syntax, exception handling looks similar:

```python
async def fetch_data(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error when fetching {url}: {e}")
        raise DataFetchError(f"Failed to fetch data from {url}") from e
    except asyncio.TimeoutError:
        logger.error(f"Timeout when fetching {url}")
        raise DataFetchError(f"Timeout when fetching {url}") from None
```

## 12. Practical Exception Handling Patterns

### 12.1 Retry Pattern

```python
def retry_operation(operation, max_attempts=3, retry_delay=1):
    """Retry an operation with exponential backoff."""
    attempt = 0
    last_exception = None
    
    while attempt < max_attempts:
        try:
            return operation()
        except (ConnectionError, TimeoutError) as e:
            attempt += 1
            last_exception = e
            
            if attempt < max_attempts:
                # Exponential backoff
                sleep_time = retry_delay * (2 ** (attempt - 1))
                logger.warning(f"Attempt {attempt} failed, retrying in {sleep_time}s: {e}")
                time.sleep(sleep_time)
    
    # If we get here, all attempts failed
    logger.error(f"All {max_attempts} attempts failed")
    raise MaxRetryError(f"Operation failed after {max_attempts} attempts") from last_exception
```

### 12.2 Fallback Pattern

```python
def get_user_data(user_id):
    """Try to get fresh data, fall back to cached data if not available."""
    try:
        # Try to get fresh data from API
        return api_client.get_user(user_id)
    except ConnectionError as e:
        logger.warning(f"Could not connect to API, using cache: {e}")
        
        try:
            # Try to get data from cache
            return cache.get_user(user_id)
        except CacheError as cache_e:
            logger.error(f"Cache retrieval failed: {cache_e}")
            raise DataUnavailableError("Could not retrieve user data") from e
```

### 12.3 Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "closed"  # closed = normal, open = failing
        self.last_failure_time = 0
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if self.state == "open":
                if time.time() - self.last_failure_time >= self.reset_timeout:
                    # Try to recover
                    self.state = "half-open"
                else:
                    raise CircuitBreakerError(f"Circuit breaker is open for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                # Success resets the circuit breaker if it was half-open
                if self.state == "half-open":
                    self.failure_count = 0
                    self.state = "closed"
                    
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    
                raise
                
        return wrapper

# Usage
@CircuitBreaker(failure_threshold=3, reset_timeout=30)
def call_external_api(parameter):
    return requests.get(f"https://api.example.com/data?param={parameter}")
```

## 13. Testing Exception Handling

### 13.1 Using pytest

```python
import pytest

def test_withdraw_with_insufficient_funds():
    account = {"balance": 100}
    
    with pytest.raises(ValueError) as excinfo:
        withdraw(account, 150)
    
    # Check exception message
    assert "Insufficient funds" in str(excinfo.value)
    
    # Check that account wasn't modified
    assert account["balance"] == 100
```

### 13.2 Mocking to Test Exception Handling

```python
from unittest.mock import patch, MagicMock

def test_get_user_with_api_failure():
    # Create a mock API that raises an exception
    mock_api = MagicMock()
    mock_api.get_user.side_effect = ConnectionError("API unavailable")
    
    # Create a mock cache with good data
    mock_cache = MagicMock()
    mock_cache.get_user.return_value = {"id": 123, "name": "Test User"}
    
    with patch('myapp.api_client', mock_api), patch('myapp.cache', mock_cache):
        # Function should fall back to cache
        result = get_user_data(123)
        
        # Verify API was called
        mock_api.get_user.assert_called_once_with(123)
        
        # Verify result came from cache
        assert result == {"id": 123, "name": "Test User"}
```

## 14. Summary

Effective exception handling is a critical part of robust Python code. By following these principles, you can build more resilient applications:

1. **Be specific** about which exceptions you catch
2. **Don't suppress exceptions** without handling them properly
3. **Use the full power** of the try-except-else-finally structure
4. **Create custom exceptions** for your application's domains
5. **Maintain context** through proper exception chaining
6. **Clean up resources** properly with context managers
7. **Log exceptions** with appropriate context
8. **Consider safety guarantees** when designing functions
9. **Use appropriate patterns** like retry and fallback for robust code
10. **Test your exception handling** thoroughly

By mastering these concepts, you'll be able to handle error conditions gracefully and build more reliable Python applications.
