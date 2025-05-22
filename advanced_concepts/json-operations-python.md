# Comprehensive Guide to JSON Operations in Python

## 1. Introduction to JSON

JSON (JavaScript Object Notation) is a lightweight data interchange format that is easy for humans to read and write and easy for machines to parse and generate. It is based on a subset of JavaScript and is commonly used for transmitting data in web applications.

In Python, the built-in `json` module provides methods to work with JSON data, allowing conversion between Python objects and JSON formats.

## 2. Core JSON Operations

Python's `json` module offers four primary functions for working with JSON:

| Function | Description |
|----------|-------------|
| `json.load()` | Reads JSON data from a file |
| `json.loads()` | Parses JSON from a string |
| `json.dump()` | Writes JSON data to a file |
| `json.dumps()` | Converts a Python object to a JSON string |

Let's explore each of these operations in detail.

## 3. Reading JSON Data

### 3.1 Reading JSON from a File (`json.load`)

Use `json.load()` to read JSON data from a file and convert it to a Python object:

```python
import json

# Opening a file and loading JSON data
with open('data.json', 'r') as file:
    data = json.load(file)  # Converts JSON file contents to a Python object

# Now you can work with data as a Python dictionary or list
print(data)
```

The resulting Python object will be:
- A dictionary if the JSON starts with `{}`
- A list if the JSON starts with `[]`
- A simple type (string, number, boolean, null) otherwise

### 3.2 Parsing JSON from a String (`json.loads`)

Use `json.loads()` to parse a JSON string into a Python object:

```python
import json

# JSON string
json_string = '{"name": "John", "age": 30, "city": "New York"}'

# Parse the JSON string
data = json.loads(json_string)  # 's' stands for "string"

print(data['name'])  # Output: John
print(data['age'])   # Output: 30
```

Remember: `json.loads()` is for strings, while `json.load()` is for file objects.

## 4. Writing JSON Data

### 4.1 Writing JSON to a File (`json.dump`)

Use `json.dump()` to write a Python object to a file as JSON:

```python
import json

# Python dictionary
user = {
    'name': 'Alice',
    'age': 25,
    'is_active': True,
    'interests': ['reading', 'hiking', 'photography']
}

# Write to a JSON file
with open('user.json', 'w') as file:
    json.dump(user, file, indent=2)  # The indent parameter makes the output pretty-printed
```

This creates a file called `user.json` with formatted JSON content.

### 4.2 Converting Python to JSON String (`json.dumps`)

Use `json.dumps()` to convert a Python object to a JSON-formatted string:

```python
import json

# Python dictionary
user = {
    'name': 'Bob',
    'age': 32,
    'is_active': False
}

# Convert to JSON string
json_string = json.dumps(user, indent=2)
print(json_string)
```

Output:
```json
{
  "name": "Bob",
  "age": 32,
  "is_active": false
}
```

## 5. JSON Conversion Table

Python types are converted to JSON according to this mapping:

| Python Type | JSON Type |
|-------------|-----------|
| dict | object |
| list, tuple | array |
| str | string |
| int, float | number |
| True | true |
| False | false |
| None | null |

## 6. Common Parameters

Both `json.dump()` and `json.dumps()` accept these useful parameters:

### 6.1 `indent`

Makes the output pretty-printed with a specified indentation level:

```python
json.dumps(data, indent=4)  # Use 4 spaces for indentation
```

### 6.2 `ensure_ascii`

By default (True), non-ASCII characters are escaped. Set to False to keep them as-is:

```python
data = {"name": "André"}
json.dumps(data)                     # Output: {"name": "Andr\u00e9"}
json.dumps(data, ensure_ascii=False) # Output: {"name": "André"}
```

### 6.3 `sort_keys`

Sorts dictionary keys alphabetically:

```python
data = {"c": 3, "a": 1, "b": 2}
json.dumps(data)                # Output: {"c": 3, "a": 1, "b": 2}
json.dumps(data, sort_keys=True) # Output: {"a": 1, "b": 2, "c": 3}
```

### 6.4 `separators`

Customizes separators between items and key-value pairs:

```python
# Default separators are (', ', ': ')
json.dumps(data, separators=(',', ':'))  # More compact, no spaces
```

### 6.5 `default`

Specifies a function to convert non-serializable objects:

```python
import json
from datetime import datetime

data = {'timestamp': datetime.now()}

# Without a default function, this would raise TypeError
# as datetime objects are not JSON serializable

def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    # Raise TypeError for objects that can't be serialized
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

json_string = json.dumps(data, default=convert_datetime)
print(json_string)  # Output: {"timestamp": "2025-05-21T10:23:14.123456"}
```

## 7. Complete Example Using Multiple Parameters

```python
import json
from datetime import datetime

data = {
    'name': 'Charlie',
    'created_at': datetime.now(),
    'items': ['a', 'b', 'c'],
    'details': {
        'country': 'Canada',
        'language': 'English'
    }
}

# Custom converter for non-JSON types
def convert_to_json(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Convert with multiple parameters
json_string = json.dumps(
    data,
    indent=4,               # Pretty print with 4 spaces
    ensure_ascii=False,     # Allow non-ASCII characters
    sort_keys=True,         # Sort dictionary keys alphabetically
    separators=(',', ': '), # Custom separators
    default=convert_to_json # Custom converter for non-serializable types
)

print(json_string)
```

## 8. Loading JSON with Custom Object Hooks

You can customize how JSON objects are loaded into Python using an `object_hook`:

```python
import json
from datetime import datetime

json_string = '{"name": "Alice", "timestamp": "2025-05-21T10:30:00"}'

def datetime_parser(json_dict):
    for key, value in json_dict.items():
        if key == "timestamp" and isinstance(value, str):
            try:
                json_dict[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return json_dict

data = json.loads(json_string, object_hook=datetime_parser)
print(type(data["timestamp"]))  # Output: <class 'datetime.datetime'>
```

## 9. Handling JSON Errors

### 9.1 JSONDecodeError

The most common error when parsing JSON is `JSONDecodeError`:

```python
import json

# Invalid JSON string (missing quotes around key)
invalid_json = '{name: "John"}'

try:
    data = json.loads(invalid_json)
except json.JSONDecodeError as e:
    print(f"JSON parsing failed: {e}")
    print(f"Error at position {e.pos}, line {e.lineno}, column {e.colno}")
```

### 9.2 TypeError for Non-Serializable Objects

When trying to serialize objects that aren't JSON-serializable:

```python
import json
from datetime import datetime

try:
    # This will fail because datetime is not JSON serializable
    json.dumps({"timestamp": datetime.now()})
except TypeError as e:
    print(f"Serialization error: {e}")
    # Output: Serialization error: Object of type datetime is not JSON serializable
```

## 10. Working with Large JSON Files

For very large JSON files, consider using streaming parsers:

```python
import json

def process_large_json(filename):
    # Process a large JSON file line by line (assuming JSON Lines format)
    with open(filename, 'r') as file:
        for line in file:
            try:
                item = json.loads(line.strip())
                # Process each item here
                process_item(item)
            except json.JSONDecodeError:
                print(f"Error parsing line: {line}")
```

For more complex streaming needs, consider third-party libraries like `ijson`.

## 11. Best Practices

### 11.1 Always Use Context Managers for File Operations

```python
# Good practice
with open('data.json', 'r') as file:
    data = json.load(file)

# Avoid this (file might not be closed properly)
file = open('data.json', 'r')
data = json.load(file)
file.close()
```

### 11.2 Validate JSON Schema

For complex applications, consider validating JSON against a schema:

```python
import json
import jsonschema

# Define a schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number", "minimum": 0},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "email"]
}

data = json.loads('{"name": "John", "age": 30, "email": "john@example.com"}')

try:
    jsonschema.validate(instance=data, schema=schema)
    print("JSON is valid")
except jsonschema.exceptions.ValidationError as e:
    print(f"Invalid JSON: {e}")
```

### 11.3 Use Pretty Printing During Development

```python
# During development, use indentation for readability
with open('debug_output.json', 'w') as file:
    json.dump(data, file, indent=2, sort_keys=True)

# In production, save space with compact output
with open('production_output.json', 'w') as file:
    json.dump(data, file, separators=(',', ':'))
```

## 12. Real-World Examples

### 12.1 Reading Configuration

```python
def load_config():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        # Create a default config if file doesn't exist
        default_config = {
            "api_key": "",
            "debug_mode": False,
            "max_retries": 3
        }
        with open('config.json', 'w') as file:
            json.dump(default_config, file, indent=2)
        return default_config
    except json.JSONDecodeError:
        print("Config file is corrupted, using defaults")
        return {"api_key": "", "debug_mode": True, "max_retries": 3}
```

### 12.2 API Communication

```python
import json
import requests

def fetch_user(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    
    if response.status_code == 200:
        try:
            user_data = response.json()  # Uses json.loads() internally
            return user_data
        except json.JSONDecodeError:
            print("Invalid JSON response from API")
            return None
    else:
        print(f"API error: {response.status_code}")
        return None

def create_user(user_data):
    # Convert Python dict to JSON string
    user_json = json.dumps(user_data)
    
    # Send the JSON data
    response = requests.post(
        "https://api.example.com/users",
        data=user_json,
        headers={"Content-Type": "application/json"}
    )
    
    return response.status_code == 201
```

### 12.3 Data Export/Import

```python
def export_records(records, filename):
    """Export records to a JSON file."""
    with open(filename, 'w') as file:
        json.dump({
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "record_count": len(records),
            "records": records
        }, file, indent=2, default=json_serializer)
    
    print(f"Exported {len(records)} records to {filename}")

def import_records(filename):
    """Import records from a JSON file."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        
        version = data.get("version", "unknown")
        if version != "1.0":
            print(f"Warning: Importing data with version {version}")
        
        return data.get("records", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Import failed: {e}")
        return []
```

## 13. Performance Considerations

- `json.dumps()` and `json.loads()` process the entire data in memory, which may be inefficient for very large datasets
- For better performance with large files, consider using `ujson` or `orjson` libraries
- When dealing with huge datasets, consider using a streaming approach or a database instead of JSON files
- Custom serializers and deserializers can have performance impacts; profile your code if performance is critical

## 14. Summary

The Python `json` module provides a simple yet powerful interface for working with JSON data:

- Use `json.load()` and `json.loads()` to read JSON data
- Use `json.dump()` and `json.dumps()` to write JSON data
- Various parameters allow you to control the formatting and behavior
- Custom serializers and deserializers enable working with complex Python objects
- Always use error handling to manage JSON parsing or serialization failures
- For large datasets, consider streaming approaches or alternative libraries

By mastering these functions and their parameters, you can effectively work with JSON data in your Python applications, whether for configuration files, API communication, or data storage.
