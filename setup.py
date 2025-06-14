
from setuptools import setup, find_packages

setup(
    name="vlight",
    version="0.4.4",
    description="Virtual MQTT Light with auto device generation",
    author="LinknLink",
    packages=find_packages(),
    install_requires=[
        "paho-mqtt",
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "vlight = vlight.main:main"
        ]
    },
    include_package_data=True,
)
