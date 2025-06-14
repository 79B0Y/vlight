
import paho.mqtt.client as mqtt
from vlight.light_device import LightDevice

class MQTTManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.client = mqtt.Client()
        self.client.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.devices = []

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected to MQTT broker with code " + str(rc))
        for dev in self.devices:
            dev.announce_discovery()
            dev.publish_state()
            self.client.subscribe(f"{dev.base_topic}/switch")
            self.client.subscribe(f"{dev.base_topic}/brightness")
            self.client.subscribe(f"{dev.base_topic}/colortemp")
            self.client.subscribe(f"{dev.base_topic}/rgb")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        for dev in self.devices:
            if topic.startswith(dev.base_topic):
                key = topic.split("/")[-1]
                dev.handle_command(key, msg.payload.decode())
                break

    def start(self):
        mqtt_cfg = self.config['mqtt']
        base_topic = mqtt_cfg['base_topic']
        discovery_prefix = mqtt_cfg['discovery_prefix']
        simulate = self.config['lights'].get('simulate_behavior', False)

        for defn in self.config['lights']['definitions']:
            state = dict(self.config['lights']['default_state'])
            device = LightDevice(
                did=defn['did'],
                pid=defn['pid'],
                mqtt_client=self.client,
                discovery_prefix=discovery_prefix,
                base_topic=base_topic,
                logger=self.logger,
                initial_state=state,
                simulate=simulate
            )
            self.devices.append(device)

        self.client.connect(mqtt_cfg['host'], mqtt_cfg['port'], 60)
        self.client.loop_start()
