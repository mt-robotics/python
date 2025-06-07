# Python Testing Strategies

## Introduction

Testing is a critical aspect of professional software development. Effective testing ensures that code behaves as expected, catches bugs early, and makes it easier to maintain and enhance software over time. For senior Python developers, having a comprehensive understanding of testing strategies is essential.

This guide covers:
1. Testing fundamentals and principles
2. Unit testing with pytest and unittest
3. Integration testing approaches
4. Mocking and patching techniques
5. Test-driven development (TDD)
6. Property-based testing
7. Performance and load testing
8. Testing in CI/CD pipelines
9. Testing best practices

## Testing Fundamentals

### Types of Tests

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **Functional Tests**: Test entire features from a user perspective
4. **Performance Tests**: Test system behavior under load
5. **Acceptance Tests**: Verify that requirements are met
6. **Regression Tests**: Ensure that new code doesn't break existing functionality

### Testing Pyramid

The testing pyramid represents the ideal distribution of different types of tests:

```
    /\
   /  \
  /    \  UI/End-to-End Tests (Few)
 /      \
/        \
----------
|        |  Integration Tests (Some)
|        |
----------
|        |
|        |  Unit Tests (Many)
|        |
----------
```

- **Bottom Layer**: Numerous unit tests that are fast and focused
- **Middle Layer**: Fewer integration tests that verify component interactions
- **Top Layer**: A small number of end-to-end tests that validate the entire system

### Test Isolation

Good tests should be:
- **Independent**: Can run in any order
- **Repeatable**: Always give the same result for the same input
- **Self-contained**: Don't depend on external resources that might change
- **Fast**: Run quickly to encourage frequent testing

## Unit Testing with pytest

### Why pytest?

pytest has become the de facto standard for Python testing due to its:
- Simple syntax
- Powerful fixture system
- Rich plugin ecosystem
- Detailed failure reports

### Basic pytest Example

```python
# file: test_calculator.py
import pytest
from calculator import add, subtract

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(-1, -1) == -2

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(2, 3) == -1
    assert subtract(-1, -1) == 0
```

Run with:
```bash
pytest test_calculator.py
```

### Organizing Tests

For larger projects, organize tests in a structure that mirrors your application:

```
project/
├── mypackage/
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
└── tests/
    ├── __init__.py
    ├── test_module1.py
    └── test_module2.py
```

### pytest Fixtures

Fixtures provide a way to set up preconditions for tests:

```python
import pytest
from myapp.models import User
from myapp.database import db_session

@pytest.fixture
def db():
    # Set up: create tables
    db_session.create_tables()
    
    # Provide the fixture value
    yield db_session
    
    # Tear down: clean up after the test
    db_session.drop_tables()

@pytest.fixture
def user(db):
    # This fixture depends on the db fixture
    user = User(name="Test User", email="test@example.com")
    db.add(user)
    db.commit()
    return user

def test_user_exists(db, user):
    found_user = db.query(User).filter_by(name="Test User").first()
    assert found_user is not None
    assert found_user.email == "test@example.com"
```

### Parameterized Tests

Test multiple inputs without duplicating code:

```python
import pytest
from calculator import add

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (10, -10, 0),
    (100, 200, 300)
])
def test_add_parameterized(a, b, expected):
    assert add(a, b) == expected
```

### Marking Tests

Mark tests to categorize them:

```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    # This test takes a long time
    ...

@pytest.mark.api
def test_api_integration():
    # This test calls an external API
    ...
```

Run specific marked tests:
```bash
pytest -m slow  # Run only slow tests
pytest -m "not slow"  # Run all tests except slow ones
```

### Custom Assertions

For complex assertions, create custom helpers:

```python
def assert_user_valid(user):
    """Assert that a user model is valid."""
    assert user.id is not None
    assert user.name is not None
    assert '@' in user.email
    assert len(user.password) >= 8

def test_create_user():
    user = create_user("test", "test@example.com", "password123")
    assert_user_valid(user)
```

## Unit Testing with unittest

While pytest is more popular, unittest is part of the Python standard library and is still widely used.

### Basic unittest Example

```python
import unittest
from calculator import add, subtract

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(-1, -1), -2)
    
    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract(2, 3), -1)
        self.assertEqual(subtract(-1, -1), 0)

if __name__ == '__main__':
    unittest.main()
```

Run with:
```bash
python -m unittest test_calculator.py
```

### unittest Setup and Teardown

unittest provides methods for setup and teardown:

```python
import unittest
from myapp.models import User
from myapp.database import db_session

class TestUser(unittest.TestCase):
    def setUp(self):
        # Run before each test
        db_session.create_tables()
        self.user = User(name="Test User", email="test@example.com")
        db_session.add(self.user)
        db_session.commit()
    
    def tearDown(self):
        # Run after each test
        db_session.drop_tables()
    
    def test_user_exists(self):
        found_user = db_session.query(User).filter_by(name="Test User").first()
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.email, "test@example.com")
```

### Class-level Setup and Teardown

For operations that should run once per test class:

```python
@classmethod
def setUpClass(cls):
    # Run once before all tests in the class
    cls.db = create_database_connection()

@classmethod
def tearDownClass(cls):
    # Run once after all tests in the class
    cls.db.close()
```

### unittest vs pytest

| Feature | unittest | pytest |
|---------|----------|--------|
| Part of standard library | Yes | No |
| Test discovery | Yes | Yes (more powerful) |
| Fixtures | Limited (setUp/tearDown) | Powerful and flexible |
| Parameterization | Limited | Built-in and powerful |
| Assertion style | Method-based (assertEqual, assertTrue) | Python assert statements |
| Extensibility | Less extensible | Highly extensible with plugins |

## Integration Testing

Integration tests verify that components work together correctly.

### Example: Testing Database Interactions

```python
import pytest
from myapp.models import User, Post
from myapp.database import db_session

@pytest.fixture(scope="module")
def db():
    # Set up database once for all tests in this module
    db_session.create_tables()
    yield db_session
    db_session.drop_tables()

def test_user_posts_relationship(db):
    # Create a user
    user = User(name="Test User", email="test@example.com")
    db.add(user)
    db.commit()
    
    # Create posts for the user
    post1 = Post(title="Post 1", content="Content 1", author_id=user.id)
    post2 = Post(title="Post 2", content="Content 2", author_id=user.id)
    db.add(post1)
    db.add(post2)
    db.commit()
    
    # Test the relationship
    db.refresh(user)  # Refresh user to see the new posts
    assert len(user.posts) == 2
    assert user.posts[0].title == "Post 1"
    assert user.posts[1].title == "Post 2"
```

### Testing API Endpoints

```python
import pytest
from fastapi.testclient import TestClient
from myapp.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_users(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert isinstance(data["users"], list)

def test_create_user(client):
    user_data = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "securepassword"
    }
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert "id" in data
```

### Testing File I/O

```python
import os
import tempfile
import pytest
from myapp.fileprocessor import process_file

def test_file_processing():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"line1\nline2\nline3\n")
        tmp_path = tmp.name
    
    try:
        # Process the file
        result = process_file(tmp_path)
        
        # Check the result
        assert result == ["LINE1", "LINE2", "LINE3"]
    finally:
        # Clean up
        os.unlink(tmp_path)
```

## Mocking and Patching

Mocking lets you replace real objects with controlled test doubles.

### Using unittest.mock

```python
from unittest.mock import Mock, patch
import pytest
from myapp.user_service import get_user

def test_get_user_with_mock():
    # Create a mock database
    mock_db = Mock()
    
    # Configure the mock
    mock_db.query.return_value.filter_by.return_value.first.return_value = {
        "id": 1,
        "name": "Mocked User",
        "email": "mock@example.com"
    }
    
    # Use patch to replace the real database with our mock
    with patch("myapp.user_service.db", mock_db):
        user = get_user(1)
        
        # Verify the result
        assert user["name"] == "Mocked User"
        assert user["email"] == "mock@example.com"
        
        # Verify the mock was called correctly
        mock_db.query.assert_called_once()
        mock_db.query().filter_by.assert_called_once_with(id=1)
```

### Mocking HTTP Requests

```python
import requests
import pytest
from unittest.mock import patch
from myapp.github_client import get_user_repositories

# Test function that makes HTTP requests
def test_get_user_repositories():
    # Mock the requests.get function
    with patch("requests.get") as mock_get:
        # Configure the mock response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "repo1", "language": "Python"},
            {"name": "repo2", "language": "JavaScript"}
        ]
        
        # Call the function under test
        repos = get_user_repositories("testuser")
        
        # Verify the result
        assert len(repos) == 2
        assert repos[0]["name"] == "repo1"
        assert repos[0]["language"] == "Python"
        
        # Verify the mock was called correctly
        mock_get.assert_called_once_with(
            "https://api.github.com/users/testuser/repos"
        )
```

### Using pytest-mock

pytest-mock provides a fixture-based approach to mocking:

```python
def test_get_user_with_pytest_mock(mocker):
    # Create a mock using pytest-mock
    mock_db = mocker.patch("myapp.user_service.db")
    
    # Configure the mock
    mock_db.query.return_value.filter_by.return_value.first.return_value = {
        "id": 1,
        "name": "Mocked User"
    }
    
    # Rest of the test...
```

### Mock vs. MagicMock

`MagicMock` is a subclass of `Mock` that implements default magic methods:

```python
from unittest.mock import Mock, MagicMock

# Regular Mock doesn't implement __len__
mock = Mock()
# This would raise TypeError: object of type 'Mock' has no len()
# len(mock)

# MagicMock implements common magic methods
magic_mock = MagicMock()
len(magic_mock)  # Returns 0 by default
magic_mock[0]    # Returns another MagicMock
```

### Mocking Context Managers

```python
from unittest.mock import patch, mock_open

def test_file_reading():
    # Mock the built-in open function
    mock_file_content = "line1\nline2\nline3"
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        with open("fake_file.txt", "r") as f:
            content = f.read()
        
        assert content == mock_file_content
```

### Mocking Time

```python
from unittest.mock import patch
import time
from myapp.cache import Cache

def test_cache_expiry():
    cache = Cache(expiry_seconds=10)
    
    # Mock time.time to control the current time
    with patch("time.time") as mock_time:
        # Set initial time
        mock_time.return_value = 1000
        
        # Add item to cache
        cache.set("key1", "value1")
        
        # Still within expiry time
        mock_time.return_value = 1005
        assert cache.get("key1") == "value1"
        
        # After expiry time
        mock_time.return_value = 1015
        assert cache.get("key1") is None
```

## Test-Driven Development (TDD)

TDD is a development methodology where you write tests before implementing the code.

### The TDD Cycle

1. **Red**: Write a failing test
2. **Green**: Implement the simplest code that passes the test
3. **Refactor**: Improve the code while keeping the tests passing

### TDD Example: Building a Stack

#### Step 1: Write a failing test

```python
# test_stack.py
import pytest
from stack import Stack

def test_stack_push_and_pop():
    stack = Stack()
    stack.push(1)
    assert stack.pop() == 1
```

Running the test will fail because `Stack` doesn't exist yet.

#### Step 2: Implement the simplest code

```python
# stack.py
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        return self.items.pop()
```

Now the test passes.

#### Step 3: Add more tests and functionality

```python
def test_stack_peek():
    stack = Stack()
    stack.push(1)
    stack.push(2)
    assert stack.peek() == 2
    assert stack.pop() == 2
    assert stack.pop() == 1
```

Implement the peek method:

```python
def peek(self):
    return self.items[-1]
```

#### Step 4: Test edge cases

```python
def test_stack_empty():
    stack = Stack()
    assert stack.is_empty() is True
    stack.push(1)
    assert stack.is_empty() is False
    stack.pop()
    assert stack.is_empty() is True

def test_pop_empty_stack():
    stack = Stack()
    with pytest.raises(IndexError):
        stack.pop()
```

Implement the is_empty method:

```python
def is_empty(self):
    return len(self.items) == 0
```

### Benefits of TDD

- Forces you to think about the design before implementation
- Creates a comprehensive test suite automatically
- Helps maintain a clean, working codebase
- Provides immediate feedback on code changes
- Acts as documentation for how the code should behave

## Property-Based Testing

Property-based testing generates random test cases based on properties that should always hold true.

### Using Hypothesis

```bash
pip install hypothesis
```

```python
import pytest
from hypothesis import given, strategies as st
from sorting import sort_list

@given(st.lists(st.integers()))
def test_sort_list_length(numbers):
    """Sorting shouldn't change the length of the list."""
    sorted_numbers = sort_list(numbers)
    assert len(sorted_numbers) == len(numbers)

@given(st.lists(st.integers()))
def test_sort_list_contains_same_elements(numbers):
    """Sorting shouldn't add or remove elements."""
    sorted_numbers = sort_list(numbers)
    assert sorted(sorted_numbers) == sorted(numbers)

@given(st.lists(st.integers()))
def test_sort_list_is_ordered(numbers):
    """Elements should be in ascending order after sorting."""
    sorted_numbers = sort_list(numbers)
    assert all(sorted_numbers[i] <= sorted_numbers[i+1] 
              for i in range(len(sorted_numbers)-1))

@given(st.lists(st.integers(), min_size=1))
def test_sort_list_min_max(numbers):
    """Min and max should be at the extremes after sorting."""
    sorted_numbers = sort_list(numbers)
    assert sorted_numbers[0] == min(numbers)
    assert sorted_numbers[-1] == max(numbers)
```

### Hypothesis Strategies

Hypothesis provides many strategies for generating test data:

```python
# Integers with constraints
st.integers(min_value=0, max_value=100)

# Floating point numbers
st.floats(min_value=0.0, max_value=1.0)

# Text
st.text()
st.text(alphabet="abcdefg")

# Lists
st.lists(st.integers(), min_size=1, max_size=100)

# Dictionaries
st.dictionaries(keys=st.text(), values=st.integers())

# Custom data with builds
st.builds(
    User,
    name=st.text(min_size=1),
    age=st.integers(min_value=18, max_value=100)
)
```

### Hypothesis Example: Testing a Parser

```python
from hypothesis import given, strategies as st
from myapp.parser import parse_config

@given(st.dictionaries(
    keys=st.text(min_size=1),
    values=st.one_of(
        st.integers(),
        st.text(),
        st.booleans()
    )
))
def test_parse_config_roundtrip(config):
    """Test that parsing and then serializing returns the original config."""
    parsed = parse_config(config)
    serialized = parsed.to_dict()
    assert serialized == config
```

## Performance and Load Testing

Performance tests verify that the system meets performance requirements.

### Benchmarking with pytest-benchmark

```bash
pip install pytest-benchmark
```

```python
def test_sorting_performance(benchmark):
    # Generate a large list to sort
    data = [random.randint(0, 1000) for _ in range(10000)]
    
    # Benchmark the sorting function
    result = benchmark(lambda: sort_list(data))
    
    # Verify the result is correct
    assert result == sorted(data)
```

### Load Testing with Locust

Locust is a Python tool for load testing web applications:

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    @task(2)  # Weight of 2
    def view_homepage(self):
        self.client.get("/")
    
    @task(1)  # Weight of 1
    def view_about(self):
        self.client.get("/about")
    
    @task(3)  # Weight of 3
    def view_profile(self):
        self.client.get("/profile")
```

Run with:
```bash
locust -f locust_file.py
```

## Testing in CI/CD Pipelines

Integrating tests into your CI/CD pipeline ensures code quality before deployment.

### GitHub Actions Example

```yaml
name: Python Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Run tests
      run: |
        pytest --cov=myapp tests/
    - name: Upload coverage report
      uses: codecov/codecov-action@v1
```

### Testing Matrix

Test on multiple Python versions and operating systems:

```yaml
strategy:
  matrix:
    python-version: [3.8, 3.9, 3.10]
    os: [ubuntu-latest, macos-latest, windows-latest]
```

### Test Coverage

Monitor test coverage with pytest-cov:

```bash
pytest --cov=myapp tests/
```

Generate HTML reports:
```bash
pytest --cov=myapp --cov-report=html tests/
```

## Functional and End-to-End Testing

### Testing with Selenium

Selenium automates browser interaction for web application testing:

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_login_page(browser):
    browser.get("http://localhost:8000/login")
    
    # Find elements and interact with them
    username_input = browser.find_element(By.ID, "username")
    password_input = browser.find_element(By.ID, "password")
    submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    
    # Fill in the form
    username_input.send_keys("testuser")
    password_input.send_keys("password123")
    submit_button.click()
    
    # Check that login was successful
    assert "Welcome" in browser.page_source
    assert browser.current_url == "http://localhost:8000/dashboard"
```

### Testing with pytest-django

For Django applications:

```python
import pytest
from django.urls import reverse
from myapp.models import User

@pytest.mark.django_db
def test_user_list_view(client):
    # Create test users
    User.objects.create(username="user1", email="user1@example.com")
    User.objects.create(username="user2", email="user2@example.com")
    
    # Get the URL
    url = reverse("user-list")
    
    # Send a GET request
    response = client.get(url)
    
    # Check the response
    assert response.status_code == 200
    assert "user1" in response.content.decode()
    assert "user2" in response.content.decode()
```

### Testing REST APIs

```python
import pytest
import json
from django.urls import reverse
from rest_framework.test import APIClient
from myapp.models import Product

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_create_product(api_client):
    url = reverse("product-list")
    data = {
        "name": "Test Product",
        "price": 9.99,
        "description": "A test product"
    }
    
    response = api_client.post(
        url,
        data=json.dumps(data),
        content_type="application/json"
    )
    
    assert response.status_code == 201
    assert response.data["name"] == "Test Product"
    assert Product.objects.count() == 1
```

## Testing Best Practices

### 1. Keep Tests Fast

- Mock external dependencies
- Use appropriate test scopes
- Avoid unnecessary setup

### 2. Make Tests Independent

- Don't rely on test execution order
- Clean up after tests
- Use fresh fixtures for each test

### 3. Write Clear, Descriptive Test Names

```python
# Bad
def test_user():
    ...

# Good
def test_user_registration_with_valid_data():
    ...
```

### 4. Follow the AAA Pattern

- **Arrange**: Set up the test conditions
- **Act**: Perform the action being tested
- **Assert**: Verify the expected outcome

```python
def test_user_registration():
    # Arrange
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword"
    }
    
    # Act
    user = register_user(**user_data)
    
    # Assert
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("securepassword")
```

### 5. Test Edge Cases

- Empty inputs
- Boundary values
- Invalid inputs
- Error conditions

```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

### 6. Keep Test Code Clean

- Apply the same code quality standards to tests
- Refactor and remove duplication
- Use helper methods for common operations

```python
def create_test_user(username="testuser", email="test@example.com"):
    """Helper function to create a test user."""
    return User.objects.create(
        username=username,
        email=email,
        password="password123"
    )

def test_user_profile():
    user = create_test_user()
    # Rest of the test...
```

### 7. Don't Test External Libraries

- Focus on your own code
- Assume that well-established libraries work correctly

### 8. Use Test Doubles Appropriately

- **Stubs**: Return predefined values
- **Mocks**: Verify interactions
- **Fakes**: Working implementations optimized for testing
- **Spies**: Record interactions
- **Dummies**: Placeholder objects

### 9. Test Failure Scenarios

- Test that errors are handled correctly
- Verify that appropriate exceptions are raised
- Ensure error messages are helpful

### 10. Test Driven Security

- Include security test cases
- Test for common vulnerabilities
- Validate input sanitization

## Advanced Testing Topics

### Testing Asynchronous Code

With pytest-asyncio:

```python
import pytest
import asyncio
from myapp.async_service import fetch_data

@pytest.mark.asyncio
async def test_fetch_data():
    result = await fetch_data("https://api.example.com/data")
    assert result["status"] == "success"
```

### Testing Concurrency

```python
import pytest
import threading
from queue import Queue
from myapp.worker import Worker

def test_concurrent_workers():
    queue = Queue()
    results = []
    
    # Add items to the queue
    for i in range(10):
        queue.put(i)
    
    # Create and start workers
    workers = []
    for _ in range(4):
        worker = Worker(queue, results)
        worker.start()
        workers.append(worker)
    
    # Wait for completion
    queue.join()
    
    # Stop workers
    for worker in workers:
        worker.stop()
        worker.join()
    
    # Check results
    assert len(results) == 10
    assert sorted(results) == list(range(10))
```

### Testing Database Migrations

```python
import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

@pytest.mark.django_db
def test_migration_from_zero():
    # Get the database connection
    executor = MigrationExecutor(connection)
    
    # Get the current migration state
    app_name = "myapp"
    executor.loader.build_graph()
    
    # Go to zero state
    executor.migrate([app_name], None)
    
    # Apply all migrations
    executor.loader.build_graph()
    executor.migrate([app_name])
    
    # Check that the migrations ran correctly
    from myapp.models import User
    User.objects.create(username="test")
```

### Testing Command-Line Interfaces

With click's testing utilities:

```python
from click.testing import CliRunner
from myapp.cli import process_command

def test_process_command():
    runner = CliRunner()
    result = runner.invoke(process_command, ['--input', 'test.txt', '--output', 'result.txt'])
    assert result.exit_code == 0
    assert "Processing complete" in result.output
```

## Conclusion

Testing is an essential skill for senior Python developers. By implementing a comprehensive testing strategy, you can:

- Catch bugs early
- Document code behavior
- Confidently refactor and enhance code
- Ensure the reliability of your software
- Facilitate collaboration with other developers

This guide covered fundamental testing concepts, tools, and best practices. By applying these techniques, you can write more robust, maintainable Python applications.

## Further Resources

1. Books:
   - "Python Testing with pytest" by Brian Okken
   - "Test-Driven Development with Python" by Harry J.W. Percival
   - "Effective Python Testing with pytest" by Dane Hillard

2. Online Resources:
   - [pytest Documentation](https://docs.pytest.org/)
   - [Real Python's Python Testing Guide](https://realpython.com/python-testing/)
   - [Hypothesis Documentation](https://hypothesis.readthedocs.io/)

3. Tools:
   - [pytest](https://pytest.org/)
   - [Hypothesis](https://hypothesis.works/)
   - [pytest-cov](https://pytest-cov.readthedocs.io/)
   - [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
   - [pytest-mock](https://github.com/pytest-dev/pytest-mock/)
