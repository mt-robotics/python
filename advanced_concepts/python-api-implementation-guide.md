# Comprehensive Guide to API Documentation and Implementation in Python

## 1. Understanding APIs and Documentation

### 1.1 What Is an API?

An API (Application Programming Interface) is a set of rules and protocols that allows different software applications to communicate with each other. In Python, APIs can refer to:

1. **Library/Module APIs**: The classes, functions, and methods exposed by a Python package
2. **Web APIs**: HTTP-based services that your Python code can interact with
3. **Framework APIs**: Interfaces provided by frameworks like Django or Flask

### 1.2 The Importance of API Documentation

Good API documentation:
- Explains how to use the API correctly
- Provides examples and use cases
- Documents parameters, return values, and exceptions
- Describes limitations and edge cases
- Makes development faster and more efficient

### 1.3 Types of API Documentation

1. **Reference Documentation**: Complete, detailed information about all API components
2. **Tutorials**: Step-by-step guides for common tasks
3. **How-to Guides**: Practical examples for specific problems
4. **Conceptual Documentation**: Explains the API's architecture and design principles

## 2. Reading and Understanding Python Library Documentation

### 2.1 Understanding Python's Official Documentation

Python's official documentation follows a standard structure:

```python
def function_name(param1, param2=None, *args, **kwargs):
    """Short description of what the function does.
    
    More detailed explanation if needed.
    
    Parameters
    ----------
    param1 : type
        Description of param1
    param2 : type, optional
        Description of param2, default is None
    *args : tuple
        Variable positional arguments
    **kwargs : dict
        Variable keyword arguments
    
    Returns
    -------
    return_type
        Description of the return value
    
    Raises
    ------
    ExceptionType
        When/why this exception is raised
    
    Examples
    --------
    >>> function_name(1, 2)
    3
    """
    # Function implementation
    pass
```

### 2.2 Reading Third-Party Library Documentation

When exploring a new library's API:

1. **Start with the overview/introduction**
2. **Look for quickstart guides**
3. **Check for tutorials and examples**
4. **Refer to API reference for details**
5. **Look for code examples for similar use cases**

### 2.3 Finding the Right Methods and Classes

To navigate large library documentation:

1. **Use the search function** in the documentation
2. **Check the module index** for a comprehensive list
3. **Look at class hierarchies** to understand relationships
4. **Examine the examples** to see what classes/methods are commonly used
5. **Use Python's built-in help**:

```python
import some_library
help(some_library)  # View top-level documentation
help(some_library.SomeClass)  # View class documentation
```

### 2.4 Example: Reading the Requests Library Documentation

```python
import requests

# Let's explore the requests library
help(requests)

# Get detailed help on the get function
help(requests.get)

# From the documentation, we learn how to make a simple GET request
response = requests.get('https://api.example.com/data')

# Check status code (as documented)
if response.status_code == 200:
    # Access JSON data (as documented)
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")
```

## 3. Working with Web APIs

### 3.1 Understanding RESTful APIs

REST (Representational State Transfer) is an architectural style for web APIs:

- **Resources** are identified by URLs
- **HTTP methods** define actions:
  - GET: Retrieve data
  - POST: Create new data
  - PUT/PATCH: Update data
  - DELETE: Remove data
- **Status codes** indicate results (200 OK, 404 Not Found, etc.)
- **JSON or XML** typically used for data exchange

### 3.2 Making API Requests with Python

Using the requests library:

```python
import requests

# Basic GET request
response = requests.get('https://api.example.com/users')

# GET with query parameters
params = {'page': 1, 'limit': 10}
response = requests.get('https://api.example.com/users', params=params)

# POST request with JSON data
user_data = {'name': 'John', 'email': 'john@example.com'}
response = requests.post('https://api.example.com/users', json=user_data)

# PUT request to update data
update_data = {'name': 'John Smith'}
response = requests.put('https://api.example.com/users/123', json=update_data)

# DELETE request
response = requests.delete('https://api.example.com/users/123')
```

### 3.3 Handling API Responses

```python
import requests

def call_api(url, method='get', **kwargs):
    """Make an API call and handle common response scenarios."""
    # Select the appropriate method
    method_func = getattr(requests, method.lower())
    
    try:
        response = method_func(url, **kwargs)
        
        # Raise exception for HTTP errors
        response.raise_for_status()
        
        # Return JSON data if available
        if response.headers.get('content-type') == 'application/json':
            return response.json()
        else:
            return response.text
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        # You might want to handle different status codes differently
        if response.status_code == 404:
            print("Resource not found")
        elif response.status_code == 401:
            print("Authentication required")
        # Re-raise or return None/default value
        return None
        
    except requests.exceptions.ConnectionError:
        print("Connection error. Please check your internet connection.")
        return None
        
    except requests.exceptions.Timeout:
        print("Request timed out. Please try again later.")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Example usage
users = call_api('https://api.example.com/users', params={'limit': 10})
if users:
    for user in users:
        print(user['name'])
```

### 3.4 Authentication Methods

```python
import requests

# Basic authentication
response = requests.get(
    'https://api.example.com/private',
    auth=('username', 'password')
)

# API key in header
headers = {'X-Api-Key': 'your_api_key_here'}
response = requests.get('https://api.example.com/data', headers=headers)

# API key as query parameter
params = {'api_key': 'your_api_key_here'}
response = requests.get('https://api.example.com/data', params=params)

# OAuth 2.0 with Bearer token
headers = {'Authorization': 'Bearer your_access_token_here'}
response = requests.get('https://api.example.com/data', headers=headers)
```

### 3.5 Rate Limiting and Pagination

```python
import requests
import time

def get_all_pages(base_url, params=None):
    """Get all pages of results from a paginated API."""
    if params is None:
        params = {}
    
    all_results = []
    page = 1
    more_pages = True
    
    while more_pages:
        # Update page parameter
        params['page'] = page
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Add results from this page
            if 'results' in data:
                page_results = data['results']
                all_results.extend(page_results)
            
            # Check if there are more pages
            if 'next' in data and data['next']:
                page += 1
                
                # Respect rate limits
                if 'X-RateLimit-Remaining' in response.headers:
                    remaining = int(response.headers['X-RateLimit-Remaining'])
                    if remaining < 5:  # Getting low on remaining requests
                        reset_time = int(response.headers.get('X-RateLimit-Reset', 60))
                        print(f"Rate limit almost reached. Waiting {reset_time} seconds...")
                        time.sleep(reset_time)
            else:
                more_pages = False
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    return all_results

# Example usage
all_users = get_all_pages('https://api.example.com/users', {'limit': 100})
print(f"Retrieved {len(all_users)} users")
```

## 4. Creating and Documenting Your Own APIs

### 4.1 Documenting Python Module APIs with Docstrings

There are several common docstring formats:

#### Google Style

```python
def calculate_area(length, width=None):
    """Calculate the area of a rectangle or square.
    
    Args:
        length (float): The length of the rectangle.
        width (float, optional): The width of the rectangle. 
            If not provided, the shape is assumed to be a square.
    
    Returns:
        float: The calculated area.
    
    Raises:
        ValueError: If either dimension is negative.
    
    Examples:
        >>> calculate_area(4, 5)
        20.0
        >>> calculate_area(4)  # Square
        16.0
    """
    if length < 0 or (width is not None and width < 0):
        raise ValueError("Dimensions cannot be negative")
    
    if width is None:
        width = length
        
    return length * width
```

#### NumPy/SciPy Style

```python
def calculate_area(length, width=None):
    """Calculate the area of a rectangle or square.
    
    Parameters
    ----------
    length : float
        The length of the rectangle.
    width : float, optional
        The width of the rectangle. If not provided, the shape is 
        assumed to be a square.
    
    Returns
    -------
    float
        The calculated area.
    
    Raises
    ------
    ValueError
        If either dimension is negative.
    
    Examples
    --------
    >>> calculate_area(4, 5)
    20.0
    >>> calculate_area(4)  # Square
    16.0
    """
    if length < 0 or (width is not None and width < 0):
        raise ValueError("Dimensions cannot be negative")
    
    if width is None:
        width = length
        
    return length * width
```

#### reStructuredText (reST) Style

```python
def calculate_area(length, width=None):
    """Calculate the area of a rectangle or square.
    
    :param length: The length of the rectangle.
    :type length: float
    :param width: The width of the rectangle. If not provided, the shape is 
                  assumed to be a square.
    :type width: float, optional
    :return: The calculated area.
    :rtype: float
    :raises ValueError: If either dimension is negative.
    
    :Example:
    
    >>> calculate_area(4, 5)
    20.0
    >>> calculate_area(4)  # Square
    16.0
    """
    if length < 0 or (width is not None and width < 0):
        raise ValueError("Dimensions cannot be negative")
    
    if width is None:
        width = length
        
    return length * width
```

### 4.2 Generating Documentation with Sphinx

Sphinx is a popular tool for generating documentation from Python docstrings:

1. **Install Sphinx and extensions**:
   ```bash
   pip install sphinx sphinx-autodoc-typehints
   ```

2. **Initialize a Sphinx project**:
   ```bash
   mkdir docs
   cd docs
   sphinx-quickstart
   ```

3. **Configure `conf.py`**:
   ```python
   # Add extensions
   extensions = [
       'sphinx.ext.autodoc',
       'sphinx.ext.napoleon',  # For Google/NumPy style docstrings
       'sphinx.ext.viewcode',
       'sphinx_autodoc_typehints',
   ]
   
   # Add source directories
   import os
   import sys
   sys.path.insert(0, os.path.abspath('..'))
   ```

4. **Create API documentation files**:
   ```rst
   .. automodule:: mymodule
      :members:
      :undoc-members:
      :show-inheritance:
   ```

5. **Build the documentation**:
   ```bash
   make html
   ```

### 4.3 Creating RESTful APIs with Flask

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory database for demo
users = {}
next_id = 1

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users or filter by query parameters.
    
    Query Parameters:
        name (str): Filter users by name
        
    Returns:
        JSON response with list of users
    """
    # Handle query parameters
    name_filter = request.args.get('name')
    
    if name_filter:
        filtered_users = {
            user_id: user for user_id, user in users.items() 
            if name_filter.lower() in user['name'].lower()
        }
        return jsonify(list(filtered_users.values()))
    
    return jsonify(list(users.values()))

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID.
    
    Parameters:
        user_id (int): The user ID
        
    Returns:
        JSON response with user data or 404 error
    """
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify(users[user_id])

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user.
    
    Request Body:
        JSON object with user data (name and email required)
        
    Returns:
        JSON response with created user data and 201 status code
    """
    global next_id
    
    data = request.get_json()
    
    # Validate input
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    # Create new user
    user = {
        'id': next_id,
        'name': data['name'],
        'email': data['email']
    }
    
    users[next_id] = user
    next_id += 1
    
    return jsonify(user), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user.
    
    Parameters:
        user_id (int): The user ID
        
    Request Body:
        JSON object with user data to update
        
    Returns:
        JSON response with updated user data or 404 error
    """
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update user data
    if 'name' in data:
        users[user_id]['name'] = data['name']
    if 'email' in data:
        users[user_id]['email'] = data['email']
    
    return jsonify(users[user_id])

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user.
    
    Parameters:
        user_id (int): The user ID
        
    Returns:
        Empty response with 204 status code or 404 error
    """
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    del users[user_id]
    return '', 204

if __name__ == '__main__':
    # Add some initial data
    users = {
        1: {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
        2: {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
    }
    next_id = 3
    
    app.run(debug=True)
```

### 4.4 Documenting Web APIs with OpenAPI/Swagger

```python
from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# In-memory database for demo
users = {}
next_id = 1

@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Get all users
    ---
    tags:
      - Users
    parameters:
      - name: name
        in: query
        type: string
        required: false
        description: Filter users by name
    responses:
      200:
        description: List of users
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: The user ID
              name:
                type: string
                description: The user name
              email:
                type: string
                description: The user email
    """
    # Handle query parameters
    name_filter = request.args.get('name')
    
    if name_filter:
        filtered_users = {
            user_id: user for user_id, user in users.items() 
            if name_filter.lower() in user['name'].lower()
        }
        return jsonify(list(filtered_users.values()))
    
    return jsonify(list(users.values()))

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get a specific user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The user ID
    responses:
      200:
        description: User found
        schema:
          type: object
          properties:
            id:
              type: integer
              description: The user ID
            name:
              type: string
              description: The user name
            email:
              type: string
              description: The user email
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message
    """
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify(users[user_id])

# Continue with other endpoints...

if __name__ == '__main__':
    # Add some initial data
    users = {
        1: {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
        2: {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
    }
    next_id = 3
    
    app.run(debug=True)
```

## 5. API Design Best Practices

### 5.1 API Design Principles

1. **Consistency**: Use consistent naming, parameters, and response formats
2. **Simplicity**: Make your API easy to understand and use
3. **Robustness**: Handle errors gracefully and provide helpful error messages
4. **Documentation**: Document your API thoroughly with examples
5. **Versioning**: Use versioning to make changes without breaking existing clients

### 5.2 Naming Conventions

```python
# Good naming
def get_user(user_id):
    """Get a user by ID."""
    pass

def create_user(user_data):
    """Create a new user."""
    pass

def update_user(user_id, user_data):
    """Update a user."""
    pass

def delete_user(user_id):
    """Delete a user."""
    pass

# Bad naming (inconsistent, unclear)
def user(id):  # Doesn't indicate action
    pass

def make_new(data):  # Unclear what's being created
    pass

def modification(id, data):  # Verbose and unclear
    pass

def destroy_user_record_in_db(id):  # Overly verbose
    pass
```

### 5.3 Parameter Design

```python
# Good parameter design
def search_products(
    query=None,
    category=None,
    min_price=None,
    max_price=None,
    sort_by='relevance',
    page=1,
    page_size=20
):
    """
    Search for products with various filters.
    
    Args:
        query (str, optional): Search query string
        category (str, optional): Filter by category
        min_price (float, optional): Minimum price filter
        max_price (float, optional): Maximum price filter
        sort_by (str, optional): Field to sort by. Default is 'relevance'.
            Options: 'relevance', 'price_asc', 'price_desc', 'newest'
        page (int, optional): Page number for pagination. Default is 1.
        page_size (int, optional): Number of results per page. Default is 20.
            Maximum allowed is 100.
    
    Returns:
        dict: Search results with pagination info
    """
    # Implementation
    pass
```

### 5.4 Error Handling and Status Codes

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = dict(self.payload or ())
        result['error'] = self.message
        return result

@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle custom API errors."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify(error="Resource not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify(error="Internal server error"), 500

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    # Simulate database lookup
    if user_id == 0:
        # Example of raising a custom error
        raise APIError("Invalid user ID", status_code=400)
    elif user_id not in [1, 2, 3]:
        # Example of raising a not found error
        raise APIError("User not found", status_code=404)
    
    # Normal response
    return jsonify({
        'id': user_id,
        'name': f"User {user_id}",
        'email': f"user{user_id}@example.com"
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### 5.5 API Versioning

```python
from flask import Flask, Blueprint, jsonify

app = Flask(__name__)

# Create blueprints for different API versions
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Version 1 endpoints
@api_v1.route('/users/<int:user_id>')
def get_user_v1(user_id):
    """Get user (API v1)."""
    # Original version with basic fields
    return jsonify({
        'id': user_id,
        'name': f"User {user_id}",
        'email': f"user{user_id}@example.com"
    })

# Version 2 endpoints
@api_v2.route('/users/<int:user_id>')
def get_user_v2(user_id):
    """Get user (API v2)."""
    # Enhanced version with additional fields
    return jsonify({
        'id': user_id,
        'name': f"User {user_id}",
        'email': f"user{user_id}@example.com",
        'profile_url': f"https://example.com/users/{user_id}",
        'created_at': "2023-01-01T00:00:00Z"
    })

# Register both API versions
app.register_blueprint(api_v1)
app.register_blueprint(api_v2)

if __name__ == '__main__':
    app.run(debug=True)
```

## 6. Testing APIs

### 6.1 Unit Testing APIs

```python
import unittest
import json
from app import app  # Your Flask application

class APITestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and other test variables."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Sample data for testing
        self.user_data = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
    
    def test_get_users(self):
        """Test GET /api/users endpoint."""
        response = self.app.get('/api/users')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(data, list))
    
    def test_create_user(self):
        """Test POST /api/users endpoint."""
        response = self.app.post(
            '/api/users',
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['name'], self.user_data['name'])
        self.assertEqual(data['email'], self.user_data['email'])
        self.assertTrue('id' in data)
    
    def test_get_user(self):
        """Test GET /api/users/:id endpoint."""
        # First create a user
        create_response = self.app.post(
            '/api/users',
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        user_id = json.loads(create_response.data)['id']
        
        # Now get the user
        response = self.app.get(f'/api/users/{user_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], self.user_data['name'])
        self.assertEqual(data['id'], user_id)
    
    def test_get_nonexistent_user(self):
        """Test getting a user that doesn't exist."""
        response = self.app.get('/api/users/9999')
        
        self.assertEqual(response.status_code, 404)
        self.assertTrue('error' in json.loads(response.data))
    
    def test_update_user(self):
        """Test PUT /api/users/:id endpoint."""
        # First create a user
        create_response = self.app.post(
            '/api/users',
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        user_id = json.loads(create_response.data)['id']
        
        # Update the user
        update_data = {'name': 'Updated Name'}
        response = self.app.put(
            f'/api/users/{user_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], update_data['name'])
        self.assertEqual(data['email'], self.user_data['email'])  # Unchanged
    
    def test_delete_user(self):
        """Test DELETE /api/users/:id endpoint."""
        # First create a user
        create_response = self.app.post(
            '/api/users',
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        user_id = json.loads(create_response.data)['id']
        
        # Delete the user
        response = self.app.delete(f'/api/users/{user_id}')
        
        self.assertEqual(response.status_code, 204)
        
        # Verify the user is gone
        get_response = self.app.get(f'/api/users/{user_id}')
        self.assertEqual(get_response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
```

### 6.2 Testing with Pytest

```python
import pytest
import json
from app import app  # Your Flask application

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'name': 'Test User',
        'email': 'test@example.com'
    }

def test_get_users(client):
    """Test getting all users."""
    response = client.get('/api/users')
    assert response.status_code == 200
    assert isinstance(json.loads(response.data), list)

def test_create_user(client, sample_user_data):
    """Test creating a new user."""
    response = client.post(
        '/api/users',
        data=json.dumps(sample_user_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['name'] == sample_user_data['name']
    assert data['email'] == sample_user_data['email']
    assert 'id' in data

def test_user_lifecycle(client, sample_user_data):
    """Test the complete lifecycle of a user (create, get, update, delete)."""
    # Create
    create_response = client.post(
        '/api/users',
        data=json.dumps(sample_user_data),
        content_type='application/json'
    )
    user_id = json.loads(create_response.data)['id']
    assert create_response.status_code == 201
    
    # Get
    get_response = client.get(f'/api/users/{user_id}')
    get_data = json.loads(get_response.data)
    assert get_response.status_code == 200
    assert get_data['name'] == sample_user_data['name']
    
    # Update
    update_data = {'name': 'Updated Name'}
    update_response = client.put(
        f'/api/users/{user_id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    update_data = json.loads(update_response.data)
    assert update_response.status_code == 200
    assert update_data['name'] == 'Updated Name'
    
    # Delete
    delete_response = client.delete(f'/api/users/{user_id}')
    assert delete_response.status_code == 204
    
    # Verify deletion
    get_after_delete = client.get(f'/api/users/{user_id}')
    assert get_after_delete.status_code == 404
```

### 6.3 API Integration Testing

Integration tests verify that your API works correctly with external services or databases:

```python
import pytest
import requests
import json
from app import app, db
from app.models import User

@pytest.fixture
def setup_database():
    """Set up a test database."""
    # Create tables
    db.create_all()
    
    # Add test data
    test_user = User(name='Test User', email='test@example.com')
    db.session.add(test_user)
    db.session.commit()
    
    yield
    
    # Clean up
    db.session.remove()
    db.drop_all()

@pytest.fixture
def api_client(setup_database):
    """Create a test API client with a configured database."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_external_api_integration(api_client, requests_mock):
    """Test integration with an external weather API."""
    # Mock the external API
    requests_mock.get(
        'https://api.weather.com/current?city=London',
        json={'temperature': 15, 'conditions': 'Cloudy'}
    )
    
    # Test our API that uses the external API
    response = api_client.get('/api/weather/London')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'temperature' in data
    assert data['temperature'] == 15
```

### 6.4 Load Testing APIs

```python
import time
import concurrent.futures
import requests
import statistics

def call_api(endpoint):
    """Make an API call and return the response time."""
    start_time = time.time()
    response = requests.get(endpoint)
    end_time = time.time()
    response_time = end_time - start_time
    return {
        'status_code': response.status_code,
        'response_time': response_time
    }

def load_test(endpoint, num_requests=100, concurrent=10):
    """
    Perform a simple load test on an API endpoint.
    
    Args:
        endpoint: The API URL to test
        num_requests: Total number of requests to make
        concurrent: Number of concurrent requests
    
    Returns:
        dict: Load test results
    """
    results = []
    success_count = 0
    
    print(f"Running load test on {endpoint}")
    print(f"Making {num_requests} requests with {concurrent} concurrent users")
    
    start_time = time.time()
    
    # Use a thread pool to make concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent) as executor:
        # Submit all requests
        future_to_request = {
            executor.submit(call_api, endpoint): i 
            for i in range(num_requests)
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_request):
            result = future.result()
            results.append(result)
            
            if result['status_code'] == 200:
                success_count += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate statistics
    response_times = [r['response_time'] for r in results]
    avg_response_time = statistics.mean(response_times)
    p95_response_time = sorted(response_times)[int(num_requests * 0.95)]
    
    return {
        'total_requests': num_requests,
        'successful_requests': success_count,
        'success_rate': success_count / num_requests * 100,
        'total_time': total_time,
        'requests_per_second': num_requests / total_time,
        'avg_response_time': avg_response_time,
        'min_response_time': min(response_times),
        'max_response_time': max(response_times),
        'p95_response_time': p95_response_time
    }

if __name__ == '__main__':
    # Example usage
    results = load_test('http://localhost:5000/api/users', num_requests=500, concurrent=50)
    
    print("\nLoad Test Results:")
    print(f"Total Requests: {results['total_requests']}")
    print(f"Success Rate: {results['success_rate']:.2f}%")
    print(f"Requests Per Second: {results['requests_per_second']:.2f}")
    print(f"Average Response Time: {results['avg_response_time'] * 1000:.2f}ms")
    print(f"95th Percentile Response Time: {results['p95_response_time'] * 1000:.2f}ms")
    print(f"Min/Max Response Time: {results['min_response_time'] * 1000:.2f}ms / {results['max_response_time'] * 1000:.2f}ms")
```

## 7. API Authentication and Security

### 7.1 Implementing Basic Authentication

```python
from flask import Flask, request, jsonify
from functools import wraps
import base64

app = Flask(__name__)

def require_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        
        if not auth or not auth.startswith('Basic '):
            return jsonify({'error': 'Authentication required'}), 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            }
        
        try:
            # Extract and decode credentials
            encoded_credentials = auth[6:]  # Remove 'Basic '
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            # Check credentials (in a real app, check against a database)
            if username != 'admin' or password != 'secret':
                raise ValueError("Invalid credentials")
                
        except Exception as e:
            return jsonify({'error': 'Invalid credentials'}), 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            }
        
        # Add user info to request object
        request.user = {'username': username}
        return f(*args, **kwargs)
    
    return decorated

@app.route('/api/protected')
@require_basic_auth
def protected_resource():
    return jsonify({
        'message': f"Hello, {request.user['username']}! This is a protected resource."
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### 7.2 Implementing Token-Based Authentication

```python
from flask import Flask, request, jsonify
from functools import wraps
import jwt
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development-key')

# Simple user database for demo
users = {
    'user1': {'password': 'password1', 'name': 'User One'},
    'user2': {'password': 'password2', 'name': 'User Two'}
}

def generate_token(username):
    """Generate a JWT token for a user."""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    
    payload = {
        'sub': username,  # Subject
        'iat': datetime.datetime.utcnow(),  # Issued at
        'exp': expiration  # Expiration time
    }
    
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Verify token
            payload = jwt.decode(
                token, 
                app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            username = payload['sub']
            
            # Check if user exists
            if username not in users:
                raise ValueError("User not found")
                
            # Add user info to request
            request.user = {'username': username, 'name': users[username]['name']}
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except (jwt.InvalidTokenError, ValueError) as e:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    """Login and get a token."""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username']
    password = data['password']
    
    # Check credentials
    if username not in users or users[username]['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token = generate_token(username)
    
    return jsonify({
        'token': token,
        'expires_in': 7200  # 2 hours in seconds
    })

@app.route('/api/protected')
@token_required
def protected_resource():
    """A protected resource requiring a valid token."""
    return jsonify({
        'message': f"Hello, {request.user['name']}! This is a protected resource.",
        'data': {
            'username': request.user['username'],
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### 7.3 API Security Best Practices

1. **Use HTTPS**: Always use HTTPS to encrypt data in transit

2. **Implement Rate Limiting**:
```python
from flask import Flask, request, jsonify
from functools import wraps
import time
import redis

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def rate_limit(limit=100, per=60, key_prefix='rl'):
    """
    Rate limiting decorator.
    
    Args:
        limit: Maximum number of requests allowed
        per: Time window in seconds
        key_prefix: Redis key prefix
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get client identifier (IP address or API key)
            identifier = request.headers.get('X-API-Key', request.remote_addr)
            key = f"{key_prefix}:{identifier}"
            
            # Get current count
            current = redis_client.get(key)
            
            if current is not None and int(current) >= limit:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Increment the counter
            pipe = redis_client.pipeline()
            pipe.incr(key)
            # Set expiry if the key is new
            pipe.expire(key, per)
            pipe.execute()
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            
            # Get updated count
            current = redis_client.get(key)
            
            # If the response is a tuple (e.g., (jsonify(...), status_code)),
            # we need to modify the headers of the response object
            if isinstance(response, tuple) and len(response) >= 1:
                response_obj = response[0]
                # Convert to response if it's a dict
                if not hasattr(response_obj, 'headers'):
                    response_obj = jsonify(response_obj)
                    response = (response_obj,) + response[1:]
            else:
                # Convert to response if it's a dict
                if not hasattr(response, 'headers'):
                    response = jsonify(response)
            
            # Add rate limit headers
            remaining = max(0, limit - int(current))
            ttl = redis_client.ttl(key)
            
            response.headers['X-RateLimit-Limit'] = str(limit)
            response.headers['X-RateLimit-Remaining'] = str(remaining)
            response.headers['X-RateLimit-Reset'] = str(ttl)
            
            return response
            
        return decorated
    return decorator

@app.route('/api/public')
def public_endpoint():
    """Public endpoint without rate limiting."""
    return jsonify({'message': 'This is a public endpoint.'})

@app.route('/api/limited')
@rate_limit(limit=5, per=60)
def limited_endpoint():
    """Rate-limited endpoint (5 requests per minute)."""
    return jsonify({'message': 'This is a rate-limited endpoint.'})

if __name__ == '__main__':
    app.run(debug=True)
```

3. **Validate Input Data**:
```python
from flask import Flask, request, jsonify
from marshmallow import Schema, fields, validate, ValidationError

app = Flask(__name__)

class UserSchema(Schema):
    """Schema for validating user data."""
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    age = fields.Integer(validate=validate.Range(min=0, max=120))
    role = fields.String(validate=validate.OneOf(['user', 'admin', 'moderator']))

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a user with validated data."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate input data
    schema = UserSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'messages': err.messages}), 400
    
    # Process the validated data
    # In a real app, you would save to a database
    return jsonify({
        'message': 'User created successfully',
        'user': validated_data
    }), 201

if __name__ == '__main__':
    app.run(debug=True)
```

4. **Use API Keys for Third-Party Access**:
```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# In a real app, store API keys securely in a database
API_KEYS = {
    'abc123': {'client': 'Mobile App', 'rate_limit': 100},
    'xyz789': {'client': 'Partner API', 'rate_limit': 1000}
}

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key not in API_KEYS:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Add API client info to request
        request.api_client = API_KEYS[api_key]
        
        return f(*args, **kwargs)
    return decorated

@app.route('/api/data')
@require_api_key
def get_data():
    """Get data requiring a valid API key."""
    return jsonify({
        'message': f"Hello, {request.api_client['client']}!",
        'data': {'timestamp': time.time(), 'sample': 'data'}
    })

if __name__ == '__main__':
    app.run(debug=True)
```

5. **Implement CORS for Browser Security**:
```python
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow CORS for specific origins and methods
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://app.example.com", "https://admin.example.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/api/data')
def get_data():
    """Endpoint with CORS headers."""
    return jsonify({'message': 'This endpoint has CORS headers'})

if __name__ == '__main__':
    app.run(debug=True)
```

## 8. API Client Libraries

### 8.1 Creating a Python Client Library

```python
import requests
import json

class APIClient:
    """Client library for the Example API."""
    
    def __init__(self, base_url, api_key=None, timeout=10):
        """
        Initialize the API client.
        
        Args:
            base_url (str): The base URL of the API (e.g., https://api.example.com)
            api_key (str, optional): Your API key for authentication
            timeout (int, optional): Request timeout in seconds. Defaults to 10.
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
    
    def _get_headers(self):
        """Get headers for API requests."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            headers['X-API-Key'] = self.api_key
            
        return headers
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """
        Make an API request.
        
        Args:
            method (str): HTTP method (get, post, put, delete)
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            data (dict, optional): Request body data
            
        Returns:
            dict: Parsed API response
            
        Raises:
            requests.RequestException: If the request fails
            ValueError: If the response is not valid JSON
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        # Convert data to JSON if provided
        json_data = json.dumps(data) if data else None
        
        # Make the request
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            data=json_data,
            timeout=self.timeout
        )
        
        # Raise exception for HTTP errors
        response.raise_for_status()
        
        # Parse JSON response
        return response.json()
    
    # User endpoints
    def get_users(self, page=1, limit=20):
        """
        Get a list of users.
        
        Args:
            page (int, optional): Page number for pagination. Defaults to 1.
            limit (int, optional): Number of results per page. Defaults to 20.
            
        Returns:
            list: List of user objects
        """
        params = {'page': page, 'limit': limit}
        return self._make_request('get', '/api/users', params=params)
    
    def get_user(self, user_id):
        """
        Get a specific user by ID.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            dict: User object
            
        Raises:
            requests.HTTPError: If the user is not found (404)
        """
        return self._make_request('get', f'/api/users/{user_id}')
    
    def create_user(self, user_data):
        """
        Create a new user.
        
        Args:
            user_data (dict): User data including name and email
            
        Returns:
            dict: Created user object
        """
        return self._make_request('post', '/api/users', data=user_data)
    
    def update_user(self, user_id, user_data):
        """
        Update a user.
        
        Args:
            user_id (int): The user ID
            user_data (dict): User data to update
            
        Returns:
            dict: Updated user object
        """
        return self._make_request('put', f'/api/users/{user_id}', data=user_data)
    
    def delete_user(self, user_id):
        """
        Delete a user.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            None: Successful deletion returns None
        """
        return self._make_request('delete', f'/api/users/{user_id}')

# Example usage
if __name__ == '__main__':
    # Initialize the client
    client = APIClient(
        base_url='https://api.example.com',
        api_key='your_api_key_here'
    )
    
    try:
        # Get users
        users = client.get_users(page=1, limit=10)
        print(f"Found {len(users)} users")
        
        # Create a user
        new_user = client.create_user({
            'name': 'John Doe',
            'email': 'john@example.com'
        })
        print(f"Created user with ID: {new_user['id']}")
        
        # Get a specific user
        user = client.get_user(new_user['id'])
        print(f"User details: {user}")
        
        # Update the user
        updated_user = client.update_user(user['id'], {
            'name': 'John Smith'
        })
        print(f"Updated user: {updated_user}")
        
        # Delete the user
        client.delete_user(user['id'])
        print(f"Deleted user {user['id']}")
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
```

### 8.2 Documenting Your Client Library

```python
"""
Example API Client
=================

A Python client library for the Example API.

Basic Usage:
-----------

.. code-block:: python

    from example_api import APIClient
    
    # Initialize the client
    client = APIClient(
        base_url='https://api.example.com',
        api_key='your_api_key_here'
    )
    
    # Get users
    users = client.get_users(page=1, limit=10)
    
    # Create a user
    new_user = client.create_user({
        'name': 'John Doe',
        'email': 'john@example.com'
    })
    
    # Update a user
    client.update_user(new_user['id'], {'name': 'John Smith'})
    
    # Delete a user
    client.delete_user(new_user['id'])

Authentication:
--------------

This client supports API key authentication. Pass your API key when initializing the client:

.. code-block:: python

    client = APIClient(
        base_url='https://api.example.com',
        api_key='your_api_key_here'
    )

Rate Limiting:
-------------

The API has rate limits. When a rate limit is exceeded, the client will raise a requests.HTTPError
with status code 429. You should catch this exception and implement appropriate backoff logic.

Error Handling:
--------------

This client raises requests.RequestException for network or API errors:

.. code-block:: python

    try:
        user = client.get_user(123)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("User not found")
        else:
            print(f"API error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
"""

# Implementation follows...
```

## 9. Real-World API Examples and Best Practices

### 9.1 GitHub API Example

```python
import requests
import base64

class GitHubAPI:
    """Client for the GitHub API."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token=None):
        """
        Initialize the GitHub API client.
        
        Args:
            token (str, optional): GitHub personal access token
        """
        self.token = token
    
    def _get_headers(self):
        """Get headers for API requests."""
        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        
        if self.token:
            headers['Authorization'] = f"token {self.token}"
            
        return headers
    
    def get_user(self, username):
        """
        Get GitHub user information.
        
        Args:
            username (str): GitHub username
            
        Returns:
            dict: User information
        """
        url = f"{self.BASE_URL}/users/{username}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_repos(self, username, page=1, per_page=30):
        """
        Get repositories for a user.
        
        Args:
            username (str): GitHub username
            page (int, optional): Page number. Defaults to 1.
            per_page (int, optional): Results per page. Defaults to 30.
            
        Returns:
            list: Repository information
        """
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {
            'page': page,
            'per_page': per_page,
            'sort': 'updated'
        }
        
        response = requests.get(
            url, 
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_repo(self, name, description=None, private=False):
        """
        Create a new repository.
        
        Args:
            name (str): Repository name
            description (str, optional): Repository description
            private (bool, optional): Whether the repository is private
            
        Returns:
            dict: Repository information
        """
        if not self.token:
            raise ValueError("Authentication token required to create a repository")
        
        url = f"{self.BASE_URL}/user/repos"
        data = {
            'name': name,
            'private': private
        }
        
        if description:
            data['description'] = description
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_file_contents(self, repo_owner, repo_name, path, ref='main'):
        """
        Get file contents from a repository.
        
        Args:
            repo_owner (str): Repository owner username
            repo_name (str): Repository name
            path (str): File path within the repository
            ref (str, optional): Branch, tag, or commit. Defaults to 'main'.
            
        Returns:
            tuple: (decoded_content, file_metadata)
        """
        url = f"{self.BASE_URL}/repos/{repo_owner}/{repo_name}/contents/{path}"
        params = {'ref': ref}
        
        response = requests.get(
            url,
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        # Decode content if it's a file (not a directory)
        content = None
        if 'content' in data and data['encoding'] == 'base64':
            content = base64.b64decode(data['content']).decode('utf-8')
        
        return (content, data)

# Example usage
if __name__ == '__main__':
    # Initialize client with a token
    github = GitHubAPI(token='your_github_token_here')
    
    try:
        # Get user information
        user = github.get_user('octocat')
        print(f"User: {user['name']} ({user['login']})")
        print(f"Bio: {user['bio']}")
        
        # Get repositories
        repos = github.get_repos('octocat', per_page=5)
        print(f"\nRepositories ({len(repos)}):")
        for repo in repos:
            print(f"- {repo['name']}: {repo['description']}")
        
        # Get file contents
        content, metadata = github.get_file_contents(
            'octocat',
            'Hello-World',
            'README.md'
        )
        print(f"\nREADME.md:")
        print(content)
        
    except requests.exceptions.RequestException as e:
        print(f"GitHub API request failed: {e}")
```

### 9.2 Stripe API Example

```python
import stripe
import os

# Set your API key
stripe.api_key = os.environ.get('STRIPE_API_KEY', 'your_stripe_api_key')

def create_customer(email, name=None, metadata=None):
    """
    Create a new Stripe customer.
    
    Args:
        email (str): Customer email
        name (str, optional): Customer name
        metadata (dict, optional): Additional metadata
        
    Returns:
        stripe.Customer: The created customer object
    """
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata
        )
        return customer
    except stripe.error.StripeError as e:
        print(f"Stripe API error: {e}")
        raise

def create_payment_intent(amount, currency='usd', customer_id=None, metadata=None):
    """
    Create a payment intent.
    
    Args:
        amount (int): Amount in cents
        currency (str, optional): Currency code. Defaults to 'usd'.
        customer_id (str, optional): Stripe customer ID
        metadata (dict, optional): Additional metadata
        
    Returns:
        stripe.PaymentIntent: The created payment intent
    """
    try:
        payment_intent_data = {
            'amount': amount,
            'currency': currency,
            'metadata': metadata or {}
        }
        
        if customer_id:
            payment_intent_data['customer'] = customer_id
        
        payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
        return payment_intent
    except stripe.error.StripeError as e:
        print(f"Stripe API error: {e}")
        raise

def create_subscription(customer_id, price_id, metadata=None):
    """
    Create a subscription for a customer.
    
    Args:
        customer_id (str): Stripe customer ID
        price_id (str): Stripe price ID
        metadata (dict, optional): Additional metadata
        
    Returns:
        stripe.Subscription: The created subscription
    """
    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {'price': price_id},
            ],
            metadata=metadata
        )
        return subscription
    except stripe.error.StripeError as e:
        print(f"Stripe API error: {e}")
        raise

def handle_webhook_event(payload, signature, webhook_secret):
    """
    Handle a webhook event from Stripe.
    
    Args:
        payload (str): Raw webhook payload
        signature (str): Stripe signature header
        webhook_secret (str): Webhook signing secret
        
    Returns:
        dict: Processed event data
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        
        # Handle different event types
        event_type = event['type']
        event_data = event['data']['object']
        
        if event_type == 'payment_intent.succeeded':
            # Process successful payment
            payment_intent = event_data
            customer_id = payment_intent.get('customer')
            amount = payment_intent.get('amount')
            print(f"Payment of {amount/100} succeeded for customer {customer_id}")
            # Update your database, send confirmation email, etc.
            
        elif event_type == 'invoice.payment_succeeded':
            # Process successful invoice payment
            invoice = event_data
            customer_id = invoice.get('customer')
            amount_paid = invoice.get('amount_paid')
            print(f"Invoice payment of {amount_paid/100} succeeded for customer {customer_id}")
            # Update subscription status in your database
            
        elif event_type == 'customer.subscription.deleted':
            # Handle canceled subscription
            subscription = event_data
            customer_id = subscription.get('customer')
            print(f"Subscription {subscription.get('id')} canceled for customer {customer_id}")
            # Update your database, notify team, etc.
            
        # Return processed event data
        return {
            'type': event_type,
            'data': event_data,
            'processed': True
        }
        
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Webhook signature verification failed: {e}")
        raise
    except Exception as e:
        print(f"Webhook processing error: {e}")
        raise

# Example usage
if __name__ == '__main__':
    try:
        # Create a customer
        customer = create_customer(
            email='customer@example.com',
            name='Example Customer',
            metadata={'source': 'api_example'}
        )
        print(f"Created customer: {customer.id}")
        
        # Create a payment intent
        payment_intent = create_payment_intent(
            amount=2000,  # $20.00
            currency='usd',
            customer_id=customer.id,
            metadata={'order_id': '12345'}
        )
        print(f"Created payment intent: {payment_intent.id}")
        print(f"Client secret: {payment_intent.client_secret}")
        
        # Create a subscription (if you have a price ID)
        # subscription = create_subscription(
        #     customer_id=customer.id,
        #     price_id='price_12345',
        #     metadata={'plan': 'basic'}
        # )
        # print(f"Created subscription: {subscription.id}")
        
    except stripe.error.StripeError as e:
        print(f"Stripe API error: {e}")
```

## 10. Advanced API Topics

### 10.1 GraphQL APIs

```python
import requests

class GraphQLClient:
    """Simple GraphQL API client."""
    
    def __init__(self, url, headers=None):
        """
        Initialize the GraphQL client.
        
        Args:
            url (str): GraphQL endpoint URL
            headers (dict, optional): HTTP headers for requests
        """
        self.url = url
        self.headers = headers or {}
        
        # Add default content type if not provided
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = 'application/json'
    
    def execute(self, query, variables=None):
        """
        Execute a GraphQL query or mutation.
        
        Args:
            query (str): GraphQL query string
            variables (dict, optional): Variables for the query
            
        Returns:
            dict: Query response data
        """
        data = {'query': query}
        
        if variables:
            data['variables'] = variables
        
        response = requests.post(self.url, json=data, headers=self.headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for GraphQL errors
        if 'errors' in result:
            errors = result['errors']
            raise Exception(f"GraphQL errors: {errors}")
        
        return result.get('data')

# Example usage
if __name__ == '__main__':
    # GitHub GraphQL API example
    github_token = 'your_github_token'
    
    client = GraphQLClient(
        url='https://api.github.com/graphql',
        headers={'Authorization': f'Bearer {github_token}'}
    )
    
    # Query to get user information and repositories
    query = """
    query UserInfo($username: String!) {
        user(login: $username) {
            name
            bio
            websiteUrl
            repositories(first: 5, orderBy: {field: UPDATED_AT, direction: DESC}) {
                nodes {
                    name
                    description
                    stargazerCount
                    url
                }
            }
        }
    }
    """
    
    try:
        # Execute the query
        result = client.execute(query, variables={'username': 'octocat'})
        
        # Process the results
        user = result['user']
        print(f"Name: {user['name']}")
        print(f"Bio: {user['bio']}")
        
        repos = user['repositories']['nodes']
        print("\nRepositories:")
        for repo in repos:
            print(f"- {repo['name']}: {repo['description']}")
            print(f"  Stars: {repo['stargazerCount']}, URL: {repo['url']}")
        
    except Exception as e:
        print(f"Error: {e}")
```

### 10.2 API Versioning Strategies

```python
from flask import Flask, Blueprint, jsonify, request

app = Flask(__name__)

# Method 1: URL Path Versioning
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

@api_v1.route('/users/<int:user_id>')
def get_user_v1(user_id):
    """Get user (API v1)."""
    # v1 implementation
    return jsonify({
        'id': user_id,
        'name': f"User {user_id}",
        'email': f"user{user_id}@example.com"
    })

@api_v2.route('/users/<int:user_id>')
def get_user_v2(user_id):
    """Get user (API v2)."""
    # v2 implementation with additional fields
    return jsonify({
        'id': user_id,
        'name': f"User {user_id}",
        'email': f"user{user_id}@example.com",
        'created_at': '2023-01-01T00:00:00Z'
    })

# Method 2: Content Negotiation
@app.route('/api/users/<int:user_id>')
def get_user_content_negotiation(user_id):
    """Get user with content negotiation versioning."""
    # Get version from Accept header
    accept_header = request.headers.get('Accept', '')
    
    if 'application/vnd.example.v2+json' in accept_header:
        # v2 implementation
        return jsonify({
            'id': user_id,
            'name': f"User {user_id}",
            'email': f"user{user_id}@example.com",
            'created_at': '2023-01-01T00:00:00Z'
        })
    else:
        # v1 implementation (default)
        return jsonify({
            'id': user_id,
            'name': f"User {user_id}",
            'email': f"user{user_id}@example.com"
        })

# Method 3: Custom Request Header
@app.route('/api/users/<int:user_id>')
def get_user_header_version(user_id):
    """Get user with header versioning."""
    # Get version from custom header
    api_version = request.headers.get('X-API-Version', '1.0')
    
    if api_version == '2.0':
        # v2 implementation
        return jsonify({
            'id': user_id,
            'name': f"User {user_id}",
            'email': f"user{user_id}@example.com",
            'created_at': '2023-01-01T00:00:00Z'
        })
    else:
        # v1 implementation
        return jsonify({
            'id': user_id,
            'name': f"User {user_id}",
            'email': f"user{user_id}@example.com"
        })

# Method 4: Query Parameter
@app.route('/api/users/<int:user_id>')
def get_user_query_version(user_id):
    """Get user with query parameter versioning."""
    # Get version from query parameter
    api_version = request.args.get('version', '1.0')
    
    if api_version == '2.0':
        # v2 implementation
        return jsonify({
            'id': user_id,
            'name': f"User {user_id}",
            'email': f"user{user_id}@example.com",
            'created_at': '2023-01-01T00:00:00Z'
        })
    else:
        # v1 implementation
        return jsonify({
            'id': user_id,
            'name': f"User {user_id}",
            'email': f"user{user_id}@example.com"
        })

# Register blueprints for URL path versioning
app.register_blueprint(api_v1)
app.register_blueprint(api_v2)

if __name__ == '__main__':
    app.run(debug=True)
```

### 10.3 API Pagination and Filtering

```python
from flask import Flask, jsonify, request
import math

app = Flask(__name__)

# Sample data
items = [{'id': i, 'name': f'Item {i}', 'category': f'Category {i % 3 + 1}'} for i in range(1, 101)]

@app.route('/api/items')
def get_items():
    """Get items with pagination and filtering."""
    # Parse query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 100)  # Limit maximum per_page
    category = request.args.get('category')
    search = request.args.get('search')
    
    # Apply filters
    filtered_items = items
    
    if category:
        filtered_items = [item for item in filtered_items if item['category'] == category]
    
    if search:
        search_lower = search.lower()
        filtered_items = [
            item for item in filtered_items 
            if search_lower in item['name'].lower()
        ]
    
    # Calculate pagination
    total_items = len(filtered_items)
    total_pages = math.ceil(total_items / per_page)
    
    # Ensure page is within bounds
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    
    # Get current page items
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_page_items = filtered_items[start_idx:end_idx]
    
    # Construct pagination links
    base_url = request.base_url
    query_params = request.args.copy()
    
    def get_page_url(page_num):
        query_params['page'] = page_num
        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        return f"{base_url}?{query_string}"
    
    # Build response
    response = {
        'items': current_page_items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'links': {
                'self': get_page_url(page),
                'first': get_page_url(1),
                'last': get_page_url(total_pages) if total_pages > 0 else None,
                'next': get_page_url(page + 1) if page < total_pages else None,
                'prev': get_page_url(page - 1) if page > 1 else None
            }
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
```

### 10.4 API Throttling and Rate Limiting

```python
from flask import Flask, jsonify, request
import time
import threading
from functools import wraps

app = Flask(__name__)

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self):
        self.rate_limits = {}
        self.lock = threading.Lock()
    
    def is_rate_limited(self, key, limit, period):
        """
        Check if a key is rate limited.
        
        Args:
            key (str): Rate limit key (e.g., IP address, API key)
            limit (int): Maximum number of requests
            period (int): Time period in seconds
            
        Returns:
            tuple: (is_limited, remaining, reset_time)
        """
        now = time.time()
        
        with self.lock:
            # Get or create rate limit data for the key
            if key not in self.rate_limits:
                self.rate_limits[key] = {
                    'reset_time': now + period,
                    'remaining': limit,
                    'count': 0
                }
            
            data = self.rate_limits[key]
            
            # Reset if period has elapsed
            if now > data['reset_time']:
                data['reset_time'] = now + period
                data['remaining'] = limit
                data['count'] = 0
            
            # Check limit
            is_limited = data['remaining'] <= 0
            
            # Update remaining if not limited
            if not is_limited:
                data['remaining'] -= 1
                data['count'] += 1
            
            return (
                is_limited,
                data['remaining'],
                data['reset_time']
            )

# Create a rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit, period):
    """
    Rate limiting decorator.
    
    Args:
        limit (int): Maximum number of requests
        period (int): Time period in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use client IP address as rate limit key
            # In production, you might use API key or user ID
            key = request.remote_addr
            
            # Check rate limit
            is_limited, remaining, reset_time = rate_limiter.is_rate_limited(
                key, limit, period
            )
            
            # Set rate limit headers
            response_headers = {
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Remaining': str(max(0, remaining)),
                'X-RateLimit-Reset': str(int(reset_time))
            }
            
            if is_limited:
                # Return rate limit error response
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Try again after {int(reset_time - time.time())} seconds'
                })
                response.status_code = 429
                
                # Add headers to the response
                for key, value in response_headers.items():
                    response.headers[key] = value
                
                return response
            
            # Call the original function
            response = f(*args, **kwargs)
            
            # Add rate limit headers to the response
            if isinstance(response, tuple) and len(response) >= 1:
                # For tuple responses (e.g., (jsonify(...), status_code))
                response_obj = response[0]
                for key, value in response_headers.items():
                    response_obj.headers[key] = value
            else:
                # For direct responses
                for key, value in response_headers.items():
                    response.headers[key] = value
            
            return response
        
        return decorated_function
    
    return decorator

# Example API endpoints with rate limiting
@app.route('/api/public')
def public_endpoint():
    """Public endpoint without rate limiting."""
    return jsonify({'message': 'This is a public endpoint.'})

@app.route('/api/basic')
@rate_limit(limit=10, period=60)  # 10 requests per minute
def basic_endpoint():
    """Rate-limited endpoint (10 requests per minute)."""
    return jsonify({'message': 'This is a rate-limited endpoint.'})

@app.route('/api/limited')
@rate_limit(limit=3, period=60)  # 3 requests per minute
def limited_endpoint():
    """Severely rate-limited endpoint (3 requests per minute)."""
    return jsonify({'message': 'This is a severely rate-limited endpoint.'})

if __name__ == '__main__':
    app.run(debug=True)
```

## 11. Conclusion

### 11.1 API Documentation Best Practices Summary

1. **Be comprehensive**: Document all endpoints, parameters, and responses
2. **Use examples**: Provide clear examples for common use cases
3. **Be consistent**: Use consistent formatting and terminology
4. **Keep it up-to-date**: Update documentation when APIs change
5. **Include error handling**: Document possible errors and how to handle them
6. **Document authentication**: Clearly explain authentication requirements
7. **Provide both reference and guides**: Different types of documentation serve different purposes
8. **Use tools**: Leverage documentation generation tools like Sphinx and OpenAPI

### 11.2 API Implementation Best Practices Summary

1. **Follow RESTful principles**: Use appropriate HTTP methods and status codes
2. **Version your APIs**: Allow for evolution without breaking existing clients
3. **Use consistent naming**: Apply consistent naming conventions
4. **Implement proper error handling**: Return helpful error messages
5. **Secure your APIs**: Use HTTPS, authentication, and input validation
6. **Rate limit appropriately**: Protect your services from abuse
7. **Implement pagination**: For large data sets
8. **Write comprehensive tests**: Unit tests, integration tests, and load tests
9. **Monitor API usage**: Track performance and errors
10. **Create client libraries**: Make it easier for developers to use your API

### 11.3 Further Learning Resources

1. **Books**:
   - "RESTful Web APIs" by Leonard Richardson and Mike Amundsen
   - "API Design Patterns" by JJ Geewax
   - "Designing Web APIs" by Brenda Jin, Saurabh Sahni, and Amir Shevat

2. **Online Documentation**:
   - [Flask Documentation](https://flask.palletsprojects.com/)
   - [Django REST Framework](https://www.django-rest-framework.org/)
   - [OpenAPI Specification](https://swagger.io/specification/)
   - [Sphinx Documentation](https://www.sphinx-doc.org/)

3. **Courses and Tutorials**:
   - Real Python's API tutorials
   - Pluralsight's "Designing RESTful Web APIs"
   - Udemy's "RESTful API with Python Flask"

By following these best practices and continuously learning, you'll be able to create well-documented, secure, and user-friendly APIs in Python.