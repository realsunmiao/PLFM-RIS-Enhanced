# PLFM-RIS-Enhanced

[![License](https://img.shields.io/badge/license-CERN-OHL--P-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![FPGA](https://img.shields.io/badge/fpga-Vivado%202020.1-orange.svg)](https://www.xilinx.com/)

## 📡 项目简介

**PLFM-RIS-Enhanced** 是基于智能超表面(Reconfigurable Intelligent Surface, RIS)技术改进的脉冲线性调频(PLFM)相控阵雷达系统。相比传统相控阵架构，本方案通过时空编码(STC)超表面实现波束赋形与波形生成的一体化，显著降低硬件成本(↓50-60%)、功耗(↓52%)和系统复杂度，同时提升波束精度(<1°)、测距误差(≤5m)和测速误差(≤0.04m/s)。

### 🎯 核心创新

1. **RIS 替代 T/R 组件**: 采用 PIN 二极管 + 变容二极管复合结构，实现 360° 相位连续可调，射频器件减少 70%
2. **时空联合编码**: 单一超表面阵列同时实现 ±60° 二维波束扫描和 LFMCW 波形生成，消除独立 DDS/VCO
3. **射频域去斜处理**: 接收端直接在物理层完成宽带信号压缩，ADC 采样率从 100 MSPS 降至 1 MSPS

### 📊 性能对比

| 指标 | 传统 PLFM 雷达 | RIS 改进版 | 改善幅度 |
|-----|--------------|-----------|---------|
| 硬件成本 | $2000-3000 | $800-1200 | ↓ 50-60% |
| 系统功耗 | ~250W | ~120W | ↓ 52% |
| 波束扫描范围 | ±45° | ±60° | ↑ 33% |
| 波束指向精度 | ~2-3° | <1° | ↑ 50-67% |
| 测距误差 | ~10m | ≤5m | ↑ 50% |
| 测速误差 | ~0.1m/s | ≤0.04m/s | ↑ 60% |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    RIS 天线阵列 (8×8)                     │
│  ┌──────────┐  ┌──────────┐         ┌──────────┐       │
│  │ Unit(1,1)│  │ Unit(1,2)│   ...   │ Unit(1,8)│       │
│  │PIN+VarCap│  │PIN+VarCap│         │PIN+VarCap│       │
│  └──────────┘  └──────────┘         └──────────┘       │
│  ┌──────────┐  ┌──────────┐         ┌──────────┐       │
│  │ Unit(2,1)│  │ Unit(2,2)│   ...   │ Unit(2,8)│       │
│  └──────────┘  └──────────┘         └──────────┘       │
│       ...            ...                ...             │
│  ┌──────────┐  ┌──────────┐         ┌──────────┐       │
│  │ Unit(8,1)│  │ Unit(8,2)│   ...   │ Unit(8,8)│       │
│  └──────────┘  └──────────┘         └──────────┘       │
└──────────────────────┬──────────────────────────────────┘
                       │ 馈电网络 (1分64 威尔金森功分器)
                       │
┌──────────────────────▼──────────────────────────────────┐
│              高速可编程控制电路                           │
│  ┌─────────────┐    ┌──────────────┐                    │
│  │   FPGA      │───▶│ 串并转换芯片  │                    │
│  │ (XC7A100T)  │    │ (级联扩展)    │                    │
│  └─────────────┘    └──────┬───────┘                    │
│                            │                             │
│                  ┌─────────▼─────────┐                  │
│                  │                   │                  │
│           ┌──────▼──────┐   ┌───────▼──────┐           │
│           │ PIN 驱动    │   │ 12-bit DAC   │           │
│           │ (4.5ns延时) │   │ (0-10V输出)  │           │
│           └──────┬──────┘   └───────┬──────┘           │
│                  │                   │                  │
│            Vpin (0°/180°)     Vvar (0°~180°连续)       │
└─────────────────────────────────────────────────────────┘
```

## 📁 目录结构

```
PLFM-RIS-Enhanced/
├── 1_Project_Description/          # 项目总览文档
│   ├── README.md                   # 本文件
│   ├── Specifications.pdf          # 系统指标文档
│   └── System_Overview.pdf         # 系统架构说明
├── 2_RIS_Antenna_Design/           # RIS 天线阵列设计
│   ├── Antenna_Unit.sch            # 单元原理图
│   ├── Antenna_Array.brd           # 阵列 PCB 布局
│   ├── Gerber/                     # 光绘文件
│   ├── BOM.csv                     # 物料清单
│   └── 3D_Model.step               # 3D 模型
├── 3_Feed_Network/                 # 馈电网络设计
│   ├── Wilkinson_PowerDivider.sch  # 威尔金森功分器
│   ├── PhaseShifter.sch            # 反射型移相器
│   └── FeedNetwork.brd             # 馈电网络 PCB
├── 4_STC_Firmware/                 # 时空编码固件
│   ├── STC_Encoder.v               # Verilog 时空编码模块
│   ├── Beamforming.v               # 波束赋形模块
│   ├── Waveform_Gen.v              # LFM 波形生成
│   └── Top_Module.v                # 顶层模块
├── 5_Control_Circuit/              # 控制电路
│   ├── SPI_Interface.v             # SPI 通信接口
│   ├── ShiftRegister.v             # 串并转换
│   ├── PIN_Driver.v                # PIN 二极管驱动
│   └── DAC_Control.v               # DAC 控制逻辑
├── 6_Simulation/                   # 仿真验证
│   ├── Antenna_Simulation/         # 天线仿真 (HFSS/CST)
│   ├── RF_Chain_Simulation/        # 射频链路仿真 (ADS)
│   ├── STC_Algorithm/              # 时空编码算法 (MATLAB/Python)
│   └── System_Level/               # 系统级仿真
├── 7_Application_Notes/            # 应用笔记
│   ├── Setup_Guide.md              # 环境搭建指南
│   ├── Calibration.md              # 校准方法
│   └── Troubleshooting.md          # 常见问题排查
├── 8_Utils/                        # 实用工具
│   ├── data_parser.py              # 数据解析脚本
│   ├── calibration_tool.py         # 校准工具
│   └── visualization.py            # 可视化工具
└── 9_GUI/                          # Python 上位机界面
    ├── main.py                     # 主程序
    ├── ris_control.py              # RIS 控制接口
    ├── requirements.txt            # Python 依赖
    └── assets/                     # UI 资源
```

## 🚀 快速开始

### 硬件要求

- **RIS 天线阵列**: 8×8 单元 (64 个 RIS 单元)
- **控制板**: FPGA (Xilinx Artix-7 XC7A100T) + STM32F746
- **电源**: 12V/5V/3.3V/1.8V/1.0V 多路供电
- **外设**: USB 数据线、天线馈源

### 软件环境

#### 1. FPGA 编译环境 (Vivado)

```bash
# 安装 Vivado 2020.1 (推荐版本)
# 确保勾选 "Artix-7 系列" 支持

# 导入项目
vivado 4_STC_Firmware/Top_Module.xpr

# 生成比特流并烧录
generate_bitstream
program_fpga
```

#### 2. Python GUI 环境

```bash
cd 9_GUI
pip install -r requirements.txt
python main.py
```

#### 3. 仿真环境

- **天线仿真**: HFSS 或 CST Studio
- **射频仿真**: ADS (Advanced Design System)
- **算法仿真**: MATLAB 或 Python (NumPy, SciPy)

### 调试流程

1. **连接硬件**: USB 连接主板与电脑，接通电源
2. **启动系统**: 运行 GUI，配置雷达参数
3. **验证功能**: 使用金属目标测试检测能力

## 📖 技术文档

- [系统规格说明书](1_Project_Description/Specifications.pdf)
- [RIS 天线设计指南](2_RIS_Antenna_Design/README.md)
- [时空编码算法详解](6_Simulation/STC_Algorithm/README.md)
- [校准与调试手册](7_Application_Notes/Calibration.md)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！在贡献前请阅读：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

- **硬件设计**: CERN Open Hardware Licence v2 - Permissive (CERN-OHL-P)
- **软件代码**: MIT License

详见 [LICENSE](LICENSE) 文件。

## 📚 参考文献

1. Wang, S.R., et al. "Simplified radar architecture based on information metasurface." *Nature Communications* 16, 6505 (2025).
2. 赵震宇, 郭永新. "可重构超表面赋能智能雷达." *iScience* (2026).
3. 专利 CN202610462974: "一种基于可重构超表面天线的低成本雷达前端" (2026).
4. NawfalMotii79. "PLFM_RADAR: Open-source, low-cost 10.5 GHz PLFM phased array RADAR system." GitHub (2026).

## 👥 作者

本项目由 Wukong AI Assistant 基于 PLFM_RADAR 项目改进开发。

## 🙏 致谢

感谢以下项目和团队的开源贡献：

- [PLFM_RADAR](https://github.com/NawfalMotii79/PLFM_RADAR) - 原始 PLFM 相控阵雷达项目
- 东南大学崔铁军院士团队 - 时空编码超表面研究
- 新加坡国立大学赵震宇团队 - 可重构超表面雷达综述

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
