# 环境搭建与调试指南

> 本文档提供从零开始搭建 PLFM-RIS-Enhanced 开发环境的详细步骤

---

## 📋 前置要求

### 硬件清单
- [ ] RIS 天线阵列 PCB (8×8, 64 单元)
- [ ] FPGA 开发板 (Xilinx Artix-7 XC7A100T)
- [ ] STM32F746 控制板
- [ ] 电源模块 (12V/5V/3.3V/1.8V/1.0V)
- [ ] USB-UART 桥接器
- [ ] SMA 射频连接器

### 软件清单
- [ ] Vivado 2020.1 或更高版本
- [ ] Keil uVision 5 (STM32 开发)
- [ ] Python 3.8+
- [ ] MATLAB (可选,用于仿真)

---

## 🔧 步骤 1: FPGA 开发环境搭建

### 1.1 安装 Vivado

1. **下载 Vivado**
   - 访问: https://www.xilinx.com/support/download.html
   - 选择 Vivado 2020.1 WebPACK (免费版本)
   - 下载大小: ~30 GB

2. **安装步骤**
   ```bash
   # Windows
   Xilinx_Vivado_2020.1_Win64.exe
   
   # Linux
   ./Xilinx_Vivado_2020.1_Lin64.bin
   ```

3. **选择组件**
   - ✅ Vivado HL Design Edition
   - ✅ Artix-7 系列支持
   - ✅ Device Programming Utilities
   - ❌ Zynq UltraScale+ (不需要,节省空间)

4. **申请许可证**
   - 启动 Vivado
   - Help → Manage License
   - 获取免费 WebPACK 许可证

### 1.2 导入工程

```bash
# 方法 1: GUI 方式
vivado
File → Open Project → 选择 4_STC_Firmware/Top_Module.xpr

# 方法 2: 命令行
vivado 4_STC_Firmware/Top_Module.xpr
```

### 1.3 生成比特流

1. **运行综合**
   - Flow Navigator → Run Synthesis
   - 等待完成 (~10 分钟)

2. **运行实现**
   - Flow Navigator → Run Implementation
   - 检查 Timing Report (确保无违例)

3. **生成比特流**
   - Flow Navigator → Generate Bitstream
   - 输出文件: `Top_Module.bit`

### 1.4 烧录 FPGA

1. **连接硬件**
   - JTAG 下载器连接到 FPGA 板
   - USB 连接到电脑

2. **烧录步骤**
   ```
   Open Hardware Manager → Auto Connect
   Right-click on device → Program Device
   选择 Top_Module.bit
   Click "Program"
   ```

3. **验证**
   - 观察 LED 指示灯
   - 使用 ILA (Integrated Logic Analyzer) 调试内部信号

---

## 🔧 步骤 2: STM32 开发环境搭建

### 2.1 安装 Keil uVision 5

1. **下载 Keil**
   - 访问: https://www.keil.com/demo/eval/arm.htm
   - 注册账号并下载

2. **安装 STM32F7 支持包**
   ```
   Pack Installer → STM32F7 Series → Install
   ```

3. **导入工程**
   ```
   File → Open Project → 5_Control_Circuit/STM32F746.uvprojx
   ```

### 2.2 编译固件

1. **配置目标**
   - Project → Options for Target
   - Device: STM32F746ZGTx
   - Clock: 216 MHz

2. **编译**
   ```
   Project → Build Target (F7)
   ```

3. **烧录**
   - 连接 ST-Link 下载器
   - Flash → Download (F8)

---

## 🔧 步骤 3: Python GUI 环境搭建

### 3.1 安装 Python

```bash
# Windows
# 从 https://www.python.org/downloads/ 下载 Python 3.9
# 安装时勾选 "Add Python to PATH"

# Linux
sudo apt install python3.9 python3-pip

# macOS
brew install python@3.9
```

### 3.2 安装依赖

```bash
cd 9_GUI
pip install -r requirements.txt
```

**依赖列表**:
```
PyQt5>=5.15.0
matplotlib>=3.4.0
numpy>=1.20.0
pyserial>=3.5
scipy>=1.7.0
```

### 3.3 测试 GUI

```bash
python main.py
```

**预期结果**:
- 弹出 GUI 窗口
- 可以看到模拟的距离剖面和距离-多普勒图
- 滑块可以调节方位角和俯仰角

---

## 🔧 步骤 4: 硬件连接检查

### 4.1 接线图

```
┌─────────────┐         ┌──────────────┐
│   PC/笔记本  │         │  RIS 雷达板   │
└──────┬──────┘         └───────┬──────┘
       │                        │
       │ USB                    │ USB-B
       ├────────────────────────┤
       
       │ JTAG                   │ JTAG
       ├────────────────────────┤
       
       │ SMA (可选,用于测试)     │ SMA 输入
       ├────────────────────────┤
```

### 4.2 上电前检查清单

- [ ] 所有电源线连接正确 (12V/5V/3.3V/1.8V/1.0V)
- [ ] 接地线连接良好
- [ ] SMA 连接器紧固
- [ ] FPGA 配置跳线正确
- [ ] STM32 复位按钮可访问

### 4.3 上电顺序

1. **接通 12V 电源**
2. **观察电源指示灯**
   - LED_PWR_OK 应亮起
3. **检查电压**
   ```bash
   # 使用万用表测量各电压轨
   12V ± 5%
   5V ± 5%
   3.3V ± 5%
   1.8V ± 3%
   1.0V ± 3%
   ```

---

## 🐛 常见问题排查

### 问题 1: FPGA 无法配置

**症状**: Vivado 提示 "Device not found"

**解决方法**:
1. 检查 JTAG 连接线
2. 确认 FPGA 供电正常 (1.8V/1.0V)
3. 重启 Vivado
4. 尝试手动添加设备: Open Hardware Manager → Add Device

### 问题 2: GUI 无法启动

**症状**: `python main.py` 报错

**解决方法**:
```bash
# 检查 Python 版本
python --version  # 应为 3.8+

# 重新安装依赖
pip uninstall PyQt5
pip install PyQt5

# 检查串口权限 (Linux)
sudo usermod -a -G dialout $USER
```

### 问题 3: 波束不扫描

**症状**: GUI 调节角度,但实际波束不动

**解决方法**:
1. 检查 SPI 通信是否正常
2. 使用 ILA 观察 FPGA 内部相位控制字
3. 确认 PIN 二极管和变容二极管供电正常

### 问题 4: 无目标回波

**症状**: 距离剖面全为噪声

**解决方法**:
1. 检查天线连接
2. 增加发射功率
3. 使用金属板作为测试目标 (距离 1-10m)
4. 调整 CFAR 阈值

---

## 📊 性能测试

### 测试 1: 波束指向精度

**方法**:
1. 设置方位角 = 30°
2. 使用矢量网络分析仪测量辐射方向图
3. 记录主瓣峰值位置

**合格标准**: 误差 < 1°

### 测试 2: 测距精度

**方法**:
1. 放置金属板在已知距离 (如 100m)
2. 读取 GUI 显示的距离值
3. 计算误差

**合格标准**: 误差 ≤ 5m

### 测试 3: 测速精度

**方法**:
1. 使用移动平台携带金属板 (速度 10 m/s)
2. 读取 GUI 显示的速度值
3. 计算误差

**合格标准**: 误差 ≤ 0.04 m/s

---

## 📚 进阶调试

### 使用 ILA 调试 FPGA

1. **插入 ILA 核**
   ```verilog
   // 在 Top_Module.v 中添加
   wire [31:0] debug_time;
   wire [31:0] debug_freq;
   
   ila_debug ila_inst (
       .clk(clk_100m),
       .probe0(debug_time),
       .probe1(debug_freq)
   );
   ```

2. **重新生成比特流**
3. **在 Hardware Manager 中触发采集**

### 使用逻辑分析仪调试 SPI

- 通道 0: SPI_CS
- 通道 1: SPI_CLK
- 通道 2: SPI_MOSI
- 通道 3: SPI_MISO

**解码协议**: SPI, MSB First, 8-bit

---

## 🎓 学习资源

- [Xilinx Vivado 教程](https://www.xilinx.com/training/vivado/vivado-design-methodology-for-fpga.htm)
- [STM32 HAL 库文档](https://www.st.com/en/embedded-software/stm32cube-mcu-mpu-packages.html)
- [PyQt5 官方文档](https://www.riverbankcomputing.com/docs/pyqt5/)
- [雷达原理教材](https://www.amazon.com/Introduction-Radar-Systems-Merrill-Skolnik/dp/0071419462)

---

**需要帮助?** 
- 提交 Issue: https://github.com/realsunmiao/PLFM-RIS-Enhanced/issues
- 查看原始项目: https://github.com/NawfalMotii79/PLFM_RADAR
