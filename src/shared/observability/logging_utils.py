"""
Logging utilities and container detection for observability system.
"""

import json
import logging
import os
import sys
from datetime import datetime




class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'component': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields dynamically
        for field in ['agent', 'execution_id', 'duration_ms', 'tool_name', 
                     'tool_use_id', 'error', 'tool_input', 'tool_output',
                     'agent_name', 'callback_data']:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, default=str, ensure_ascii=False)


def get_logger(component_name: str) -> logging.Logger:
    """
    Get configured logger for non-agent components.
    
    Args:
        component_name: Name of the component
        
    Returns:
        Configured logger instance
    """
    from ..config import get_log_level
    
    logger = logging.getLogger(f"chaos_agent.{component_name}")
    
    if not logger.handlers:
        # Use stderr to avoid interfering with agent stdout
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
        # Use centralized config for log level
        log_level = get_log_level()
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.propagate = False
    
    return logger
