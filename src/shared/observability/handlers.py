"""
Custom logging handlers for agent observability.
"""

import logging
import os
import sys
from typing import Optional

from strands.handlers import PrintingCallbackHandler, CompositeCallbackHandler

from .logging_utils import JSONFormatter
from ..config import get_log_level, get_log_file_path


class StructuredLoggingHandler:
    """Custom handler for structured logging to files or stdout based on environment."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with appropriate output based on environment."""
        logger = logging.getLogger(f"chaos_agent.{self.agent_name}")
        
        if logger.handlers:
            return logger
        
        # Add handler (file or stdout based on environment)
        handler = self._create_handler()
        if handler:
            handler.setFormatter(JSONFormatter())
            logger.addHandler(handler)
        
        # Use centralized config for log level
        log_level = get_log_level()
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.propagate = False
        
        return logger
    
    def _create_handler(self):
        """Create appropriate handler based on environment."""
        # Check for explicit configuration override
        force_stdout = os.environ.get('CHAOS_AGENT_LOG_TO_STDOUT', '').lower() in ('true', '1', 'yes')
        
        # In AWS environments, always log to stdout for CloudWatch integration
        if force_stdout or os.environ.get('AWS_EXECUTION_ENV'):
            # Use stdout for structured logs in containers so they reach CloudWatch
            return logging.StreamHandler(sys.stdout)
        
        # Local/notebook environment: use file logging
        try:
            log_file = get_log_file_path(self.agent_name)
            if not log_file:
                return logging.StreamHandler(sys.stderr)
            
            log_dir = os.path.dirname(os.path.abspath(log_file))
            if log_dir and log_dir != '.':
                os.makedirs(log_dir, exist_ok=True)
            
            # Test write permissions
            test_file = os.path.join(log_dir if log_dir else '.', f'.test_{self.agent_name}')
            with open(test_file, 'w') as f:
                f.write('test')
            os.unlink(test_file)
            
            return logging.FileHandler(log_file)
        except Exception:
            # Fallback to stderr to avoid interfering with agent stdout
            return logging.StreamHandler(sys.stderr)
    
    def __call__(self, **kwargs):
        """Handle callback events by logging them."""
        if not self.logger:
            return
        
        # Log all callback data as structured information
        log_level = "error" if any(key in kwargs for key in ['error', 'exception']) else "info"
        
        # Create log record with callback data
        self.logger.log(
            getattr(logging, log_level.upper()),
            "Agent callback event",
            extra={
                'agent_name': self.agent_name,
                'callback_data': kwargs
            }
        )


def get_callback(agent_name: str, **kwargs) -> CompositeCallbackHandler:
    """
    Get configured callback handler for agent observability.
    
    Combines PrintingCallbackHandler for clean stdout output with
    StructuredLoggingHandler for comprehensive file logging.
    
    Args:
        agent_name: Name of the agent for logging context
        **kwargs: Additional configuration options (for future extensibility)
        
    Returns:
        CompositeCallbackHandler that handles both stdout and logging
    """
    # Create the built-in printing handler for stdout
    printing_handler = PrintingCallbackHandler()
    
    # Create our custom structured logging handler
    logging_handler = StructuredLoggingHandler(agent_name)
    
    # Combine them with CompositeCallbackHandler
    return CompositeCallbackHandler(printing_handler, logging_handler)
