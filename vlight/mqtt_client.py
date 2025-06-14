
import paho.mqtt.client as mqtt
from vlight.light_device import LightDevice
from vlight.temp_sensor import TempSensor

class MQTTManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.client = mqtt.Client()
        self.client.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.devices = []
        self.sensors = []

    def on_connect(self, client, userdata, flags, rc):
        """Handle connection callbacks from the MQTT client."""
        if rc != 0:
            # Non-zero return codes indicate connection failure. Log the issue
            # and raise an exception so that the service can react accordingly
            # instead of silently continuing in a bad state.
            self.logger.error(f"Failed to connect to MQTT broker, rc={rc}")
            raise ConnectionError(f"MQTT connection failed with code {rc}")

        self.logger.info("Connected to MQTT broker with code " + str(rc))
        for dev in self.devices:
            dev.announce_discovery()
            dev.publish_state()
            self.client.subscribe(f"{dev.base_topic}/switch")
            self.client.subscribe(f"{dev.base_topic}/brightness")
            self.client.subscribe(f"{dev.base_topic}/colortemp")
            self.client.subscribe(f"{dev.base_topic}/rgb")
        for sensor in self.sensors:
            sensor.announce_discovery()
            sensor.publish_state()

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
        static_count = self.config['lights'].get('static_count', 0)

        for idx, defn in enumerate(self.config['lights']['definitions']):
            state = dict(self.config['lights']['default_state'])
            device_simulate = simulate and idx >= static_count
            device = LightDevice(
                did=defn['did'],
                pid=defn['pid'],
                mqtt_client=self.client,
                discovery_prefix=discovery_prefix,
                base_topic=base_topic,
                logger=self.logger,
                initial_state=state,
                simulate=device_simulate
            )
            self.devices.append(device)

        sensors_cfg = self.config.get('sensors')
        if sensors_cfg:
            sensor_base = sensors_cfg.get('base_topic', 'home')
            sensor_sim = sensors_cfg.get('simulate_behavior', {})
            initial_value = sensors_cfg.get('default_value', 250)
            for defn in sensors_cfg['definitions']:
                sensor = TempSensor(
                    did=defn['did'],
                    pid=defn['pid'],
                    mqtt_client=self.client,
                    discovery_prefix=discovery_prefix,
                    base_topic=sensor_base,
                    logger=self.logger,
                    initial_value=initial_value,
                    simulate_cfg=sensor_sim,
                )
                self.sensors.append(sensor)

        self.client.connect(mqtt_cfg['host'], mqtt_cfg['port'], 60)
        self.client.loop_start()
