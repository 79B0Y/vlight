import logging
import os

def init_logger(config):
    log_path = config['logging']['file']
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        filename=log_path,
        level=getattr(logging, config['logging']['level'].upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    return logging.getLogger("vlight")
