# Advanced Python Logging Guide

## Table of Contents
1. [Logging Architecture Overview](#logging-architecture-overview)
2. [Logger Hierarchy and Propagation](#logger-hierarchy-and-propagation)
3. [Handlers: Output Destinations](#handlers-output-destinations)
4. [Formatters: Message Styling](#formatters-message-styling)
5. [Filters: Selective Logging](#filters-selective-logging)
6. [Configuration Strategies](#configuration-strategies)
7. [Performance Optimization](#performance-optimization)
8. [Structured Logging](#structured-logging)
9. [Production Patterns](#production-patterns)
10. [Monitoring Integration](#monitoring-integration)

## Logging Architecture Overview

Python's logging system follows a hierarchical architecture with four main components:

```
Logger → Filter → Handler → Filter → Formatter → Output
```

### Core Components

- **Logger**: Entry point for log messages, organized in a hierarchy
- **Handler**: Determines where log records go (console, file, network)
- **Formatter**: Controls the layout of log messages
- **Filter**: Provides fine-grained control over which records are processed

## Logger Hierarchy and Propagation

### Hierarchy Structure

Loggers form a tree structure using dot notation:

```python
import logging

# Root logger
root = logging.getLogger()

# Application loggers
app = logging.getLogger('myapp')
db = logging.getLogger('myapp.database')
api = logging.getLogger('myapp.api')
auth = logging.getLogger('myapp.api.auth')
```

### Propagation Mechanism

```python
import logging

# Configure root logger
logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')

# Create child logger
child = logging.getLogger('myapp.module')
child.setLevel(logging.DEBUG)

# Log message - will propagate to root logger
child.info("This message will appear")  # Output: myapp.module: This message will appear

# Disable propagation
child.propagate = False
child.info("This won't propagate to root")  # No output (no handlers on child)
```

### Effective Level Calculation

```python
import logging

# Root at WARNING
logging.getLogger().setLevel(logging.WARNING)

# Child logger inherits from parent
child = logging.getLogger('myapp')
print(child.getEffectiveLevel())  # 30 (WARNING)

# Explicitly set child level
child.setLevel(logging.DEBUG)
print(child.getEffectiveLevel())  # 10 (DEBUG)
```

## Handlers: Output Destinations

### Built-in Handler Types

```python
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

logger = logging.getLogger('advanced_example')

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File Handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Rotating File Handler (size-based)
rotating_handler = RotatingFileHandler(
    'app_rotating.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

# Timed Rotating Handler
timed_handler = TimedRotatingFileHandler(
    'app_timed.log',
    when='midnight',
    interval=1,
    backupCount=30
)

# Memory Handler (buffers logs)
memory_handler = logging.handlers.MemoryHandler(
    capacity=100,
    target=file_handler  # Flush to this handler when full
)

# Add handlers to logger
for handler in [console_handler, file_handler, rotating_handler]:
    logger.addHandler(handler)
```

### Custom Handlers

```python
import logging
import requests
from typing import Dict, Any

class SlackHandler(logging.Handler):
    """Custom handler that sends logs to Slack"""
    
    def __init__(self, webhook_url: str, channel: str = None):
        super().__init__()
        self.webhook_url = webhook_url
        self.channel = channel
    
    def emit(self, record: logging.LogRecord):
        try:
            log_message = self.format(record)
            payload = {
                "text": log_message,
                "channel": self.channel
            }
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception:
            self.handleError(record)

# Usage
slack_handler = SlackHandler("https://hooks.slack.com/...", "#alerts")
slack_handler.setLevel(logging.ERROR)
logger.addHandler(slack_handler)
```

## Formatters: Message Styling

### Standard Formatting

```python
import logging
from datetime import datetime

# Basic formatter
basic_formatter = logging.Formatter('%(levelname)s - %(message)s')

# Detailed formatter
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

# Custom date format
custom_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### Advanced Custom Formatters

```python
import logging
import json
from typing import Dict, Any

class JsonFormatter(logging.Formatter):
    """Formats log records as JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
            
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

class ContextFormatter(logging.Formatter):
    """Formatter that includes contextual information"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add context information
        if not hasattr(record, 'context'):
            record.context = {}
            
        # You could pull from thread-local storage, request context, etc.
        record.context.update({
            'thread_name': record.thread,
            'process_id': record.process
        })
        
        # Format with context
        original = super().format(record)
        if record.context:
            context_str = ' '.join(f"{k}={v}" for k, v in record.context.items())
            return f"{original} [{context_str}]"
        return original
```

## Filters: Selective Logging

### Built-in Filters

```python
import logging

class LevelFilter(logging.Filter):
    """Only allow specific log levels"""
    
    def __init__(self, allowed_levels):
        super().__init__()
        self.allowed_levels = allowed_levels
    
    def filter(self, record):
        return record.levelno in self.allowed_levels

class ModuleFilter(logging.Filter):
    """Filter by module name"""
    
    def __init__(self, allowed_modules):
        super().__init__()
        self.allowed_modules = allowed_modules
    
    def filter(self, record):
        return any(record.name.startswith(module) for module in self.allowed_modules)

# Usage
logger = logging.getLogger('myapp')
handler = logging.StreamHandler()

# Only INFO and WARNING
level_filter = LevelFilter([logging.INFO, logging.WARNING])
handler.addFilter(level_filter)

# Only certain modules
module_filter = ModuleFilter(['myapp.api', 'myapp.auth'])
handler.addFilter(module_filter)
```

### Advanced Filtering

```python
import logging
import re
from typing import Pattern

class RegexFilter(logging.Filter):
    """Filter log messages using regex patterns"""
    
    def __init__(self, pattern: str, exclude: bool = False):
        super().__init__()
        self.pattern: Pattern = re.compile(pattern)
        self.exclude = exclude
    
    def filter(self, record):
        match = self.pattern.search(record.getMessage())
        return not match if self.exclude else bool(match)

class RateLimitFilter(logging.Filter):
    """Rate limit log messages"""
    
    def __init__(self, max_per_minute: int = 60):
        super().__init__()
        self.max_per_minute = max_per_minute
        self.message_counts = {}
        self.last_reset = time.time()
    
    def filter(self, record):
        import time
        current_time = time.time()
        
        # Reset counts every minute
        if current_time - self.last_reset > 60:
            self.message_counts.clear()
            self.last_reset = current_time
        
        # Count this message
        message = record.getMessage()
        count = self.message_counts.get(message, 0) + 1
        self.message_counts[message] = count
        
        return count <= self.max_per_minute

# Usage
regex_filter = RegexFilter(r'password|secret', exclude=True)  # Exclude sensitive data
rate_filter = RateLimitFilter(max_per_minute=10)

handler.addFilter(regex_filter)
handler.addFilter(rate_filter)
```

## Configuration Strategies

### Dictionary Configuration

```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'json': {
            '()': 'myapp.logging.JsonFormatter'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'myapp.logging.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
            'level': 'DEBUG'
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
            'formatter': 'standard',
            'level': 'ERROR',
            'filters': ['require_debug_false']
        }
    },
    'loggers': {
        'myapp': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'myapp.database': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING'
    }
}

# Apply configuration
logging.config.dictConfig(LOGGING_CONFIG)
```

### Environment-based Configuration

```python
import os
import logging.config
from typing import Dict, Any

class LoggingConfigurator:
    """Dynamic logging configuration based on environment"""
    
    @staticmethod
    def get_config(environment: str = 'development') -> Dict[str, Any]:
        base_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                },
                'simple': {
                    'format': '%(levelname)s - %(message)s'
                }
            }
        }
        
        if environment == 'development':
            base_config.update({
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'detailed',
                        'level': 'DEBUG'
                    }
                },
                'root': {
                    'handlers': ['console'],
                    'level': 'DEBUG'
                }
            })
        
        elif environment == 'production':
            base_config.update({
                'handlers': {
                    'file': {
                        'class': 'logging.handlers.TimedRotatingFileHandler',
                        'filename': '/var/log/myapp/app.log',
                        'when': 'midnight',
                        'backupCount': 30,
                        'formatter': 'detailed',
                        'level': 'INFO'
                    },
                    'error_file': {
                        'class': 'logging.FileHandler',
                        'filename': '/var/log/myapp/errors.log',
                        'formatter': 'detailed',
                        'level': 'ERROR'
                    }
                },
                'root': {
                    'handlers': ['file', 'error_file'],
                    'level': 'INFO'
                }
            })
        
        return base_config
    
    @classmethod
    def configure(cls, environment: str = None):
        if environment is None:
            environment = os.getenv('ENVIRONMENT', 'development')
        
        config = cls.get_config(environment)
        logging.config.dictConfig(config)
```

## Performance Optimization

### Lazy Evaluation

```python
import logging

logger = logging.getLogger(__name__)

# BAD: String formatting happens even if log level is too low
logger.debug("Processing user %s with %d items" % (user.name, len(items)))

# GOOD: Lazy evaluation using % formatting
logger.debug("Processing user %s with %d items", user.name, len(items))

# GOOD: Using str.format() style
logger.debug("Processing user {} with {} items", user.name, len(items))

# BETTER: Check log level first for expensive operations
if logger.isEnabledFor(logging.DEBUG):
    expensive_data = calculate_expensive_debug_info()
    logger.debug("Debug info: %s", expensive_data)
```

### Custom LogRecord for Performance

```python
import logging
from typing import Any, Dict

class FastLogRecord(logging.LogRecord):
    """Optimized LogRecord for high-performance logging"""
    
    def __init__(self, name, level, pathname, lineno, msg, args, exc_info, func=None, extra=None):
        # Skip some expensive operations in __init__
        self.name = name
        self.msg = msg
        self.args = args
        self.levelname = logging.getLevelName(level)
        self.levelno = level
        self.pathname = pathname
        self.filename = pathname.split('/')[-1] if pathname else None
        self.module = self.filename[:-3] if self.filename and self.filename.endswith('.py') else self.filename
        self.exc_info = exc_info
        self.funcName = func
        self.lineno = lineno
        self.stack_info = None
        
        # Only calculate time when actually formatting
        self._created = None
        
        if extra:
            self.__dict__.update(extra)
    
    @property
    def created(self):
        if self._created is None:
            import time
            self._created = time.time()
        return self._created

# Use custom LogRecord
logging.setLogRecordFactory(FastLogRecord)
```

### Asynchronous Logging

```python
import asyncio
import logging
import queue
import threading
from typing import Optional

class AsyncHandler(logging.Handler):
    """Non-blocking handler that queues log records"""
    
    def __init__(self, target_handler: logging.Handler, queue_size: int = 1000):
        super().__init__()
        self.target_handler = target_handler
        self.queue = queue.Queue(maxsize=queue_size)
        self.thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
        self._start_worker()
    
    def _start_worker(self):
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
    
    def _worker(self):
        while not self.shutdown_event.is_set():
            try:
                record = self.queue.get(timeout=1)
                if record is None:  # Shutdown signal
                    break
                self.target_handler.handle(record)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in async logging worker: {e}")
    
    def emit(self, record: logging.LogRecord):
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            # Drop the record if queue is full
            pass
    
    def close(self):
        self.queue.put(None)  # Signal shutdown
        if self.thread:
            self.thread.join(timeout=5)
        self.target_handler.close()
        super().close()

# Usage
file_handler = logging.FileHandler('app.log')
async_handler = AsyncHandler(file_handler)
logger.addHandler(async_handler)
```

## Structured Logging

### JSON Logging with Context

```python
import logging
import json
import contextvars
from typing import Dict, Any, Optional
from datetime import datetime

# Context variables for request tracking
request_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('request_id', default=None)
user_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('user_id', default=None)

class StructuredFormatter(logging.Formatter):
    """Advanced structured logging formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Base structured data
        log_data = {
            '@timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add context variables
        if request_id.get():
            log_data['request_id'] = request_id.get()
        if user_id.get():
            log_data['user_id'] = user_id.get()
        
        # Add extra fields from LogRecord
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                        'filename', 'module', 'lineno', 'funcName', 'created',
                        'msecs', 'relativeCreated', 'thread', 'threadName',
                        'processName', 'process', 'stack_info', 'exc_info', 'exc_text')
        }
        log_data.update(extra_fields)
        
        # Handle exceptions
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info).split('\n')
            }
        
        return json.dumps(log_data, default=str)

# Context manager for request tracking
class RequestContext:
    def __init__(self, req_id: str, user: str = None):
        self.req_id = req_id
        self.user = user
        self.request_token = None
        self.user_token = None
    
    def __enter__(self):
        self.request_token = request_id.set(self.req_id)
        if self.user:
            self.user_token = user_id.set(self.user)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        request_id.reset(self.request_token)
        if self.user_token:
            user_id.reset(self.user_token)

# Usage example
logger = logging.getLogger('myapp')
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# In your application
with RequestContext('req-123', 'user-456'):
    logger.info('Processing request', extra={'action': 'login', 'ip': '192.168.1.1'})
    try:
        # Some operation
        raise ValueError("Something went wrong")
    except Exception:
        logger.exception('Request failed')
```

## Production Patterns

### Health Check Logging

```python
import logging
import time
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class HealthMetrics:
    requests_per_second: float
    error_rate: float
    avg_response_time: float
    memory_usage: float

class HealthCheckLogger:
    """Specialized logger for health metrics"""
    
    def __init__(self, logger_name: str = 'health'):
        self.logger = logging.getLogger(logger_name)
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def log_request(self, response_time: float, error: bool = False):
        self.request_count += 1
        self.response_times.append(response_time)
        if error:
            self.error_count += 1
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_metrics(self) -> HealthMetrics:
        elapsed = time.time() - self.start_time
        rps = self.request_count / elapsed if elapsed > 0 else 0
        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0
        avg_response = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        import psutil
        memory_usage = psutil.Process().memory_percent()
        
        return HealthMetrics(rps, error_rate, avg_response, memory_usage)
    
    def log_health(self):
        metrics = self.get_metrics()
        self.logger.info(
            'Health check',
            extra={
                'requests_per_second': metrics.requests_per_second,
                'error_rate': metrics.error_rate,
                'avg_response_time': metrics.avg_response_time,
                'memory_usage': metrics.memory_usage,
                'metric_type': 'health_check'
            }
        )

# Usage in web application
health_logger = HealthCheckLogger()

def middleware(request, response):
    start = time.time()
    try:
        # Process request
        return response
    except Exception:
        health_logger.log_request(time.time() - start, error=True)
        raise
    finally:
        health_logger.log_request(time.time() - start)

# Periodic health logging
import threading
def periodic_health_check():
    while True:
        health_logger.log_health()
        time.sleep(60)  # Every minute

health_thread = threading.Thread(target=periodic_health_check, daemon=True)
health_thread.start()
```

### Error Aggregation and Alerting

```python
import logging
import hashlib
from collections import defaultdict, Counter
from typing import Dict, Set
import time

class ErrorAggregator(logging.Handler):
    """Aggregates similar errors and triggers alerts"""
    
    def __init__(self, alert_threshold: int = 5, time_window: int = 300):
        super().__init__()
        self.alert_threshold = alert_threshold
        self.time_window = time_window
        self.error_counts: Dict[str, Counter] = defaultdict(Counter)
        self.alerted_errors: Set[str] = set()
        self.last_cleanup = time.time()
    
    def emit(self, record: logging.LogRecord):
        if record.levelno < logging.ERROR:
            return
        
        # Create error signature
        error_signature = self._create_error_signature(record)
        current_time = int(time.time() // 60)  # Minute buckets
        
        # Count this error
        self.error_counts[error_signature][current_time] += 1
        
        # Check if we should alert
        if error_signature not in self.alerted_errors:
            recent_count = sum(
                count for minute, count in self.error_counts[error_signature].items()
                if current_time - minute <= self.time_window // 60
            )
            
            if recent_count >= self.alert_threshold:
                self._send_alert(error_signature, recent_count, record)
                self.alerted_errors.add(error_signature)
        
        # Periodic cleanup
        if time.time() - self.last_cleanup > 3600:  # Every hour
            self._cleanup_old_errors()
    
    def _create_error_signature(self, record: logging.LogRecord) -> str:
        """Create a unique signature for similar errors"""
        signature_data = f"{record.module}:{record.funcName}:{record.lineno}"
        if record.exc_info:
            signature_data += f":{record.exc_info[0].__name__}"
        return hashlib.md5(signature_data.encode()).hexdigest()[:8]
    
    def _send_alert(self, signature: str, count: int, record: logging.LogRecord):
        """Send alert for high error rate"""
        alert_logger = logging.getLogger('alerts')
        alert_logger.critical(
            'High error rate detected',
            extra={
                'error_signature': signature,
                'count': count,
                'threshold': self.alert_threshold,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'alert_type': 'error_rate'
            }
        )
    
    def _cleanup_old_errors(self):
        """Remove old error data"""
        current_time = int(time.time() // 60)
        cutoff = current_time - (self.time_window // 60)
        
        for signature in list(self.error_counts.keys()):
            # Remove old minute buckets
            old_minutes = [
                minute for minute in self.error_counts[signature]
                if minute < cutoff
            ]
            for minute in old_minutes:
                del self.error_counts[signature][minute]
            
            # Remove empty signatures
            if not self.error_counts[signature]:
                del self.error_counts[signature]
                self.alerted_errors.discard(signature)
        
        self.last_cleanup = time.time()

# Usage
error_aggregator = ErrorAggregator(alert_threshold=10, time_window=300)
logger.addHandler(error_aggregator)
```

## Monitoring Integration

### Metrics Collection

```python
import logging
import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge

# Prometheus metrics
log_messages_total = Counter('log_messages_total', 'Total log messages', ['level', 'logger'])
log_processing_duration = Histogram('log_processing_duration_seconds', 'Log processing time')
active_loggers = Gauge('active_loggers_total', 'Number of active loggers')

class MetricsHandler(logging.Handler):
    """Handler that exports logging metrics to Prometheus"""
    
    def emit(self, record: logging.LogRecord):
        start_time = time.time()
        
        try:
            # Count log messages by level and logger
            log_messages_total.labels(
                level=record.levelname,
                logger=record.name
            ).inc()
            
            # Track processing time
            processing_time = time.time() - start_time
            log_processing_duration.observe(processing_time)
            
        except Exception:
            self.handleError(record)

# OpenTelemetry integration
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

class TracingHandler(logging.Handler):
    """Handler that creates traces for error logs"""
    
    def emit(self, record: logging.LogRecord):
        if record.levelno >= logging.ERROR:
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(f"error_log_{record.funcName}") as span:
                span.set_attribute("log.level", record.levelname)
                span.set_attribute("log.logger", record.name)
                span.set_attribute("log.module", record.module)
                span.set_attribute("log.function", record.funcName)
                span.set_attribute("log.line", record.lineno)
                
                if record.exc_info:
                    span.set_status(Status(StatusCode.ERROR, str(record.exc_info[1])))
                    span.record_exception(record.exc_info[1])

# Usage
metrics_handler = MetricsHandler()
tracing_handler = TracingHandler()

logger.addHandler(metrics_handler)
logger.addHandler(tracing_handler)
```

## Best Practices Summary

### Configuration
- Use dictionary configuration for complex setups
- Environment-specific configurations
- Centralized logging configuration
- Validate configuration at startup

### Performance
- Use lazy evaluation (% formatting with logging)
- Check log levels before expensive operations
- Consider async handlers for high-throughput applications
- Avoid creating loggers in tight loops

### Security
- Filter sensitive data (passwords, tokens, PII)
- Use structured logging for better parsing
- Implement log rotation to manage disk space
- Consider log shipping for centralized monitoring

### Error Handling
- Always handle exceptions in custom handlers
- Use try/except in emit() methods
- Implement fallback mechanisms
- Monitor handler health

### Monitoring
- Collect metrics on log volume and errors
- Set up alerting for error spikes
- Use distributed tracing for complex applications
- Monitor log processing latency

## Quick Reference

### Essential Logger Methods
```python
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
logger.exception("Error with traceback")  # Only in except blocks
```

### Handler Configuration
```python
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
handler.addFilter(filter_obj)
logger.addHandler(handler)
```

### Common Patterns
```python
# Logger per module
logger = logging.getLogger(__name__)

# Conditional logging
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Expensive debug info: %s", expensive_operation())

# Extra context
logger.info("User action", extra={'user_id': 123, 'action': 'login'})

# Structured data
logger.info("Request processed", extra={
    'request_id': req_id,
    'duration': elapsed,
    'status_code': 200
})
```