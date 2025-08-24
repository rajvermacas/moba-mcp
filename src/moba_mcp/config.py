"""Configuration management for the Moba MCP server.

This module handles all configuration settings including database paths,
metadata locations, and server settings.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    """Configuration settings for the MCP server."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Database configuration
    database_path: str = Field(
        default="test_data/sample.db",
        description="Path to the SQLite database file"
    )
    
    # Resource configuration
    metadata_path: str = Field(
        default="resources/metadata.json",
        description="Path to the resource metadata JSON file"
    )
    
    # Server configuration
    server_name: str = Field(
        default="moba-mcp",
        description="Name of the MCP server"
    )
    
    server_version: str = Field(
        default="0.1.0",
        description="Version of the MCP server"
    )
    
    # Network configuration
    host: str = Field(
        default="localhost",
        description="Host address to bind the server (use 0.0.0.0 for all interfaces)"
    )
    
    port: int = Field(
        default=8000,
        description="Port number for the server"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_mcp_server_url(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Parse MCP_SERVER_URL if provided and set host/port."""
        # Check both uppercase and lowercase due to case_sensitive=False
        mcp_url = (values.get('MCP_SERVER_URL') or 
                   values.get('mcp_server_url') or 
                   os.getenv('MCP_SERVER_URL'))
        if mcp_url:
            try:
                parsed = urlparse(mcp_url)
                if parsed.hostname:
                    values['host'] = parsed.hostname
                if parsed.port:
                    values['port'] = parsed.port
            except Exception as e:
                logging.warning(f"Failed to parse MCP_SERVER_URL '{mcp_url}': {e}")
        return values
    
    transport: str = Field(
        default="stdio",
        description="Transport type: stdio, sse, or streamable-http"
    )
    
    stateless_http: bool = Field(
        default=False,
        description="Enable stateless HTTP mode (no session persistence)"
    )
    
    json_response: bool = Field(
        default=False,
        description="Use JSON responses instead of SSE streams (for streamable-http)"
    )
    
    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    
    # Query limits
    max_query_length: int = Field(
        default=10000,
        description="Maximum allowed query length in characters"
    )
    
    max_result_rows: int = Field(
        default=1000,
        description="Maximum number of rows to return in query results"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level value."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("database_path")
    @classmethod
    def validate_database_path(cls, v):
        """Validate database path."""
        if not v:
            raise ValueError("database_path cannot be empty")
        return v
    
    @field_validator("metadata_path")
    @classmethod
    def validate_metadata_path(cls, v):
        """Validate metadata path."""
        if not v:
            raise ValueError("metadata_path cannot be empty")
        return v
    
    @field_validator("max_query_length")
    @classmethod
    def validate_max_query_length(cls, v):
        """Validate maximum query length."""
        if v <= 0:
            raise ValueError("max_query_length must be positive")
        return v
    
    @field_validator("max_result_rows")
    @classmethod
    def validate_max_result_rows(cls, v):
        """Validate maximum result rows."""
        if v <= 0:
            raise ValueError("max_result_rows must be positive")
        return v
    
    @field_validator("transport")
    @classmethod
    def validate_transport(cls, v):
        """Validate transport type."""
        valid_transports = ["stdio", "sse", "streamable-http"]
        if v not in valid_transports:
            raise ValueError(f"transport must be one of {valid_transports}")
        return v
    
    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        """Validate port number."""
        if not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v
    
    def get_absolute_database_path(self, base_path: Optional[Path] = None) -> Path:
        """Get absolute path to database file.
        
        Args:
            base_path: Base path to resolve relative paths against
            
        Returns:
            Absolute path to database file
        """
        db_path = Path(self.database_path)
        if db_path.is_absolute():
            return db_path
        
        if base_path is None:
            base_path = Path.cwd()
        
        return base_path / db_path
    
    def get_absolute_metadata_path(self, base_path: Optional[Path] = None) -> Path:
        """Get absolute path to metadata file.
        
        Args:
            base_path: Base path to resolve relative paths against
            
        Returns:
            Absolute path to metadata file
        """
        metadata_path = Path(self.metadata_path)
        if metadata_path.is_absolute():
            return metadata_path
        
        if base_path is None:
            base_path = Path.cwd()
        
        return base_path / metadata_path




def setup_logging(config: ServerConfig) -> None:
    """Setup logging configuration.
    
    Args:
        config: Server configuration instance
    """
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=config.log_format,
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    # Set specific logger levels
    logger = logging.getLogger("moba_mcp")
    logger.setLevel(getattr(logging, config.log_level))
    
    # Reduce verbosity of external libraries if needed
    if config.log_level != "DEBUG":
        logging.getLogger("mcp").setLevel(logging.WARNING)
        logging.getLogger("sqlite3").setLevel(logging.WARNING)