import logging
import sys
from datetime import datetime

# Configureer de logger
def setup_logger():
    logger = logging.getLogger('tradingbot')
    logger.setLevel(logging.DEBUG)

    # Console handler met gekleurde output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Formatter met timestamp en kleuren
    class ColorFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[94m',    # Blauw
            'INFO': '\033[92m',     # Groen
            'WARNING': '\033[93m',   # Geel
            'ERROR': '\033[91m',    # Rood
            'CRITICAL': '\033[91m',  # Rood
            'ENDC': '\033[0m'       # Reset
        }

        def format(self, record):
            # Voeg timestamp toe
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Kleur op basis van log level
            color = self.COLORS.get(record.levelname, self.COLORS['ENDC'])
            
            # Format: [TIMESTAMP] [LEVEL] message
            return f"{color}[{timestamp}] [{record.levelname}] {record.getMessage()}{self.COLORS['ENDC']}"

    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)
    return logger

# Creëer een globale logger instantie
logger = setup_logger() 