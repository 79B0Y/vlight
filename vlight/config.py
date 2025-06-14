
import yaml

def load_config(path='configuration.yaml'):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)

    lights = config.get('lights', {})
    if 'definitions' not in lights:
        prefix = lights.get('prefix', 'light')
        pid = lights.get('pid', 'vlight')
        count = lights.get('count', 1)
        lights['definitions'] = [
            {'did': f'{prefix}-{i+1:04d}', 'pid': pid} for i in range(count)
        ]

    sensors = config.get('sensors')
    if sensors and 'definitions' not in sensors:
        s_prefix = sensors.get('prefix', 'sensor')
        s_pid = sensors.get('pid', 'vsensor')
        s_count = sensors.get('count', 1)
        sensors['definitions'] = [
            {'did': f'{s_prefix}-{i+1:04d}', 'pid': s_pid}
            for i in range(s_count)
        ]
    return config
