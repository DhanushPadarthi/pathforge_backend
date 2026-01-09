import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Timestamp for log files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Configure logging format
log_format = logging.Formatter(
    '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create logger for roadmaps
roadmap_logger = logging.getLogger('roadmap')
roadmap_logger.setLevel(logging.DEBUG)
roadmap_handler = logging.FileHandler(f'logs/roadmap_{timestamp}.log')
roadmap_handler.setFormatter(log_format)
roadmap_logger.addHandler(roadmap_handler)

# Create logger for resource operations
resource_logger = logging.getLogger('resource')
resource_logger.setLevel(logging.DEBUG)
resource_handler = logging.FileHandler(f'logs/resource_{timestamp}.log')
resource_handler.setFormatter(log_format)
resource_logger.addHandler(resource_handler)

# Create logger for time tracking
time_logger = logging.getLogger('time_tracking')
time_logger.setLevel(logging.DEBUG)
time_handler = logging.FileHandler(f'logs/time_tracking_{timestamp}.log')
time_handler.setFormatter(log_format)
time_logger.addHandler(time_handler)

# Create logger for AI service
ai_logger = logging.getLogger('ai_service')
ai_logger.setLevel(logging.DEBUG)
ai_handler = logging.FileHandler(f'logs/ai_service_{timestamp}.log')
ai_handler.setFormatter(log_format)
ai_logger.addHandler(ai_handler)

# Create combined logger for all operations
combined_logger = logging.getLogger('combined')
combined_logger.setLevel(logging.DEBUG)
combined_handler = logging.FileHandler(f'logs/combined_{timestamp}.log')
combined_handler.setFormatter(log_format)
combined_logger.addHandler(combined_handler)
