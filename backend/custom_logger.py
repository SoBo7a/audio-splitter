import logging
import os
import gzip
import shutil
import re
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 1) Ensure logs/ directory exists
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 2) Constants
BASE_NAME    = "audio_splitter"
LOG_FILE     = os.path.join(LOG_DIR, f"{BASE_NAME}.log")
MAX_BYTES    = 2 * 1024 * 1024  # 2 MB
BACKUP_COUNT = 6

class TimestampedRotatingFileHandler(RotatingFileHandler):
    def doRollover(self):
        """
        On rollover:
        1) Close the current stream.
        2) Move & compress the current log file to a timestamped .gz.
        3) Re-open a new base log file.
        4) Remove any archives older than BACKUP_COUNT.
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # Build timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Original log: audio_splitter.log
        # Archive name:   audio_splitter-20250512_153045.log.gz
        archive_name = f"{BASE_NAME}-{timestamp}.log.gz"
        archive_path = os.path.join(LOG_DIR, archive_name)

        # Compress the current log to the archive, then erase it
        with open(self.baseFilename, "rb") as src, gzip.open(archive_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
        os.remove(self.baseFilename)

        # Re-open the log file (so future writes go to a fresh .log)
        self.mode = 'a'
        self.stream = self._open()

        # Prune old archives beyond BACKUP_COUNT
        pattern = re.compile(rf"^{re.escape(BASE_NAME)}-(\d{{8}}_\d{{6}})\.log\.gz$")
        archives = sorted(
            [f for f in os.listdir(LOG_DIR) if pattern.match(f)],
            key=lambda n: pattern.match(n).group(1)
        )
        # keep only the most recent BACKUP_COUNT
        for old in archives[:-BACKUP_COUNT]:
            try:
                os.remove(os.path.join(LOG_DIR, old))
            except OSError:
                pass


# 3) Set up the logger
logger = logging.getLogger("audio_splitter")
logger.setLevel(logging.DEBUG)

handler = TimestampedRotatingFileHandler(
    LOG_FILE,
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT
)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
