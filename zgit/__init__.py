"""A collection of git sync and analysis tools.

Copyright Wenyi Tang 2024-2025

:Author: Wenyi Tang
:Email: wenyitang@outlook.com
"""

import logging

logger = logging.getLogger("ZGIT")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s"))
logger.addHandler(handler)

__version__ = "1.0.2"
