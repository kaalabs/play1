"""Generate a JSON snapshot of the active configuration for documentation or deployment."""

import json
from firmware.common import config


def as_dict(nt):
    return nt._asdict() if hasattr(nt, "_asdict") else dict(nt.__dict__)


def main():
    payload = {
        "system": as_dict(config.system),
        "pins": as_dict(config.pins),
        "boiler": as_dict(config.boiler),
        "thermistor": as_dict(config.thermistor),
        "autofill": as_dict(config.autofill),
        "pump": as_dict(config.pump),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
