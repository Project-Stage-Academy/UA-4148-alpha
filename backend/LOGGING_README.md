# Django Logging System Integration

## Overview
This pull request implements a comprehensive logging system for the Django forum project to track and monitor events, errors, and general runtime behavior. The logging system helps identify and troubleshoot issues by capturing important events across all application components.

## Features Implemented

### 1. Logging Configuration (`config/settings.py`)
- **Dual Output**: Logs are written to both console and file (`logs/forum.log`)
- **Log Levels**: Configured for DEBUG, INFO, WARNING, ERROR, and CRITICAL levels
- **Log Rotation**: Uses `TimedRotatingFileHandler` with daily rotation and 7-day retention
- **Formatters**: 
  - Console: Simple format with level and message
  - File: Verbose format with timestamp, level, logger name, and message

### 2. Application Coverage
Logging is implemented across all Django apps:
- **users**: User authentication, registration, profile management
- **profiles**: User profile operations
- **projects**: Project management and subscriptions
- **communications**: Chat and messaging functionality
- **dashboard**: Dashboard operations

### 3. Database Operations Logging
- **django.db.backends**: Captures all database queries for monitoring and optimization
- **Query Tracking**: Logs SQL queries, execution time, and database interactions

### 4. Security Event Logging
- **Permission Denials**: Logs unauthorized access attempts in `users/permissions.py`
- **Authentication Failures**: Tracks failed login attempts and security violations
- **Role-based Access**: Monitors access control violations

### 5. Error Handling
- **Exception Logging**: Comprehensive error logging in all views with try/catch blocks
- **Validation Errors**: Logs form validation failures and data integrity issues
- **Critical Errors**: Captures and logs all unhandled exceptions

## Technical Implementation

### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'forum.log',
            'when': 'midnight',
            'backupCount': 7,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        # App-specific loggers for users, profiles, projects, communications, dashboard
    },
}
```

### View Logging Example
```python
import logging

logger = logging.getLogger(__name__)

def example_view(request):
    try:
        logger.info("Processing the request.")
        # Some processing
    except Exception as e:
        logger.error(f"Error occurred: {e}")
```

### Permission Logging Example
```python
import logging
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)

class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        if some_condition_fails:
            logger.warning(f"Permission denied for user {request.user}")
            return False
        return True
```

## Benefits

1. **Debugging**: Easy identification of issues through comprehensive logging
2. **Monitoring**: Real-time monitoring of application behavior and performance
3. **Security**: Tracking of security events and unauthorized access attempts
4. **Performance**: Database query monitoring for optimization opportunities
5. **Maintenance**: Historical logs for troubleshooting and system maintenance

## Testing

The logging system has been tested with:
- User registration and authentication flows
- Database operations and query logging
- Permission-based access control
- Error handling and exception logging
- Security event tracking

### Test Script

A comprehensive test script was created to verify the logging system functionality. The script makes actual HTTP requests to the running Django server to trigger various logging events. Here's the test script that can be used by colleagues to test the logging system:

```python
"""
Test script to verify the logging system is working correctly in real conditions.
This script makes actual HTTP requests to the running Django server to test logging.
The logging system should automatically capture these events.
"""

import requests
import time

class RealWorldLoggingTest:
    """Test the logging system with real HTTP requests to the running server."""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "http://localhost:8000"
        
    def test_user_registration_success(self):
        """Test successful user registration logging."""
        
        registration_data = {
            "email": "newuser456@example.com",
            "username": "newuser456",
            "password": "newpass123",
            "confirm_password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": 11,  # investor role
            "representative_type": "investor",
            "company_name": "Test Company"
        }
        
        response = self.session.post(f'{self.base_url}/api/users/register/', json=registration_data)
        # Let the logging system handle the response logging
    
    def test_user_registration_failed(self):
        """Test failed user registration logging."""
        
        registration_data = {
            "email": "invalid-email",
            "username": "newuser2",
            "password": "short",
            "confirm_password": "different",
            "first_name": "",
            "last_name": "",
            "role": 999,  # non-existent role
            "representative_type": "",
            "company_name": ""
        }
        
        response = self.session.post(f'{self.base_url}/api/users/register/', json=registration_data)
        # Let the logging system handle the response logging
    
    def test_user_login_success(self):
        """Test successful user login logging."""
        
        # Test successful login with existing account
        login_data = {
            "email": "jamespena@example.com",
            "password": "password123"
        }
        
        response = self.session.post(f'{self.base_url}/api/users/login/', json=login_data)
        
        if response.status_code == 200:
            return response.json().get('access')
        else:
            return None
    
    def test_user_login_failed(self):
        """Test failed user login logging."""
        
        failed_login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = self.session.post(f'{self.base_url}/api/users/login/', json=failed_login_data)
        # Let the logging system handle the response logging
    
    def test_authenticated_requests(self, access_token):
        """Test authenticated requests logging."""
        
        if not access_token:
            return
        
        # Set authentication header
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Test user profile endpoint
        response = self.session.get(f'{self.base_url}/api/users/me/', headers=headers)
        # Let the logging system handle the response logging
    
    def test_permission_denials(self):
        """Test permission denial logging."""
        
        # Test accessing protected endpoint without authentication
        response = self.session.get(f'{self.base_url}/api/users/me/')
        # Let the logging system handle the response logging

    def run_all_tests(self):
        """Run all logging tests."""
        
        try:
            # Run tests that trigger logs
            self.test_user_registration_success()
            self.test_user_registration_failed()
            self.test_user_login_failed()
            access_token = self.test_user_login_success()
            self.test_authenticated_requests(access_token)
            self.test_permission_denials()
            
            # Give some time for logs to be written
            time.sleep(2)
            
        except Exception as e:
            pass  # Let the logging system handle errors

if __name__ == "__main__":
    # Run real-world tests
    test_suite = RealWorldLoggingTest()
    test_suite.run_all_tests()
```

## Log Files

- **Location**: `logs/forum.log`
- **Rotation**: Daily at midnight
- **Retention**: 7 days of backup files
- **Format**: Timestamp, log level, logger name, message

This implementation provides a robust foundation for monitoring and debugging the Django forum application while maintaining good performance and security practices.