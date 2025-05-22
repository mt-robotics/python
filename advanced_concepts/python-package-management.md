# Python Package Management and Deployment

## Introduction

Effective package management and deployment are critical skills for senior Python developers. These processes ensure that your code can be reliably distributed, installed, and executed across different environments. This guide covers the essential aspects of Python package management and deployment, from creating distributable packages to implementing sophisticated deployment workflows.

## Table of Contents

1. [Package Management Fundamentals](#package-management-fundamentals)
2. [Creating Python Packages](#creating-python-packages)
3. [Dependency Management](#dependency-management)
4. [Package Distribution](#package-distribution)
5. [Virtual Environments](#virtual-environments)
6. [Modern Packaging Tools](#modern-packaging-tools)
7. [Deployment Strategies](#deployment-strategies)
8. [Containerization with Docker](#containerization-with-docker)
9. [CI/CD Pipelines for Python](#cicd-pipelines-for-python)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)
11. [Best Practices](#best-practices)

## Package Management Fundamentals

### What is a Python Package?

A Python package is a collection of modules organized in a directory hierarchy. It includes:

- Python modules (`.py` files)
- Package metadata
- Dependencies information
- Documentation
- Tests

### Package vs. Module

- **Module**: A single Python file containing classes, functions, and variables
- **Package**: A directory containing multiple related modules and an `__init__.py` file

### Python Packaging Ecosystem

- **PyPI (Python Package Index)**: The official repository for Python packages
- **pip**: The standard package installer for Python
- **setuptools**: A library for creating and distributing Python packages
- **wheel**: A built-package format that can be installed without building
- **twine**: A utility for publishing packages to PyPI

## Creating Python Packages

### Basic Package Structure

A minimal package structure:

```
mypackage/
├── __init__.py
├── module1.py
├── module2.py
└── setup.py
```

A more comprehensive structure:

```
mypackage/
├── LICENSE
├── README.md
├── pyproject.toml
├── setup.py
├── setup.cfg
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
└── tests/
    ├── __init__.py
    ├── test_module1.py
    └── test_module2.py
```

### Creating setup.py

The `setup.py` file defines your package's metadata and dependencies:

```python
from setuptools import setup, find_packages

setup(
    name="mypackage",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A short description of the package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mypackage",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=20.8b1",
            "flake8>=3.8.0",
        ],
    },
)
```

### Using pyproject.toml (Modern Approach)

The `pyproject.toml` file is the modern standard for Python packaging:

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mypackage"
version = "0.1.0"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
description = "A short description of the package"
readme = "README.md"
requires-python = ">=3.6"
license = {text = "MIT"}
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "requests>=2.25.0",
    "numpy>=1.19.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/mypackage"
"Bug Tracker" = "https://github.com/yourusername/mypackage/issues"

[project.optional-dependencies]
dev = [
    "pytest>=6.0.0",
    "black>=20.8b1",
    "flake8>=3.8.0",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

### Package Metadata

Key metadata elements:

- **name**: The name of your package on PyPI
- **version**: The package version (use [Semantic Versioning](https://semver.org/))
- **author and author_email**: Contact information
- **description and long_description**: Package descriptions
- **url**: Homepage for the package
- **classifiers**: Package metadata for PyPI (see [Classifiers](https://pypi.org/classifiers/))
- **python_requires**: Compatible Python versions
- **install_requires**: Package dependencies
- **extras_require**: Optional dependencies

### Creating the __init__.py File

The `__init__.py` file makes a directory a Python package:

```python
"""
My Package - A useful description of what the package does.

This package provides tools for:
- Feature 1
- Feature 2
- Feature 3
"""

__version__ = "0.1.0"

# Import important classes/functions to make them available at the package level
from .module1 import ClassA, function_b
from .module2 import ClassC

# Define what's available via `from mypackage import *`
__all__ = ["ClassA", "function_b", "ClassC"]
```

### Including Data Files

To include non-Python files in your package:

Using `setup.py`:
```python
setup(
    # ... other parameters
    package_data={
        "mypackage": ["data/*.json", "templates/*.html"],
    },
    # Or include all data files:
    include_package_data=True,
)
```

Using `MANIFEST.in`:
```
include LICENSE
include README.md
recursive-include src/mypackage/data *.json
recursive-include src/mypackage/templates *.html
```

Using `pyproject.toml` with setuptools:
```toml
[tool.setuptools.package-data]
mypackage = ["data/*.json", "templates/*.html"]
```

## Dependency Management

### Specifying Dependencies

In `setup.py` or `pyproject.toml`, use:

```python
install_requires=[
    "package1>=1.0.0,<2.0.0",  # At least 1.0.0 but less than 2.0.0
    "package2~=2.1.0",          # Compatible release (≥2.1.0, <3.0.0)
    "package3==1.0.5",          # Exactly version 1.0.5
    "package4>=4.0.0",          # At least version 4.0.0
]
```

Dependency specification operators:
- `==`: Exact version
- `>=`, `<=`, `>`, `<`: Version comparison
- `~=`: Compatible release
- `!=`: Not equal to

### Managing Dependencies with requirements.txt

A `requirements.txt` file lists all dependencies:

```
# requirements.txt
requests==2.25.1
numpy>=1.19.0
pandas~=1.2.0
matplotlib>=3.3.0
```

Install with:
```bash
pip install -r requirements.txt
```

### Pinning Dependencies

For reproducible environments, pin exact versions:

```
# requirements-frozen.txt
requests==2.25.1
numpy==1.19.5
pandas==1.2.4
matplotlib==3.4.2
certifi==2021.5.30
charset-normalizer==2.0.4
cycler==0.10.0
idna==3.2
kiwisolver==1.3.1
pillow==8.3.1
pyparsing==2.4.7
python-dateutil==2.8.2
pytz==2021.1
six==1.16.0
urllib3==1.26.6
```

Generate with:
```bash
pip freeze > requirements-frozen.txt
```

### Dependency Groups

Organize dependencies into logical groups:

```python
# In setup.py
extras_require={
    "dev": [
        "pytest>=6.0.0",
        "black>=20.8b1",
        "flake8>=3.8.0",
    ],
    "docs": [
        "sphinx>=3.0.0",
        "sphinx-rtd-theme>=0.5.0",
    ],
}
```

Install with:
```bash
pip install -e ".[dev,docs]"
```

## Package Distribution

### Building Source Distributions

A source distribution contains the raw source code:

```bash
python setup.py sdist
```

With modern tooling:
```bash
python -m build --sdist
```

### Building Wheel Distributions

A wheel is a pre-built package that can be installed without building:

```bash
python setup.py bdist_wheel
```

With modern tooling:
```bash
python -m build --wheel
```

### Build Both Distributions at Once

```bash
python -m build
```

### Publishing to PyPI

First, register an account on [PyPI](https://pypi.org/).

```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*
```

For testing, use the Test PyPI instance:
```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### Private Package Repositories

For private packages, you can use:
- [Artifactory](https://jfrog.com/artifactory/)
- [DevPI](https://www.devpi.net/)
- [AWS CodeArtifact](https://aws.amazon.com/codeartifact/)
- [GitHub Packages](https://github.com/features/packages)

Example with DevPI:
```bash
# Install DevPI client
pip install devpi-client

# Log in to the DevPI server
devpi login username --password=password

# Upload your package
devpi upload
```

## Virtual Environments

### Creating Virtual Environments

Using `venv` (built into Python 3):
```bash
python -m venv myenv

# Activate on Windows
myenv\Scripts\activate

# Activate on macOS/Linux
source myenv/bin/activate

# Deactivate
deactivate
```

### Using virtualenv

```bash
# Install
pip install virtualenv

# Create
virtualenv myenv

# Activate (same as venv)
```

### Using virtualenvwrapper

```bash
# Install
pip install virtualenvwrapper

# Setup (add to .bashrc or .zshrc)
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

# Create and activate
mkvirtualenv myproject

# Deactivate
deactivate

# Activate existing
workon myproject

# Delete
rmvirtualenv myproject
```

### Virtual Environment Best Practices

1. **Use one virtual environment per project**: Isolate dependencies
2. **Include the virtual environment in .gitignore**: Don't commit virtual environments
3. **Document environment setup**: Include instructions in README
4. **Use consistent naming**: Name environments after the project

## Modern Packaging Tools

### Poetry

Poetry is a modern dependency management and packaging tool:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Create a new project
poetry new myproject

# Initialize in existing project
cd existing-project
poetry init

# Add dependencies
poetry add requests numpy
poetry add pytest --dev

# Install dependencies
poetry install

# Update dependencies
poetry update

# Build package
poetry build

# Publish package
poetry publish
```

Sample `pyproject.toml` for Poetry:
```toml
[tool.poetry]
name = "mypackage"
version = "0.1.0"
description = "A sample Python package"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [{include = "mypackage", from = "src"}]

[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.25.0"
numpy = "^1.19.0"

[tool.poetry.group.dev.dependencies]
pytest = "^6.0.0"
black = "^20.8b1"
flake8 = "^3.8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Pipenv

Pipenv combines pip and virtual environments:

```bash
# Install Pipenv
pip install pipenv

# Install dependencies
pipenv install requests numpy
pipenv install pytest --dev

# Activate virtual environment
pipenv shell

# Install from Pipfile
pipenv install

# Lock dependencies
pipenv lock

# Uninstall package
pipenv uninstall requests
```

Sample `Pipfile`:
```toml
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
requests = "*"
numpy = "*"

[dev-packages]
pytest = "*"
black = "*"
flake8 = "*"

[requires]
python_version = "3.8"
```

### pip-tools

pip-tools helps manage dependencies with `requirements.txt`:

```bash
# Install
pip install pip-tools

# Generate requirements.txt from setup.py/requirements.in
pip-compile

# Generate dev-requirements.txt
pip-compile requirements-dev.in

# Install requirements
pip-sync requirements.txt dev-requirements.txt

# Update all packages
pip-compile --upgrade
```

Sample `requirements.in`:
```
# requirements.in
requests>=2.25.0
numpy>=1.19.0
```

### Comparison of Tools

| Feature | pip | Poetry | Pipenv | pip-tools |
|---------|-----|--------|--------|-----------|
| Dependency resolution | Basic | Advanced | Advanced | Advanced |
| Lock file | No | Yes | Yes | Yes |
| Virtual environments | No | Yes | Yes | No |
| Project initialization | No | Yes | Yes | No |
| Dependency groups | No | Yes | Limited | Limited |
| Build and publish | No | Yes | No | No |
| Maturity | High | Medium | Medium | Medium |
| Learning curve | Low | Medium | Medium | Low |

## Deployment Strategies

### Source Installation

Deploy by cloning and installing:

```bash
git clone https://github.com/username/myproject.git
cd myproject
pip install -e .
```

### Package Installation

Deploy from PyPI:

```bash
pip install mypackage
```

From a private repository:
```bash
pip install --index-url https://private-repo.example.com/simple/ mypackage
```

### Application Deployment

For web applications (e.g., Flask, Django):

```bash
# Clone repository
git clone https://github.com/username/mywebapp.git
cd mywebapp

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
gunicorn app:app  # For Flask
```

With WSGI server (uWSGI):
```bash
uwsgi --http :8000 --module app:app
```

### Using Fabric for Deployment

Fabric automates deployment tasks:

```python
# fabfile.py
from fabric import task

@task
def deploy(c):
    # Pull latest code
    c.run("cd /path/to/app && git pull")
    
    # Install dependencies
    c.run("cd /path/to/app && source venv/bin/activate && pip install -r requirements.txt")
    
    # Run migrations
    c.run("cd /path/to/app && source venv/bin/activate && flask db upgrade")
    
    # Restart service
    c.run("sudo systemctl restart myapp")
```

Run with:
```bash
fab -H user@server deploy
```

### Deploy with PaaS

Deploy to Platform as a Service providers:

**Heroku**:
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create myapp

# Push to Heroku
git push heroku main

# Scale dynos
heroku ps:scale web=1
```

**Google App Engine**:
```yaml
# app.yaml
runtime: python39

handlers:
- url: /.*
  script: auto

entrypoint: gunicorn -b :$PORT main:app
```

Deploy with:
```bash
gcloud app deploy
```

## Containerization with Docker

### Creating a Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

### Docker Compose for Development

```yaml
# docker-compose.yml
version: '3'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/myapp
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Building and Running Docker Containers

```bash
# Build image
docker build -t myapp .

# Run container
docker run -p 5000:5000 myapp

# With Docker Compose
docker-compose up

# Build and run in detached mode
docker-compose up -d --build
```

### Multi-stage Builds for Smaller Images

```dockerfile
# Build stage
FROM python:3.9 AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir wheel \
    && python setup.py bdist_wheel

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl \
    && rm *.whl

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

### Docker Tips for Python Applications

1. **Use specific image tags**: `python:3.9-slim` instead of `python:latest`
2. **Install dependencies first**: Leverage Docker's layer caching
3. **Don't run as root**: Add a non-root user
   ```dockerfile
   RUN useradd -m myuser
   USER myuser
   ```
4. **Set Python environment variables**:
   ```dockerfile
   ENV PYTHONDONTWRITEBYTECODE=1 \
       PYTHONUNBUFFERED=1
   ```
5. **Use .dockerignore** to exclude unnecessary files:
   ```
   .git
   __pycache__
   *.pyc
   venv
   .env
   ```

## CI/CD Pipelines for Python

### GitHub Actions

```yaml
# .github/workflows/python-app.yml
name: Python Application

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        pip install pytest
    
    - name: Test with pytest
      run: |
        pytest
    
    - name: Build package
      run: |
        pip install build
        python -m build
    
    - name: Publish to PyPI
      if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags')
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        user: __token__
        password: ${{ secrets.PYPI_API_TOKEN }}
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
image: python:3.9

stages:
  - test
  - build
  - deploy

before_script:
  - pip install -r requirements.txt

test:
  stage: test
  script:
    - pip install pytest pytest-cov
    - pytest --cov=mypackage

build:
  stage: build
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/
  only:
    - tags

deploy:
  stage: deploy
  script:
    - pip install twine
    - twine upload dist/*
  only:
    - tags
```

### Travis CI

```yaml
# .travis.yml
language: python
python:
  - "3.8"
  - "3.9"

install:
  - pip install -r requirements.txt
  - pip install pytest

script:
  - pytest

deploy:
  provider: pypi
  username: "__token__"
  password:
    secure: "your-encrypted-pypi-token"
  on:
    tags: true
    python: "3.9"
```

### CircleCI

```yaml
# .circleci/config.yml
version: 2.1
jobs:
  build-and-test:
    docker:
      - image: cimg/python:3.9
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: |
            python -m venv venv
            . venv/bin/activate
            pip install -r requirements.txt
            pip install pytest
      - run:
          name: Run tests
          command: |
            . venv/bin/activate
            pytest
  deploy:
    docker:
      - image: cimg/python:3.9
    steps:
      - checkout
      - run:
          name: Install build tools
          command: |
            python -m venv venv
            . venv/bin/activate
            pip install build twine
      - run:
          name: Build and publish
          command: |
            . venv/bin/activate
            python -m build
            twine upload dist/*

workflows:
  version: 2
  build-test-deploy:
    jobs:
      - build-and-test
      - deploy:
          requires:
            - build-and-test
          filters:
            tags:
              only: /^v.*/
            branches:
              ignore: /.*/
```

## Monitoring and Maintenance

### Application Monitoring

Monitor Python applications with:

- **Prometheus**: Metrics collection
  ```python
  from prometheus_client import start_http_server, Counter

  REQUEST_COUNT = Counter('app_requests_total', 'Total app requests')

  def process_request():
      REQUEST_COUNT.inc()
      # Process request...

  if __name__ == '__main__':
      start_http_server(8000)  # Expose metrics on port 8000
      # Start your app...
  ```

- **Sentry**: Error tracking
  ```python
  import sentry_sdk
  
  sentry_sdk.init(
      "https://your-sentry-dsn@sentry.io/123456",
      traces_sample_rate=0.2
  )
  
  def buggy_function():
      try:
          1 / 0
      except Exception as e:
          sentry_sdk.capture_exception(e)
  ```

- **New Relic**: Application performance monitoring
  ```python
  import newrelic.agent
  newrelic.agent.initialize('newrelic.ini')
  
  @newrelic.agent.background_task()
  def long_running_task():
      # Do something time-consuming...
      pass
  ```

### Dependency Updates

Keep dependencies updated:

- **Using pip**:
  ```bash
  pip list --outdated
  pip install --upgrade package-name
  ```

- **Using pipenv**:
  ```bash
  pipenv update
  pipenv update package-name
  ```

- **Using poetry**:
  ```bash
  poetry update
  poetry update package-name
  ```

### Automated Dependency Updates

Automate dependency updates with tools like:

- **Dependabot**:
  ```yaml
  # .github/dependabot.yml
  version: 2
  updates:
    - package-ecosystem: "pip"
      directory: "/"
      schedule:
        interval: "weekly"
      open-pull-requests-limit: 10
  ```

- **PyUp**:
  ```yaml
  # .pyup.yml
  update: all
  schedule: "every week"
  assignees:
    - yourusername
  ```

### Automated Security Scanning

Check for security vulnerabilities:

- **Safety**:
  ```bash
  pip install safety
  safety check
  ```

- **Bandit**:
  ```bash
  pip install bandit
  bandit -r .
  ```

- **In CI pipeline**:
  ```yaml
  - name: Security check
    run: |
      pip install safety bandit
      safety check
      bandit -r .
  ```

## Best Practices

### Package Naming

1. **Use lowercase names**: Follow PEP 8
2. **Use hyphens, not underscores**: For PyPI names (e.g., `my-package`)
3. **Be descriptive but concise**: Clearly indicate purpose
4. **Check availability**: Ensure name is not taken on PyPI
5. **Consider namespace packages**: For related packages (e.g., `yourcompany-packagename`)

### Versioning

Follow Semantic Versioning (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: Add functionality (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

Example: 2.1.3 (Major 2, Minor 1, Patch 3)

### Documentation

Include comprehensive documentation:

1. **README.md**: Project overview, installation, basic usage
2. **CONTRIBUTING.md**: Contribution guidelines
3. **CHANGELOG.md**: Version history
4. **Docstrings**: For all modules, classes, and functions
5. **Sphinx documentation**: For more detailed docs

Example README structure:
```markdown
# My Package

A brief description of what the package does.

## Installation

```bash
pip install mypackage
```

## Usage

```python
import mypackage

mypackage.do_something()
```

## Documentation

Full documentation at [Read the Docs](https://mypackage.readthedocs.io).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

### Managing Project Complexity

For large projects:

1. **Use a src-layout**:
   ```
   project/
   ├── src/
   │   └── mypackage/
   │       ├── __init__.py
   │       └── ...
   ├── tests/
   ├── docs/
   └── ...
   ```

2. **Split into subpackages**:
   ```
   src/mypackage/
   ├── __init__.py
   ├── core/
   │   ├── __init__.py
   │   └── ...
   ├── utils/
   │   ├── __init__.py
   │   └── ...
   └── cli/
       ├── __init__.py
       └── ...
   ```

3. **Use entry points**:
   ```python
   # In setup.py or pyproject.toml
   entry_points={
       'console_scripts': [
           'mycli=mypackage.cli:main',
       ],
   }
   ```

### Continuous Integration Workflow

Implement a comprehensive CI workflow:

1. **Run linters**: flake8, black, isort
2. **Run tests**: pytest with coverage
3. **Security scan**: safety, bandit
4. **Build package**: sdist and wheel
5. **Upload documentation**: Read the Docs
6. **Publish package** (for releases): PyPI

Example GitHub Actions workflow:
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install black isort flake8 mypy
    - name: Check code style
      run: |
        black --check .
        isort --check --profile black .
        flake8 .
        mypy src
  
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.7', '3.8', '3.9', '3.10']
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
        pip install -e .
    - name: Test with pytest
      run: |
        pytest --cov=mypackage --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
  
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit
    - name: Run security checks
      run: |
        safety check
        bandit -r src
  
  build:
    runs-on: ubuntu-latest
    needs: [quality, test, security]
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags')
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build and check package
      run: |
        python -m build
        twine check dist/*
    - name: Publish package
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        user: __token__
        password: ${{ secrets.PYPI_API_TOKEN }}
```

### Release Checklist

Before releasing a package:

1. **Update version number**: In `__init__.py`, `setup.py`, or `pyproject.toml`
2. **Update CHANGELOG.md**: Document changes
3. **Run full test suite**: Ensure all tests pass
4. **Check documentation**: Update and verify docs
5. **Create a git tag**: Tag the release in Git
6. **Build the distribution**: Create source and wheel distributions
7. **Test the distribution**: Install from the built package
8. **Upload to PyPI**: Publish the package
9. **Verify installation**: Test installing from PyPI

Example release script:
```bash
#!/bin/bash
set -e

# 1. Get the new version
if [ -z "$1" ]; then
    echo "Usage: ./release.sh VERSION"
    exit 1
fi
VERSION=$1

# 2. Update version number and verify
echo "Updating version to $VERSION"
sed -i "s/__version__ = .*/__version__ = \"$VERSION\"/" src/mypackage/__init__.py

# 3. Update changelog
echo "Don't forget to update CHANGELOG.md"
read -p "Press enter to continue"

# 4. Run tests
echo "Running tests..."
pytest

# 5. Build docs
echo "Building docs..."
cd docs && make html && cd ..

# 6. Create git tag
echo "Creating git commit and tag..."
git add .
git commit -m "Bump version to $VERSION"
git tag -a v$VERSION -m "Version $VERSION"

# 7. Build distribution
echo "Building distribution..."
python -m build

# 8. Test the distribution
echo "Testing distribution..."
cd dist
pip install --force-reinstall mypackage-$VERSION.tar.gz
cd ..

# 9. Upload to PyPI
echo "Uploading to PyPI..."
twine upload dist/*

# 10. Push to remote
echo "Pushing to remote..."
git push origin main
git push origin v$VERSION

echo "Release $VERSION completed!"
```

## Conclusion

Effective package management and deployment are essential skills for senior Python developers. By mastering these processes, you can:

1. Create well-structured, maintainable packages
2. Manage dependencies reliably
3. Automate building and publishing
4. Implement robust deployment workflows
5. Monitor and maintain applications in production

The Python ecosystem offers a rich set of tools and practices for each stage of the development lifecycle. Modern tools like Poetry and Docker, combined with CI/CD pipelines, enable streamlined workflows from development to deployment.

By following the best practices outlined in this guide, you can create Python packages that are easy to distribute, install, and maintain, whether you're building libraries for other developers or deploying applications to production environments.

## Further Resources

### Books
- "Python Packaging User Guide" (official documentation)
- "Packaging and Distributing Projects" (Python.org)
- "Docker for Python Developers" by Michael Herman

### Websites
- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI](https://pypi.org/)
- [Read the Docs](https://readthedocs.org/)
- [Testdriven.io](https://testdriven.io/blog/topics/docker/)

### Tools
- [PyPI](https://pypi.org/) - The Python Package Index
- [Poetry](https://python-poetry.org/) - Modern package management
- [Pipenv](https://pipenv.pypa.io/) - Virtual environment and package management
- [Docker](https://www.docker.com/) - Container platform
- [GitHub Actions](https://github.com/features/actions) - CI/CD platform
- [Read the Docs](https://readthedocs.org/) - Documentation hosting