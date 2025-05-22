# Python Design Patterns and Architecture

## Introduction

Design patterns are reusable solutions to common problems that arise during software design. They represent best practices that have evolved over time as developers faced and solved similar design challenges. Understanding design patterns helps you write more maintainable, flexible, and scalable code.

This guide covers:
1. Core design pattern concepts
2. Python-specific implementations
3. Architectural patterns for larger applications
4. Practical examples and use cases

## Design Pattern Categories

Design patterns generally fall into three categories:

### 1. Creational Patterns
Patterns that deal with object creation mechanisms, trying to create objects in a manner suitable to the situation.

### 2. Structural Patterns
Patterns that focus on the composition of classes or objects to form larger structures while keeping these structures flexible and efficient.

### 3. Behavioral Patterns
Patterns that are concerned with algorithms and the assignment of responsibilities between objects.

## Common Python Design Patterns

### Creational Patterns

#### 1. Singleton Pattern

The Singleton pattern ensures a class has only one instance and provides a global point of access to it.

```python
class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

# Usage
singleton1 = Singleton()
singleton2 = Singleton()
print(singleton1 is singleton2)  # True - both variables reference the same instance
```

A more Pythonic approach using a module:

```python
# singleton.py
value = "I'm a singleton value"

def get_value():
    return value

# Using it
import singleton
print(singleton.value)  # Access the singleton value
```

**When to use**: When exactly one instance of a class is needed, such as for database connections, configuration managers, or logging systems.

#### 2. Factory Method Pattern

The Factory Method pattern provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created.

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    def create_animal(self, animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# Usage
factory = AnimalFactory()
dog = factory.create_animal("dog")
print(dog.speak())  # Woof!
```

**When to use**: When a class cannot anticipate the class of objects it must create, or when a class wants its subclasses to specify the objects it creates.

#### 3. Builder Pattern

The Builder pattern separates the construction of a complex object from its representation so that the same construction process can create different representations.

```python
class Computer:
    def __init__(self):
        self.cpu = None
        self.ram = None
        self.storage = None
        self.gpu = None
    
    def __str__(self):
        return f"Computer specs: CPU={self.cpu}, RAM={self.ram}GB, Storage={self.storage}GB, GPU={self.gpu}"

class ComputerBuilder:
    def __init__(self):
        self.computer = Computer()
    
    def set_cpu(self, cpu):
        self.computer.cpu = cpu
        return self
    
    def set_ram(self, ram):
        self.computer.ram = ram
        return self
    
    def set_storage(self, storage):
        self.computer.storage = storage
        return self
    
    def set_gpu(self, gpu):
        self.computer.gpu = gpu
        return self
    
    def build(self):
        return self.computer

# Usage - creating a gaming computer
gaming_pc = (ComputerBuilder()
             .set_cpu("Intel i9")
             .set_ram(32)
             .set_storage(1000)
             .set_gpu("RTX 3080")
             .build())

print(gaming_pc)  # Computer specs: CPU=Intel i9, RAM=32GB, Storage=1000GB, GPU=RTX 3080
```

**When to use**: When the construction of an object is complex and requires multiple steps, or when different representations of an object need to be created using the same construction process.

### Structural Patterns

#### 1. Adapter Pattern

The Adapter pattern allows classes with incompatible interfaces to work together by wrapping an instance of one class with a new adapter class that implements the interface expected by clients.

```python
# Existing class with incompatible interface
class OldSystem:
    def old_operation(self, data):
        return f"Old system processed: {data}"

# Target interface
class NewInterface:
    def new_operation(self, data):
        pass

# Adapter
class SystemAdapter(NewInterface):
    def __init__(self, old_system):
        self.old_system = old_system
    
    def new_operation(self, data):
        # Call the old system using the new interface
        return self.old_system.old_operation(data)

# Client code
def client_code(new_system, data):
    return new_system.new_operation(data)

# Usage
old_system = OldSystem()
adapter = SystemAdapter(old_system)
result = client_code(adapter, "Important data")
print(result)  # Old system processed: Important data
```

**When to use**: When you need to use an existing class with an incompatible interface, or when you need to use a class that doesn't fit your system's architecture.

#### 2. Decorator Pattern

The Decorator pattern allows behavior to be added to individual objects, either statically or dynamically, without affecting the behavior of other objects from the same class.

Python has built-in support for decorators, making this pattern very natural to implement:

```python
# Function decorators
def log_execution(func):
    def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished executing {func.__name__}")
        return result
    return wrapper

@log_execution
def add(a, b):
    return a + b

# Usage
result = add(5, 3)
# Output:
# Executing add
# Finished executing add
```

Using classes as decorators:

```python
# Component interface
class Component:
    def operation(self):
        pass

# Concrete component
class ConcreteComponent(Component):
    def operation(self):
        return "Basic operation"

# Base decorator
class Decorator(Component):
    def __init__(self, component):
        self._component = component
    
    def operation(self):
        return self._component.operation()

# Concrete decorators
class ConcreteDecoratorA(Decorator):
    def operation(self):
        return f"DecoratorA({super().operation()})"

class ConcreteDecoratorB(Decorator):
    def operation(self):
        return f"DecoratorB({super().operation()})"

# Usage
component = ConcreteComponent()
decorated_a = ConcreteDecoratorA(component)
decorated_b = ConcreteDecoratorB(decorated_a)

print(decorated_b.operation())  # DecoratorB(DecoratorA(Basic operation))
```

**When to use**: When you need to add responsibilities to objects dynamically, or when extension by subclassing is impractical.

#### 3. Facade Pattern

The Facade pattern provides a unified interface to a set of interfaces in a subsystem, making the subsystem easier to use.

```python
class CPU:
    def process(self):
        return "Processing data..."

class Memory:
    def load(self):
        return "Loading data into memory..."

class HardDrive:
    def read(self):
        return "Reading data from hard drive..."

# Facade
class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()
    
    def start(self):
        steps = [
            self.hard_drive.read(),
            self.memory.load(),
            self.cpu.process()
        ]
        return "\n".join(steps)

# Usage
computer = ComputerFacade()
print(computer.start())
# Output:
# Reading data from hard drive...
# Loading data into memory...
# Processing data...
```

**When to use**: When you need to provide a simple interface to a complex subsystem, or when you want to decouple a subsystem from its clients.

### Behavioral Patterns

#### 1. Observer Pattern

The Observer pattern defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

```python
class Subject:
    def __init__(self):
        self._observers = []
        self._state = None
    
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, state):
        self._state = state
        self.notify()

class Observer:
    def update(self, subject):
        pass

class ConcreteObserverA(Observer):
    def update(self, subject):
        print(f"ObserverA: Reacted to the state change to {subject.state}")

class ConcreteObserverB(Observer):
    def update(self, subject):
        print(f"ObserverB: Reacted to the state change to {subject.state}")

# Usage
subject = Subject()

observer_a = ConcreteObserverA()
observer_b = ConcreteObserverB()

subject.attach(observer_a)
subject.attach(observer_b)

subject.state = "State 1"
# Output:
# ObserverA: Reacted to the state change to State 1
# ObserverB: Reacted to the state change to State 1

subject.detach(observer_a)
subject.state = "State 2"
# Output:
# ObserverB: Reacted to the state change to State 2
```

**When to use**: When changes to one object require changing others, and you don't know how many objects need to be changed, or when an object should be able to notify other objects without making assumptions about them.

#### 2. Strategy Pattern

The Strategy pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable. It lets the algorithm vary independently from clients that use it.

```python
from abc import ABC, abstractmethod

# Strategy interface
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass

# Concrete strategies
class QuickSort(SortStrategy):
    def sort(self, data):
        print("Sorting using quick sort")
        # Implementation omitted
        return sorted(data)

class MergeSort(SortStrategy):
    def sort(self, data):
        print("Sorting using merge sort")
        # Implementation omitted
        return sorted(data)

class BubbleSort(SortStrategy):
    def sort(self, data):
        print("Sorting using bubble sort")
        # Implementation omitted
        return sorted(data)

# Context
class Sorter:
    def __init__(self, strategy=None):
        self._strategy = strategy
    
    @property
    def strategy(self):
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy):
        self._strategy = strategy
    
    def sort(self, data):
        if not self._strategy:
            raise ValueError("Sorting strategy not set")
        return self._strategy.sort(data)

# Usage
data = [5, 3, 8, 1, 2]

sorter = Sorter()
sorter.strategy = QuickSort()
print(sorter.sort(data))  # Quick sort result

sorter.strategy = MergeSort()
print(sorter.sort(data))  # Merge sort result
```

**When to use**: When you want to define a family of algorithms, encapsulate each one, and make them interchangeable, or when you need to vary the algorithm according to the situation.

#### 3. Command Pattern

The Command pattern encapsulates a request as an object, thereby allowing for parameterization of clients with different requests, queuing of requests, and logging of the requests.

```python
from abc import ABC, abstractmethod

# Command interface
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

# Concrete commands
class LightOnCommand(Command):
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        self.light.turn_on()

class LightOffCommand(Command):
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        self.light.turn_off()

# Receiver
class Light:
    def turn_on(self):
        print("Light is now ON")
    
    def turn_off(self):
        print("Light is now OFF")

# Invoker
class RemoteControl:
    def __init__(self):
        self.command = None
    
    def set_command(self, command):
        self.command = command
    
    def press_button(self):
        if self.command:
            self.command.execute()

# Usage
light = Light()
light_on = LightOnCommand(light)
light_off = LightOffCommand(light)

remote = RemoteControl()

# Turn on the light
remote.set_command(light_on)
remote.press_button()  # Light is now ON

# Turn off the light
remote.set_command(light_off)
remote.press_button()  # Light is now OFF
```

**When to use**: When you want to parameterize objects with operations, queue operations, or support undoable operations.

## Application Architecture Patterns

Beyond individual design patterns, understanding larger architectural patterns is crucial for building robust applications.

### 1. Model-View-Controller (MVC)

MVC separates an application into three main components:
- **Model**: Data and business logic
- **View**: User interface
- **Controller**: Handles user input and updates model/view

```python
# Model
class UserModel:
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_id, name, email):
        self.users[user_id] = {"name": name, "email": email}
    
    def get_user(self, user_id):
        return self.users.get(user_id)
    
    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]

# View
class UserView:
    def show_user_details(self, user_data):
        if user_data:
            print(f"User: {user_data['name']}")
            print(f"Email: {user_data['email']}")
        else:
            print("User not found")
    
    def show_error(self, message):
        print(f"Error: {message}")

# Controller
class UserController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def add_user(self, user_id, name, email):
        try:
            self.model.add_user(user_id, name, email)
        except Exception as e:
            self.view.show_error(str(e))
    
    def show_user(self, user_id):
        try:
            user = self.model.get_user(user_id)
            self.view.show_user_details(user)
        except Exception as e:
            self.view.show_error(str(e))
    
    def delete_user(self, user_id):
        try:
            self.model.delete_user(user_id)
        except Exception as e:
            self.view.show_error(str(e))

# Usage
model = UserModel()
view = UserView()
controller = UserController(model, view)

controller.add_user(1, "John Doe", "john@example.com")
controller.show_user(1)
```

### 2. Repository Pattern

The Repository pattern separates the logic that retrieves data from storage from the business logic that acts on the data.

```python
from abc import ABC, abstractmethod

# Repository interface
class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id):
        pass
    
    @abstractmethod
    def save(self, user):
        pass
    
    @abstractmethod
    def delete(self, user_id):
        pass

# Concrete repository implementation (using a dictionary as a mock database)
class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users = {}
    
    def find_by_id(self, user_id):
        return self.users.get(user_id)
    
    def save(self, user):
        self.users[user.id] = user
        return user
    
    def delete(self, user_id):
        if user_id in self.users:
            del self.users[user_id]

# User model
class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

# Service that uses the repository
class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def get_user(self, user_id):
        return self.user_repository.find_by_id(user_id)
    
    def create_user(self, id, name, email):
        user = User(id, name, email)
        return self.user_repository.save(user)
    
    def delete_user(self, user_id):
        self.user_repository.delete(user_id)

# Usage
repository = InMemoryUserRepository()
user_service = UserService(repository)

user_service.create_user(1, "John Doe", "john@example.com")
user = user_service.get_user(1)
print(f"User: {user.name}, Email: {user.email}")
```

### 3. Dependency Injection

Dependency Injection is a technique where one object supplies the dependencies of another object, making the code more modular and testable.

```python
# Without dependency injection
class UserService:
    def __init__(self):
        self.user_repository = InMemoryUserRepository()  # Tightly coupled
    
    def get_user(self, user_id):
        return self.user_repository.find_by_id(user_id)

# With dependency injection
class UserService:
    def __init__(self, user_repository):  # Dependency injected
        self.user_repository = user_repository
    
    def get_user(self, user_id):
        return self.user_repository.find_by_id(user_id)

# Usage with dependency injection
repository = InMemoryUserRepository()
user_service = UserService(repository)

# For testing, we can inject a mock repository
class MockUserRepository(UserRepository):
    def find_by_id(self, user_id):
        return User(user_id, "Mock User", "mock@example.com")
    
    def save(self, user):
        return user
    
    def delete(self, user_id):
        pass

# Testing with mock repository
mock_repository = MockUserRepository()
test_service = UserService(mock_repository)
```

### 4. Service Layer Pattern

The Service Layer pattern defines an application's boundary and its set of available operations from the perspective of interfacing client layers.

```python
# Entity
class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

# Repository
class UserRepository:
    def __init__(self):
        self.users = {}
    
    def find_by_id(self, user_id):
        return self.users.get(user_id)
    
    def save(self, user):
        self.users[user.id] = user
        return user

# Service layer
class UserService:
    def __init__(self, user_repository, email_service):
        self.user_repository = user_repository
        self.email_service = email_service
    
    def register_user(self, id, name, email):
        # Business logic
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")
        
        # Create and save user
        user = User(id, name, email)
        saved_user = self.user_repository.save(user)
        
        # Send welcome email
        self.email_service.send_welcome_email(email, name)
        
        return saved_user
    
    def _is_valid_email(self, email):
        # Email validation logic
        return '@' in email

# Email service
class EmailService:
    def send_welcome_email(self, email, name):
        print(f"Sending welcome email to {name} at {email}")

# Usage
user_repository = UserRepository()
email_service = EmailService()
user_service = UserService(user_repository, email_service)

try:
    user = user_service.register_user(1, "John Doe", "john@example.com")
    print(f"User registered: {user.name}")
except ValueError as e:
    print(f"Error: {str(e)}")
```

## Best Practices for Python Architecture

1. **Follow the Single Responsibility Principle (SRP)**
   - Each class should have only one reason to change
   - Keep classes focused on a single concern

2. **Use Dependency Injection**
   - Inject dependencies rather than creating them inside classes
   - Makes testing easier and reduces coupling

3. **Keep the Core Domain Logic Separate**
   - Isolate business logic from infrastructure concerns
   - Use interfaces to define boundaries between layers

4. **Favor Composition Over Inheritance**
   - Compose objects to gain functionality rather than inheriting
   - Leads to more flexible and maintainable code

5. **Use Type Hints for Better Documentation**
   - Python's type hints improve code readability and IDE support
   ```python
   def get_user(user_id: int) -> User:
       # Implementation
   ```

6. **Write Tests First**
   - Test-driven development helps define clear interfaces
   - Ensures your architecture is testable

7. **Use Dataclasses for Simple Data Containers**
   ```python
   from dataclasses import dataclass
   
   @dataclass
   class User:
       id: int
       name: str
       email: str
   ```

## Real-World Example: Flask Application Architecture

Here's how you might structure a Flask application using some of these patterns:

```
project_root/
│
├── app/
│   ├── __init__.py              # App initialization
│   ├── models/                  # Domain models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   └── user_repository.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── controllers/             # API endpoints
│   │   ├── __init__.py
│   │   └── user_controller.py
│   └── templates/               # UI templates
│       └── users/
│           └── profile.html
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
│
├── config.py                    # Configuration
└── run.py                       # Application entry point
```

Example implementation:

```python
# app/models/user.py
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

# app/repositories/user_repository.py
from app.models.user import User

class UserRepository:
    def __init__(self):
        self.users = {}
    
    def find_by_id(self, user_id):
        return self.users.get(user_id)
    
    def save(self, user):
        self.users[user.id] = user
        return user

# app/services/user_service.py
from app.models.user import User

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def get_user(self, user_id):
        return self.user_repository.find_by_id(user_id)
    
    def create_user(self, id, name, email):
        user = User(id=id, name=name, email=email)
        return self.user_repository.save(user)

# app/controllers/user_controller.py
from flask import Blueprint, jsonify, request
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

user_bp = Blueprint('users', __name__)
user_repository = UserRepository()
user_service = UserService(user_repository)

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = user_service.get_user(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email
        })
    return jsonify({'error': 'User not found'}), 404

@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    user = user_service.create_user(
        data['id'],
        data['name'],
        data['email']
    )
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }), 201

# app/__init__.py
from flask import Flask
from app.controllers.user_controller import user_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(user_bp, url_prefix='/api/users')
    return app
```

## Conclusion

Understanding design patterns and architecture principles is a key skill for senior Python developers. These patterns provide a common vocabulary for discussing solutions to recurring problems and help you write more maintainable, flexible, and scalable code.

Remember that design patterns are not a one-size-fits-all solution. Always consider the specific requirements and constraints of your project before applying a pattern. Sometimes, a simpler approach might be more appropriate than implementing a complex pattern.

Key takeaways:
- Design patterns are proven solutions to common software design problems
- Python's dynamic nature allows for elegant implementations of many patterns
- Architecture patterns help structure larger applications
- Choose the right pattern for your specific problem context
- Favor simplicity when possible

## Further Learning Resources

1. Books:
   - "Design Patterns: Elements of Reusable Object-Oriented Software" by the Gang of Four
   - "Python 3 Patterns, Recipes and Idioms" (available online)
   - "Architecture Patterns with Python" by Harry Percival and Bob Gregory

2. Online Resources:
   - [Python Design Patterns on GitHub](https://github.com/faif/python-patterns)
   - [Real Python's Design Patterns Series](https://realpython.com/tutorials/design-patterns/)
   - [Refactoring.Guru Design Patterns](https://refactoring.guru/design-patterns/python)
