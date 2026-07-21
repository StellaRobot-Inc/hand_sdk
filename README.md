# hand_sdk
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)

[简体中文](README.zh.md)

A unified control module for Stellarobot dexterous hands, supporting multiple hand interfaces including Gaia, Pantheon, and more. Providing both high‑level abstraction and low‑level control primitives, making it suitable for robotics research, education, and industrial applications.

# SDK

| Language | Install | Docs | Example |
|----------|---------|------|---------|
| Python | `pip install handsdk` | [Quick HandSDK Tutorial (Gaia20_direct_drive)](https://qcnqdkti44v2.feishu.cn/docx/JhOBdUFwconvDZxAnobc9Cqan36)<br>[HandSDK Development Guidelines](https://qcnqdkti44v2.feishu.cn/docx/K398dZc0cojwFDxEcnxc83oynyg) | [GaiaHand20](./example/gaiahand_example.py) <br>[PantheonHand20](./example/pantheonhand_example.py) |

# SDK Structure
```
hand/
├── hand/
│   ├── __init__.py          # Module Entry
│   ├── core.py              # Core Abstract Classes and Adapters
│   ├── gaiahand/            # GaiaHand Implementation
│   │   ├── gaia_hand.py     # GaiaHand Adapter
│   │   ├── motor.py         # Motor Control
│   │   └── hand_mappings.py # Mapping
│   ├── pantheonhand/        # PantheonHand Implementation
│   │   ├── pantheon_hand.py # PantheonHand Adapter
│   │   └── can_utils/       # CAN Communication Utilities
│   └── utils/               # Utility Functions
│       └── serial_utils.py  # Serial Port Utilities
├── example/                 # Examples
├── docs/                    # Documentation
├── tests/                   # Tests
└── setup.py                 # Installation
```

# Documentation
See [Quick HandSDK Tutorial (Gaia20_direct_drive)](https://qcnqdkti44v2.feishu.cn/docx/JhOBdUFwconvDZxAnobc9Cqan36) for a quick start.

For more detailed documentation, see [HandSDK Development Guidelines](https://qcnqdkti44v2.feishu.cn/docx/K398dZc0cojwFDxEcnxc83oynyg).

# Contact
Homepage: [StellaRobot](https://www.stella-robot.com/)

Feedback: [support@stella-robot.com](support@stella-robot.com)

# License
This project is licensed under the MIT License , see [LICENSE](LICENSE) for details.
