# STM32 工程配置指南

> **本文档说明如何使用 CubeMX 生成 STM32F746 工程并编译固件**

---

## 🛠️ 前置要求

### 软件安装

1. **STM32CubeMX**
   - 下载: https://www.st.com/en/development-tools/stm32cubemx.html
   - 版本: 6.9.0 或更高
   - 安装 Java Runtime (JRE 8+)

2. **Keil uVision 5**
   - 下载: https://www.keil.com/demo/eval/arm.htm
   - 安装 STM32F7 支持包 (Pack Installer)

3. **STM32CubeProgrammer**
   - 用于烧录固件
   - 下载: https://www.st.com/en/development-tools/stm32cubeprog.html

---

## ⚙️ CubeMX 配置步骤

### 1. 创建新工程

```
File → New Project
→ MCU Selector → STM32F746ZGTx
→ Start Project
```

### 2. Pinout & Configuration

#### System Core

**RCC (时钟)**:
- High Speed Clock (HSE): Crystal/Ceramic Resonator
- LSE: Disable

**SYS**:
- Debug: Serial Wire
- Timebase Source: TIM6 (避免使用 SysTick)

**GPIO**:
```
Pin         Mode            Label
─────────────────────────────────
PA0         Analog          ADC1_IN0 (温度传感器)
PA1         Analog          ADC1_IN1 (电压检测)
PB0         Output Push Pull LED_STATUS
PB1         Output Push Pull LED_PWR_OK
PC0         Output Push Pull PWR_12V_EN
PC1         Output Push Pull PWR_5V_EN
PC2         Output Push Pull PWR_3V3_EN
PC3         Output Push Pull PWR_1V8_EN
PC4         Output Push Pull PWR_1V0_EN
PA5         AF5             SPI1_SCK
PA6         AF5             SPI1_MISO
PA7         AF5             SPI1_MOSI
PA4         Output Push Pull SPI1_CS
PB6         AF7             USART1_TX
PB7         AF7             USART1_RX
```

#### Connectivity

**SPI1**:
- Mode: Full-Duplex Master
- Data Size: 8 bits
- First Bit: MSB First
- Prescaler: 16 (6.75 MHz @ 108 MHz APB2)
- CPOL: Low
- CPHA: 1 Edge

**USART1**:
- Mode: Asynchronous
- Baud Rate: 115200
- Word Length: 8 Bits
- Parity: None
- Stop Bits: 1

#### Analog

**ADC1**:
- Resolution: 12 bits
- Data Alignment: Right
- Scan Conversion Mode: Enable
- Continuous Conversion Mode: Disable
- Number of Conversion: 2
- Channel 0: ADC_CHANNEL_TEMPSENSOR
- Channel 1: ADC_CHANNEL_1

### 3. Clock Configuration

```
HSE: 25 MHz (外部晶振)
PLL Source Mux: HSE
PLL M: 25
PLL N: 432
PLL P: 2
System Clock Mux: PLLCLK

结果:
  SYSCLK: 216 MHz
  HCLK: 216 MHz
  PCLK1: 54 MHz (APB1)
  PCLK2: 108 MHz (APB2)
```

### 4. Project Manager

**Project**:
- Project Name: STM32F746_RIS_Control
- Project Location: `5_Control_Circuit/`
- Toolchain / IDE: MDK-ARM (Keil)
- Minimum Heap Size: 0x400
- Minimum Stack Size: 0x800

**Code Generator**:
- ☑ Generate peripheral initialization as a pair of '.c/.h' files
- ☑ Keep User Code when re-generating
- Back-up previously generated user files: ✓

### 5. 生成代码

```
Project → Generate Code (Alt + K)
```

生成的文件位于 `5_Control_Circuit/`:
```
STM32F746_RIS_Control/
├── MDK-ARM/
│   ├── STM32F746_RIS_Control.uvprojx  ← Keil 工程文件
│   └── ...
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── stm32f7xx_hal_conf.h
│   │   └── stm32f7xx_it.h
│   └── Src/
│       ├── main.c
│       ├── stm32f7xx_hal_msp.c
│       └── stm32f7xx_it.c
├── Drivers/
│   ├── CMSIS/
│   └── STM32F7xx_HAL_Driver/
└── STM32F746_RIS_Control.ioc  ← CubeMX 配置文件
```

---

## 🔨 Keil 编译步骤

### 1. 打开工程

```
File → Open → 5_Control_Circuit/MDK-ARM/STM32F746_RIS_Control.uvprojx
```

### 2. 添加用户代码

将之前创建的源文件复制到工程中:

```
5_Control_Circuit/Src/main.c           → 替换生成的 main.c
5_Control_Circuit/Src/power_seq.c      → 添加到工程
5_Control_Circuit/Inc/power_seq.h      → 添加到工程
5_Control_Circuit/Src/fpga_config.c    → 添加到工程
5_Control_Circuit/Inc/fpga_config.h    → 添加到工程
5_Control_Circuit/Src/monitor.c        → 添加到工程
5_Control_Circuit/Inc/monitor.h        → 添加到工程
```

**在 Keil 中添加文件**:
```
Project Window → 右键 "Source Group 1" → Add Existing Files
选择上述 .c 和 .h 文件
```

### 3. 配置编译选项

```
Project → Options for Target (Alt + F7)

C/C++ 标签页:
  - Define: USE_HAL_DRIVER,STM32F746xx
  - Include Paths: 添加 ../Core/Inc, ../Drivers/...

Linker 标签页:
  - Use Memory Layout from Target Dialog: ✓
```

### 4. 编译工程

```
Project → Build Target (F7)
```

**预期输出**:
```
Build target 'Target 1'
compiling main.c...
compiling power_seq.c...
compiling fpga_config.c...
linking...
Program Size: Code=12456 RO-data=348 RW-data=128 ZI-data=2048
".\Objects\STM32F746_RIS_Control.axf" - 0 Error(s), 0 Warning(s).
```

### 5. 生成 HEX 文件

```
Project → Options for Target → Output
☑ Create HEX File
```

重新编译后生成 `STM32F746_RIS_Control.hex`

---

## 💾 烧录固件

### 方法 1: ST-Link Utility

1. **连接硬件**
   - ST-Link V2 连接到 SWD 接口
   - USB 连接到电脑

2. **打开 ST-Link Utility**
   ```
   Target → Connect
   ```

3. **烧录**
   ```
   Target → Program & Verify
   选择 STM32F746_RIS_Control.hex
   Start
   ```

### 方法 2: Keil 直接下载

```
Flash → Download (F8)
```

### 方法 3: STM32CubeProgrammer

```
Connect → ST-LINK
Erase Chip
Upload File → 选择 .hex 文件
Start Programming
```

---

## 🐛 调试技巧

### 使用 Keil 调试器

1. **启动调试**
   ```
   Debug → Start/Stop Debug Session (Ctrl + F5)
   ```

2. **设置断点**
   - 双击代码行号左侧
   - 红色圆点表示断点

3. **观察变量**
   ```
   View → Watch Windows → Watch 1
   添加变量名 (如: temperature, voltage)
   ```

4. **单步执行**
   - Step Over (F10)
   - Step Into (F11)
   - Run (F5)

### 常见问题

**Q: 烧录失败 "Cannot connect to target"**

A: 
1. 检查 ST-Link 连接
2. 确认 SWDIO/SWCLK 接线正确
3. 检查目标板供电 (3.3V 是否正常)

**Q: 程序运行后立即复位**

A:
1. 检查看门狗是否喂狗
2. 检查栈溢出 (增加 Stack Size)
3. 检查未初始化指针

---

## 📚 参考资源

- [STM32F746 Reference Manual](https://www.st.com/resource/en/reference_manual/dm00105262.pdf)
- [STM32CubeMX 用户手册](https://www.st.com/resource/en/user_manual/um1718-stm32cubemx-for-stm32-configuration-and-initialization-c-code-generation-stmicroelectronics.pdf)
- [Keil uVision 教程](https://www.keil.com/support/man/docs/uv4/uv4.htm)

---

**完成以上步骤后,STM32 固件即可正常运行!**
