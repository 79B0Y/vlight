import time
from vlight.config import load_config
from vlight.logger import init_logger
from vlight.mqtt_client import MQTTManager

def main():
    config = load_config()
    logger = init_logger(config)
    mqtt_manager = MQTTManager(config, logger)
    mqtt_manager.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
