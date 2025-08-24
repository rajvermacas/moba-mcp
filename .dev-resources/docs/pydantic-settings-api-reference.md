# Pydantic Settings API Reference

## Overview

Pydantic Settings provides a powerful way to manage application configuration using environment variables, dotenv files, and other sources. It extends Pydantic's validation capabilities to create type-safe configuration classes that automatically load values from various sources.

**Key Features:**
- Automatic environment variable loading
- Type validation and conversion
- Multiple configuration sources (env vars, .env files, secrets, etc.)
- Nested configuration support
- CLI integration capabilities

**Version Information:**
- Latest Version: 2.10.1 (as of August 2025)
- Requires: Python 3.9+
- Pydantic Dependency: v2.0+

**Official Documentation:**
- GitHub: https://github.com/pydantic/pydantic-settings
- Docs: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

## Installation & Setup

### Basic Installation

```bash
pip install pydantic-settings
```

### Optional Dependencies

```bash
# For AWS Secrets Manager integration
pip install "pydantic-settings[aws-secrets-manager]"

# For Azure Key Vault integration  
pip install "pydantic-settings[azure-key-vault]"

# For Google Cloud Secret Manager integration
pip install "pydantic-settings[gcp-secret-manager]"
```

### Import Structure

```python
# Pydantic v2+ - BaseSettings is in separate package
from pydantic_settings import BaseSettings, SettingsConfigDict

# Core Pydantic imports still from main package
from pydantic import BaseModel, Field, SecretStr
```

## Core Concepts

### BaseSettings vs BaseModel

| Feature | BaseModel | BaseSettings |
|---------|-----------|--------------|
| **Purpose** | Data validation and modeling | Configuration management |
| **Default validation** | Defaults not validated by default | **Defaults ARE validated by default** |
| **Environment variables** | Not automatically loaded | **Automatically loaded from environment** |
| **Initialization sources** | Only keyword arguments | Environment, .env files, secrets, CLI, etc. |
| **Use case** | API models, data structures | Application configuration |

### Automatic Environment Variable Loading

BaseSettings automatically attempts to load field values from:
1. **Environment variables** (highest priority)
2. **dotenv (.env) files**
3. **Secrets files** (Docker secrets, etc.)
4. **Initialization arguments** (lowest priority)

```python
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    database_url: str = "sqlite:///default.db"
    debug: bool = False
    port: int = 8000

# Will automatically read DATABASE_URL, DEBUG, PORT from environment
settings = AppSettings()
```

## Configuration Options

### SettingsConfigDict Parameters

The `SettingsConfigDict` replaces the old `Config` class from Pydantic v1:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Environment variables
        env_prefix='MY_APP_',           # Prefix for all env vars
        env_file='.env',                # dotenv file path(s)
        env_file_encoding='utf-8',      # Encoding for dotenv files
        case_sensitive=False,           # Case sensitivity for env vars
        
        # Nested variables
        env_nested_delimiter='__',      # Delimiter for nested env vars
        nested_model_default_partial_update=True,
        
        # JSON decoding
        enable_decoding=True,           # Enable JSON parsing from strings
        
        # Secrets
        secrets_dir='/run/secrets',     # Directory for secret files
        
        # Validation
        validate_default=True,          # Validate default values
        extra='ignore',                 # Handle extra variables
        
        # TOML/pyproject.toml
        pyproject_toml_table_header=('tool', 'pydantic-settings'),
        pyproject_toml_depth=0,         # Search depth for pyproject.toml
    )
```

### Environment Variable Prefixing

Use `env_prefix` to group related environment variables:

```python
class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='DB_')
    
    host: str = 'localhost'     # Reads from DB_HOST
    port: int = 5432           # Reads from DB_PORT  
    user: str                  # Reads from DB_USER (required)
    password: str              # Reads from DB_PASSWORD (required)

# Environment variables:
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=myuser  
# DB_PASSWORD=mypass
```

### Case Sensitivity

By default, environment variable matching is case-insensitive:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)  # Default
    
    redis_host: str  # Matches REDIS_HOST, redis_host, Redis_Host, etc.

class StrictSettings(BaseSettings):  
    model_config = SettingsConfigDict(case_sensitive=True)
    
    redis_host: str  # Only matches redis_host exactly (plus prefix)
```

## Field Configuration

### Environment Variable Mapping with Field

Use `Field(alias=...)` or `Field(validation_alias=...)` to customize environment variable names:

```python
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Simple alias - maps to MY_SECRET_KEY env var
    secret_key: str = Field(alias='MY_SECRET_KEY')
    
    # Validation alias - only for input, not serialization
    auth_token: str = Field(validation_alias='AUTH_TOKEN')
    
    # Multiple possible environment variable names
    redis_url: str = Field(
        validation_alias=AliasChoices('REDIS_URL', 'REDIS_DSN', 'CACHE_URL')
    )
    
    # Override env_prefix for specific field
    special_setting: str = Field(alias='SPECIAL_OVERRIDE')
```

### Default Value Handling

Unlike BaseModel, BaseSettings validates default values by default:

```python
class Settings(BaseSettings):
    # This default will be validated as an integer
    port: int = "8000"  # String "8000" will be converted to int 8000
    
    # Disable validation for this field's default
    debug_mode: bool = Field("true", validate_default=False)  # Stays as string "true"

class NoValidationSettings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)
    
    # No defaults will be validated in this class
    port: int = "8000"  # Stays as string "8000"
```

### Type Conversion Examples

Pydantic Settings handles automatic type conversion:

```python
import os
from typing import List, Dict
from pydantic_settings import BaseSettings

# Set environment variables
os.environ['DEBUG'] = 'true'           # String to bool
os.environ['PORT'] = '8080'           # String to int  
os.environ['RATE_LIMIT'] = '10.5'     # String to float
os.environ['TAGS'] = '["web", "api"]' # JSON string to list
os.environ['CONFIG'] = '{"timeout": 30, "retries": 3}'  # JSON string to dict

class Settings(BaseSettings):
    debug: bool         # true
    port: int          # 8080  
    rate_limit: float  # 10.5
    tags: List[str]    # ["web", "api"]
    config: Dict[str, int]  # {"timeout": 30, "retries": 3}
```

## Advanced Features

### Computed Fields

Use computed fields for derived configuration values:

```python
from pydantic import computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = 'localhost'
    port: int = 5432
    database: str = 'mydb'
    user: str
    password: str
    
    @computed_field
    @property  
    def database_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
```

### Model Validators for Complex Parsing

Use validators for custom parsing logic:

```python
from typing import Any
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str
    allowed_hosts: str
    
    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError('Redis URL must start with redis:// or rediss://')
        return v
    
    @model_validator(mode='after')  
    def validate_hosts(self) -> 'Settings':
        # Parse comma-separated hosts
        if isinstance(self.allowed_hosts, str):
            self.allowed_hosts = [h.strip() for h in self.allowed_hosts.split(',')]
        return self

# Environment: ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
# Result: allowed_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
```

### Nested Configuration

Handle complex configuration with nested models:

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseModel):
    host: str = 'localhost'
    port: int = 5432
    user: str
    password: str
    name: str = 'app'

class RedisConfig(BaseModel):
    host: str = 'localhost' 
    port: int = 6379
    db: int = 0

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',  # Use double underscore for nesting
        env_prefix='APP_'
    )
    
    database: DatabaseConfig
    redis: RedisConfig
    debug: bool = False

# Environment variables:
# APP_DATABASE__HOST=db.example.com
# APP_DATABASE__USER=dbuser
# APP_DATABASE__PASSWORD=secret
# APP_REDIS__HOST=cache.example.com  
# APP_DEBUG=true
```

### Multiple Environment File Support

Load from multiple environment files with precedence:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=['.env', '.env.local', '.env.production'],  # Later files override earlier
        env_file_encoding='utf-8'
    )
    
    database_url: str
    secret_key: str

# .env (default values)
# .env.local (local overrides)  
# .env.production (production overrides)
```

## Migration Patterns

### Converting from Manual os.getenv()

**Before (Manual approach):**

```python
import os
from typing import Optional

class Config:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///default.db')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.port = int(os.getenv('PORT', '8000'))
        self.redis_url = os.getenv('REDIS_URL') 
        if not self.redis_url:
            raise ValueError("REDIS_URL is required")
        
        # Custom URL parsing
        self.database_host = self._parse_db_host(self.database_url)
    
    def _parse_db_host(self, url: str) -> str:
        # Custom parsing logic
        if '://' in url:
            return url.split('://')[1].split('/')[0].split('@')[-1]
        return 'localhost'

config = Config()
```

**After (pydantic-settings):**

```python
from typing import Optional
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    
    database_url: str = 'sqlite:///default.db'
    debug: bool = False
    port: int = 8000  
    redis_url: str  # Required field - will raise error if not provided
    
    @computed_field
    @property
    def database_host(self) -> str:
        """Extract host from database URL"""
        if '://' in self.database_url:
            return self.database_url.split('://')[1].split('/')[0].split('@')[-1]
        return 'localhost'
    
    @field_validator('redis_url')
    @classmethod  
    def validate_redis_url(cls, v: str) -> str:
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError('Invalid Redis URL format')
        return v

settings = Settings()
```

### Handling Custom Parsing Logic

**Migration from custom parsers:**

```python
# Before: Manual parsing
def parse_allowed_hosts(hosts_str: str) -> list[str]:
    return [h.strip() for h in hosts_str.split(',') if h.strip()]

def parse_log_level(level_str: str) -> int:
    level_map = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40}
    return level_map.get(level_str.upper(), 20)

# After: Using validators
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    allowed_hosts: str = 'localhost'
    log_level: str = 'INFO'
    
    @field_validator('allowed_hosts', mode='after')
    @classmethod
    def parse_hosts(cls, v: str) -> list[str]:
        if isinstance(v, str):
            return [h.strip() for h in v.split(',') if h.strip()]
        return v
    
    @field_validator('log_level', mode='after') 
    @classmethod
    def parse_log_level(cls, v: str) -> int:
        level_map = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40}
        return level_map.get(v.upper(), 20)
```

### Server Configuration Migration

**Complete server config migration example:**

```python
from typing import Optional, List
from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='SERVER_',
        case_sensitive=False
    )
    
    # Server basics
    host: str = '0.0.0.0'
    port: int = 8000
    debug: bool = False
    
    # Database
    database_url: str = Field(
        default='sqlite:///app.db',
        validation_alias='DATABASE_URL'  # Don't use SERVER_ prefix for this
    )
    
    # Redis  
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Security
    secret_key: str = Field(min_length=32)
    allowed_hosts: str = 'localhost,127.0.0.1'
    
    # Logging
    log_level: str = 'INFO'
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @computed_field
    @property
    def redis_url(self) -> str:
        """Build Redis URL from components"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @field_validator('allowed_hosts', mode='after')
    @classmethod
    def parse_allowed_hosts(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [h.strip() for h in v.split(',') if h.strip()]
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f'Invalid log level. Must be one of: {valid_levels}')
        return v_upper

# Environment variables:
# SERVER_HOST=0.0.0.0
# SERVER_PORT=8080  
# DATABASE_URL=postgresql://user:pass@localhost/db
# SERVER_REDIS_HOST=cache.example.com
# SERVER_SECRET_KEY=your-very-long-secret-key-here
# SERVER_ALLOWED_HOSTS=example.com,www.example.com,api.example.com
```

## Code Examples

### Basic BaseSettings Setup

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # Basic fields with defaults
    app_name: str = 'My Application'
    debug: bool = False
    port: int = 8000
    
    # Required fields (no default)
    database_url: str
    secret_key: str

# Usage
settings = AppSettings()
print(settings.model_dump())
```

### Environment Variable Mapping Examples

```python
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='MYAPP_')
    
    # Simple field - reads MYAPP_API_KEY  
    api_key: str
    
    # Custom alias - reads MY_SECRET instead of MYAPP_MY_SECRET
    my_secret: str = Field(alias='MY_SECRET')
    
    # Multiple possible names
    database_url: str = Field(
        validation_alias=AliasChoices('DATABASE_URL', 'DB_URL', 'DATABASE_DSN')
    )
    
    # Mixed configuration
    redis_config: str = Field(
        default='redis://localhost:6379/0',
        validation_alias='REDIS_URL'  # Reads REDIS_URL, not MYAPP_REDIS_CONFIG
    )
```

### URL Parsing with Computed Fields

```python
from urllib.parse import urlparse
from pydantic import computed_field
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    database_url: str
    
    @computed_field
    @property
    def db_host(self) -> str:
        return urlparse(self.database_url).hostname or 'localhost'
    
    @computed_field  
    @property
    def db_port(self) -> int:
        parsed = urlparse(self.database_url)
        return parsed.port or 5432
    
    @computed_field
    @property  
    def db_name(self) -> str:
        parsed = urlparse(self.database_url)
        return parsed.path.lstrip('/') or 'postgres'
    
    @computed_field
    @property
    def db_user(self) -> str:
        parsed = urlparse(self.database_url)
        return parsed.username or 'postgres'

# Usage:
# DATABASE_URL=postgresql://myuser:mypass@db.example.com:5433/mydb
settings = DatabaseSettings()
print(f"Host: {settings.db_host}")      # db.example.com
print(f"Port: {settings.db_port}")      # 5433
print(f"Database: {settings.db_name}")  # mydb
print(f"User: {settings.db_user}")      # myuser
```

### .env File Loading Configuration

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

# Basic .env loading
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

# Multiple .env files (later files override earlier)
class MultiEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=['.env', '.env.local', '.env.production'],
        env_file_encoding='utf-8'
    )

# Runtime .env file specification  
class RuntimeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

# Override at runtime
settings = RuntimeSettings(_env_file='config.env')

# Disable .env file loading
settings = RuntimeSettings(_env_file=None)
```

## Error Handling

### Common Validation Errors

```python
from pydantic import ValidationError
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int  # Required field
    debug: bool = False

try:
    settings = Settings()  # PORT environment variable missing
except ValidationError as e:
    print(e.errors())
    # [{'type': 'missing', 'loc': ('port',), 'msg': 'Field required'}]

# Invalid type conversion
import os
os.environ['PORT'] = 'not-a-number'
try:
    settings = Settings()
except ValidationError as e:
    print(e.errors())
    # [{'type': 'int_parsing', 'loc': ('port',), 'msg': 'Input should be a valid integer'}]
```

### Custom Validation with Better Error Messages

```python
from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    allowed_hosts: str
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        valid_schemes = ['postgresql', 'mysql', 'sqlite']
        if not any(v.startswith(f'{scheme}://') for scheme in valid_schemes):
            raise ValueError(
                f'Database URL must start with one of: {", ".join(f"{s}://" for s in valid_schemes)}'
            )
        return v
    
    @field_validator('allowed_hosts')  
    @classmethod
    def validate_allowed_hosts(cls, v: str) -> str:
        hosts = [h.strip() for h in v.split(',')]
        for host in hosts:
            if not host or host.count('.') > 3:
                raise ValueError(f'Invalid host format: {host}')
        return v
```

## Best Practices

### 1. Organize Settings into Logical Groups

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    url: str  
    pool_size: int = 10
    timeout: int = 30

class RedisSettings(BaseModel):
    url: str = 'redis://localhost:6379/0'
    timeout: int = 5

class LoggingSettings(BaseModel):
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file: Optional[str] = None

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file='.env'
    )
    
    app_name: str = 'My Application'
    debug: bool = False
    
    database: DatabaseSettings
    redis: RedisSettings  
    logging: LoggingSettings
```

### 2. Use SecretStr for Sensitive Data

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Regular string - will be logged/printed
    app_name: str = 'My App'
    
    # Secret string - hidden in logs/repr
    api_key: SecretStr
    database_password: SecretStr
    
    def get_api_key(self) -> str:
        return self.api_key.get_secret_value()

settings = Settings()
print(settings)  # api_key and database_password will show as '**********'
```

### 3. Environment-Specific Configuration

```python
import os
from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing" 
    PRODUCTION = "production"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Auto-enable debug in development
        if self.environment == Environment.DEVELOPMENT:
            self.debug = True
        
        # Load environment-specific .env file
        env_file = f'.env.{self.environment.value}'
        if os.path.exists(env_file):
            self.model_config = SettingsConfigDict(
                env_file=['.env', env_file],
                env_file_encoding='utf-8'
            )
```

### 4. Testing Configuration

```python
import pytest
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = 'sqlite:///:memory:'
    redis_url: str = 'redis://localhost:6379/0'
    debug: bool = False

@pytest.fixture
def test_settings():
    """Override settings for testing"""
    return Settings(
        database_url='sqlite:///:memory:',
        redis_url='redis://localhost:6379/15',  # Different Redis DB for tests
        debug=True
    )

def test_app_functionality(test_settings):
    # Use test_settings instead of global settings
    assert test_settings.debug is True
    assert 'memory' in test_settings.database_url
```

### 5. Configuration Validation

```python
from typing import List
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    allowed_hosts: List[str] = ['localhost']
    max_connections: int = 100
    min_connections: int = 5
    
    @field_validator('allowed_hosts', mode='before')
    @classmethod
    def parse_hosts(cls, v):
        if isinstance(v, str):
            return [h.strip() for h in v.split(',')]
        return v
    
    @model_validator(mode='after')
    def validate_connections(self):
        if self.min_connections > self.max_connections:
            raise ValueError('min_connections cannot be greater than max_connections')
        return self
```

## Additional Resources

### Related Documentation
- [Pydantic Core Documentation](https://docs.pydantic.dev/)
- [Pydantic Field Documentation](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic Validation Documentation](https://docs.pydantic.dev/latest/concepts/validators/)

### Community Resources
- [Pydantic Settings GitHub](https://github.com/pydantic/pydantic-settings)
- [Pydantic GitHub Discussions](https://github.com/pydantic/pydantic/discussions)
- [Pydantic Discord Community](https://discord.gg/HtnAWeFpPG)

### Integration Examples
- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/) 
- [Django Pydantic Integration](https://github.com/yezz123/django-pydantic-v2)

---

*Documentation Version: August 2025*  
*Based on pydantic-settings v2.10.1*  
*Created: 2025-08-24*