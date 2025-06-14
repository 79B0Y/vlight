import time
import argparse
from vlight.config import load_config
from vlight.logger import init_logger
from vlight.mqtt_client import MQTTManager

def main():
    parser = argparse.ArgumentParser(description="Start vlight service")
    parser.add_argument(
        "-c",
        "--config",
        default="configuration.yaml",
        help="Path to configuration YAML file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    logger = init_logger(config)
    mqtt_manager = MQTTManager(config, logger)
    mqtt_manager.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
