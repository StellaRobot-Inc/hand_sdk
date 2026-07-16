# hand_sdk
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)

一个统一的手部控制模块，支持多种手部类型的控制接口，包括Gaia系列灵巧手和Pantheon系列灵巧手。提供高级抽象接口和底层控制功能，适用于机器人研究、教育和工业应用。

# SDK

| 语言 | 安装方式 | 帮助文档 | 例程 |
|----------|---------|------|---------|
| Python | `pip install handsdk` | [HandSDK开发指南](https://qcnqdkti44v2.feishu.cn/wiki/FoLuwaO3ziOTSZkzplHcStIxnm7)) | [GaiaHand](./example/gaiahand_example.py) [PantheonHand](./example/pantheonhand_example.py) |

# SDK 架构
```
hand/
├── hand/
│   ├── __init__.py          # 模块入口
│   ├── core.py              # 核心抽象类和适配器
│   ├── gaiahand/            # Gaia手部实现
│   │   ├── gaia_hand.py     # Gaia手部适配器
│   │   ├── motor.py         # 电机控制
│   │   └── hand_mappings.py # 映射关系
│   ├── pantheonhand/        # Pantheon手部实现
│   │   ├── pantheon_hand.py # Pantheon手部适配器
│   │   └── can_utils/       # CAN通信工具
│   └── utils/               # 工具函数
│       └── serial_utils.py  # 串口工具
├── example/                 # 示例代码
├── docs/                    # 文档
├── tests/                   # 测试代码
└── setup.py                 # 安装配置
```

# 帮助文档
更多详细的文档内容，可查看[HandSDK开发指南](https://qcnqdkti44v2.feishu.cn/wiki/FoLuwaO3ziOTSZkzplHcStIxnm7)

# 联系我们
主页: [StellaRobot](https://www.stella-robot.com/)

反馈邮箱: [support@stella-robot.com](support@stella-robot.com)

# 许可证
本项目采用MIT许可证，查看[LICENSE](LICENSE)了解详情
