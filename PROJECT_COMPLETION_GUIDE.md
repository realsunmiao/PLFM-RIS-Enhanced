# PLFM-RIS-Enhanced 项目补全指南

> **本文档说明如何补全项目以实现完整复现**  
> 当前版本提供了核心架构和关键代码框架,部分模块需要用户根据实际需求补充实现。

---

## 📋 缺失模块清单

### ✅ 已完成模块
- [x] README.md - 项目主文档
- [x] 2_RIS_Antenna_Design/README.md - RIS 天线设计指南
- [x] 4_STC_Firmware/STC_Encoder.v - 时空编码核心
- [x] 4_STC_Firmware/Top_Module.v - FPGA 顶层模块
- [x] 4_STC_Firmware/SPI_Interface.v - SPI 通信接口
- [x] 9_GUI/main.py - Python GUI 主程序
- [x] 9_GUI/ris_control.py - RIS 控制器

### ❌ 待补充模块

#### 1. FPGA 固件 (4_STC_Firmware/)
- [ ] Beamforming.v - 波束赋形模块
- [ ] Waveform_Gen.v - LFM 波形生成
- [ ] ShiftRegister.v - 串并转换
- [ ] PIN_Driver.v - PIN 二极管驱动
- [ ] DAC_Control.v - DAC 控制逻辑
- [ ] Top_Module.xpr - Vivado 工程文件
- [ ] constraints.xdc - 引脚约束文件

#### 2. STM32 固件 (缺失整个目录)
- [ ] 3_Power_Management/ - 电源管理
- [ ] 5_Control_Circuit/ - 控制电路固件
  - [ ] main.c - STM32 主程序
  - [ ] power_seq.c - 电源时序控制
  - [ ] fpga_config.c - FPGA 配置接口
  - [ ] temperature_monitor.c - 温度监控

#### 3. 硬件设计文件 (需补充详细设计指南)
- [ ] 3_Feed_Network/ - 馈电网络设计
  - [ ] wilkinson_design.md - 威尔金森功分器设计
  - [ ] phase_shifter_design.md - 反射型移相器设计
- [ ] 5_Power_Supply/ - 电源系统设计
  - [ ] power_supply_design.md - 多路电源设计

#### 4. 仿真文件 (6_Simulation/)
- [ ] antenna_simulation/ - 天线仿真
  - [ ] hfss_script.aedt - HFSS 自动化脚本
  - [ ] cst_macro.cst - CST 宏命令
- [ ] stc_algorithm/ - STC 算法仿真
  - [ ] stc_simulation.m - MATLAB 仿真脚本
  - [ ] beam_pattern.py - Python 方向图绘制

#### 5. 应用笔记 (7_Application_Notes/)
- [ ] setup_guide.md - 环境搭建指南
- [ ] calibration.md - 校准方法
- [ ] troubleshooting.md - 故障排查

#### 6. 实用工具 (8_Utils/)
- [ ] data_parser.py - 数据解析脚本
- [ ] calibration_tool.py - 校准工具
- [ ] visualization.py - 可视化工具

---

## 🔧 快速补全方案

### 方案 A: 最小可行复现 (推荐初学者)

**目标**: 通过软件仿真验证核心算法,无需实际硬件

**步骤**:
1. **安装仿真环境**
   ```bash
   pip install numpy scipy matplotlib
   # 或安装 MATLAB
   ```

2. **运行 STC 算法仿真**
   ```python
   # 创建 6_Simulation/stc_algorithm/stc_simulation.py
   python 6_Simulation/stc_algorithm/stc_simulation.py
   ```

3. **测试 GUI**
   ```bash
   cd 9_GUI
   pip install -r requirements.txt
   python main.py  # 使用模拟数据模式
   ```

**预期结果**: 
- 看到距离剖面和距离-多普勒图的模拟数据
- 验证波束扫描和 LFM 波形生成算法

---

### 方案 B: 完整硬件复现 (适合有硬件条件者)

**前置要求**:
- PCB 打板能力
- FPGA/STM32 开发经验
- 射频测试设备(VNA、频谱仪等)

**补全顺序**:

#### 第 1 步: 补充 FPGA 完整固件

##### 1.1 创建 Beamforming.v

```verilog
// 文件: 4_STC_Firmware/Beamforming.v
// 功能: 计算波束赋形所需的相位偏移

module Beamforming (
    input wire clk,
    input wire rst_n,
    input wire [15:0] azimuth,
    input wire [15:0] elevation,
    output reg [11:0] phase_offset [0:63]  // 64 个单元的相位偏移
);
    // 实现阵列因子计算
    // φ_mn = (2π/λ) * (x_m*sinθ*cosφ + y_n*sinθ*sinφ)
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            integer i;
            for (i = 0; i < 64; i = i + 1)
                phase_offset[i] <= 12'd0;
        end else begin
            // TODO: 实现相位计算逻辑
            // 可使用 CORDIC 算法或查找表
        end
    end
endmodule
```

##### 1.2 创建约束文件 constraints.xdc

```tcl
# 文件: 4_STC_Firmware/constraints.xdc
# FPGA 引脚约束

# 时钟输入
set_property PACKAGE_PIN U18 [get_ports clk_100m]
set_property IOSTANDARD LVCMOS33 [get_ports clk_100m]

# SPI 接口
set_property PACKAGE_PIN M14 [get_ports spi_cs]
set_property PACKAGE_PIN N14 [get_ports spi_clk]
set_property PACKAGE_PIN P14 [get_ports spi_mosi]
set_property PACKAGE_PIN R14 [get_ports spi_miso]

# PIN 二极管控制 (64 路)
set_property PACKAGE_PIN A1 [get_ports {pin_ctrl[0]}]
# ... 依次定义 pin_ctrl[1] 到 pin_ctrl[63]

# VarCap 控制 (512 位,通过串行输出)
set_property PACKAGE_PIN B1 [get_ports varcap_data]
set_property PACKAGE_PIN C1 [get_ports varcap_clock]
set_property PACKAGE_PIN D1 [get_ports varcap_latch]
```

#### 第 2 步: 创建 STM32 固件框架

##### 2.1 目录结构

```
5_Control_Circuit/
├── Inc/
│   ├── main.h
│   ├── power_seq.h
│   └── fpga_config.h
├── Src/
│   ├── main.c
│   ├── power_seq.c
│   └── fpga_config.c
├── MDK-ARM/
│   └── STM32F746.uvprojx  # Keil 工程文件
└── README.md
```

##### 2.2 main.c 框架

```c
/* 文件: 5_Control_Circuit/Src/main.c */
#include "main.h"
#include "power_seq.h"
#include "fpga_config.h"

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_SPI1_Init();
    MX_ADC1_Init();
    
    // 电源时序上电
    Power_Sequence_Up();
    
    // 初始化 FPGA
    FPGA_Init();
    
    while (1) {
        // 监控温度和电压
        Monitor_Temperature();
        Monitor_Voltage();
        
        // 处理上位机命令
        Process_USB_Command();
        
        HAL_Delay(10);
    }
}
```

##### 2.3 power_seq.c 框架

```c
/* 文件: 5_Control_Circuit/Src/power_seq.c */
#include "power_seq.h"

void Power_Sequence_Up(void) {
    // 按顺序上电,避免浪涌电流
    HAL_GPIO_WritePin(PWR_12V_EN_GPIO_Port, PWR_12V_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(100);
    
    HAL_GPIO_WritePin(PWR_5V_EN_GPIO_Port, PWR_5V_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(50);
    
    HAL_GPIO_WritePin(PWR_3V3_EN_GPIO_Port, PWR_3V3_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(50);
    
    HAL_GPIO_WritePin(PWR_1V8_EN_GPIO_Port, PWR_1V8_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(50);
    
    HAL_GPIO_WritePin(PWR_1V0_EN_GPIO_Port, PWR_1V0_EN_Pin, GPIO_PIN_SET);
}
```

#### 第 3 步: 补充硬件设计文档

##### 3.1 创建馈电网络设计指南

```markdown
# 文件: 3_Feed_Network/wilkinson_design.md

## 威尔金森功分器设计 (1分64)

### 设计参数
- 工作频率: 10.5 GHz
- 特性阻抗: 50 Ω
- 隔离度: > 23 dB
- 回波损耗: < -16 dB

### 实现步骤
1. 使用 ADS 设计单级 1分2 威尔金森功分器
2. 级联 6 级实现 1分64
3. 优化隔离电阻值 (理论值 100 Ω)
4. 仿真验证 S 参数

### PCB 布局要点
- 微带线宽度: 根据板材计算 (Rogers 4350B, h=0.508mm, W≈1.14mm)
- T 型结处添加补偿电容
- 隔离电阻使用 0603 封装
```

#### 第 4 步: 创建仿真脚本

##### 4.1 MATLAB STC 仿真

```matlab
% 文件: 6_Simulation/stc_algorithm/stc_simulation.m
% 时空编码算法仿真

clear; clc;

% 参数设置
f0 = 10.5e9;          % 起始频率 10.5 GHz
bandwidth = 100e6;    % 带宽 100 MHz
pulse_width = 10e-6;  % 脉冲宽度 10 μs
N_elements = 64;      % 阵元数
array_rows = 8;
array_cols = 8;

% 计算调频斜率
k = bandwidth / pulse_width;

% 生成 LFM 信号
t = linspace(0, pulse_width, 1000);
lfm_signal = exp(1j * 2 * pi * (f0 * t + 0.5 * k * t.^2));

% 空间编码: 计算波束指向
azimuth = 30;  % 方位角 30°
elevation = 0; % 俯仰角 0°

figure;
subplot(2,1,1);
plot(t * 1e6, real(lfm_signal));
title('LFM Signal (Real Part)');
xlabel('Time (μs)');
ylabel('Amplitude');

subplot(2,1,2);
spectrogram(lfm_signal, 256, 200, 256, 1e6, 'yaxis');
title('Spectrogram of LFM Signal');
xlabel('Time (μs)');
ylabel('Frequency (MHz)');
```

##### 4.2 Python 方向图绘制

```python
# 文件: 6_Simulation/stc_algorithm/beam_pattern.py
import numpy as np
import matplotlib.pyplot as plt

def array_factor(theta, phi, azimuth, elevation, wavelength=0.0286):
    """计算 8x8 阵列的阵列因子"""
    rows, cols = 8, 8
    d = wavelength / 2  # 阵元间距
    
    AF = 0
    for m in range(rows):
        for n in range(cols):
            x = n * d
            y = m * d
            
            # 相位差
            psi = (2 * np.pi / wavelength) * (
                x * np.sin(np.radians(elevation)) * np.cos(np.radians(azimuth)) +
                y * np.sin(np.radians(elevation)) * np.sin(np.radians(azimuth))
            )
            
            # 观察方向相位
            psi_obs = (2 * np.pi / wavelength) * (
                x * np.sin(np.radians(theta)) * np.cos(np.radians(phi)) +
                y * np.sin(np.radians(theta)) * np.sin(np.radians(phi))
            )
            
            AF += np.exp(1j * (psi_obs - psi))
    
    return np.abs(AF) / (rows * cols)

# 扫描范围
theta = np.linspace(-90, 90, 181)
phi = np.linspace(-90, 90, 181)
THETA, PHI = np.meshgrid(theta, phi)

# 计算方向图
azimuth_target = 30
elevation_target = 0
AF = np.zeros_like(THETA)

for i in range(len(theta)):
    for j in range(len(phi)):
        AF[j, i] = array_factor(theta[i], phi[j], azimuth_target, elevation_target)

# 绘图
plt.figure(figsize=(10, 8))
plt.contourf(THETA, PHI, 20 * np.log10(AF + 1e-10), levels=50, cmap='jet')
plt.colorbar(label='Gain (dB)')
plt.xlabel('Azimuth (°)')
plt.ylabel('Elevation (°)')
plt.title(f'Beam Pattern (Steered to {azimuth_target}°)')
plt.grid(True, alpha=0.3)
plt.savefig('beam_pattern.png', dpi=300, bbox_inches='tight')
plt.show()
```

#### 第 5 步: 编写应用笔记

##### 5.1 环境搭建指南

```markdown
# 文件: 7_Application_Notes/setup_guide.md

## FPGA 开发环境搭建

### 1. 安装 Vivado 2020.1
1. 从 Xilinx 官网下载 Vivado 2020.1
2. 安装时勾选 "Artix-7 系列" 支持
3. 申请免费许可证 (WebPACK)

### 2. 导入工程
```bash
vivado 4_STC_Firmware/Top_Module.xpr
```

### 3. 生成比特流
- 点击 "Generate Bitstream"
- 等待综合、实现完成
- 检查 timing report (确保无违例)

### 4. 烧录 FPGA
- 连接 JTAG 下载器
- 点击 "Program Device"
- 选择生成的 .bit 文件

## Python GUI 环境搭建

```bash
cd 9_GUI
pip install -r requirements.txt
```

## 硬件连接检查清单
- [ ] USB 数据线连接正常
- [ ] 电源适配器输出正确电压
- [ ] SMA 连接器紧固
- [ ] FPGA 配置 LED 亮起
```

---

## 📚 参考资源

### 官方文档
- [Xilinx Artix-7 Data Sheet](https://www.xilinx.com/support/documentation/data_sheets/ds181_Artix_7_Data_Sheet.pdf)
- [STM32F746 Reference Manual](https://www.st.com/resource/en/reference_manual/dm00105262-stm32f74xxx-and-stm32f75xxx-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf)
- [Rogers PCB Material Guide](https://rogerscorp.com/resources/)

### 开源参考
- [PLFM_RADAR 原始项目](https://github.com/NawfalMotii79/PLFM_RADAR)
- [GNU Radio Radar Toolkit](https://github.com/gnuradio/gr-radar)

### 学术论文
- Wang, S.R., et al. "Simplified radar architecture based on information metasurface." Nature Communications 16, 6505 (2025).
- 专利 CN202610462974: "一种基于可重构超表面天线的低成本雷达前端"

---

## 🎯 下一步行动

根据你的资源和目标选择合适的补全方案:

**如果你是学生/研究者**:
→ 选择 **方案 A**,专注于算法仿真和论文撰写

**如果你有硬件团队**:
→ 选择 **方案 B**,按步骤补全所有模块

**如果你只想了解原理**:
→ 阅读 `2_RIS_Antenna_Design/README.md` 和 `4_STC_Firmware/STC_Encoder.v`

---

**需要帮助?** 
- 提交 Issue 描述你遇到的问题
- 查看 `7_Application_Notes/troubleshooting.md` (待补充)
- 参考原始 [PLFM_RADAR](https://github.com/NawfalMotii79/PLFM_RADAR) 项目
