
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
    return config
