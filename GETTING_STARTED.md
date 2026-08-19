# 新人复现操作指南 - PLFM-RIS-Enhanced

> **从零开始,手把手教你复现 RIS 雷达系统**  
> 预计总耗时: 软件仿真 1 小时 | 完整硬件 2-4 周

---

## 🎯 快速导航

根据你的资源和目标选择路径:

| 路径 | 适合人群 | 耗时 | 成本 | 产出 |
|-----|---------|------|------|------|
| **[路径 A](#路径-a-软件仿真验证)** | 学生/研究者/算法工程师 | 1-2 小时 | ¥0 | 仿真结果 + 论文素材 |
| **[路径 B](#路径-b-fpga-开发验证)** | FPGA 工程师/电子爱好者 | 3-5 天 | ¥500-800 | FPGA 比特流 + 波形验证 |
| **[路径 C](#路径-c-完整硬件复现)** | 硬件团队/创业公司 | 2-4 周 | ¥3000-5000 | 实物样机 + 测试数据 |

---

## 📋 前置检查清单

在开始之前,请确认你具备以下条件:

### 通用要求 (所有路径)
- [ ] Windows 10/11 或 Linux 电脑
- [ ] 至少 50 GB 可用硬盘空间
- [ ] 稳定的网络连接 (下载大型软件)
- [ ] 基本的命令行操作知识

### 路径 B/C 额外要求
- [ ] FPGA 开发板 (Xilinx Artix-7 XC7A100T)
- [ ] JTAG 下载器
- [ ] 示波器或逻辑分析仪 (可选,用于调试)

### 路径 C 额外要求
- [ ] PCB 打板预算 (~¥2000)
- [ ] 元器件采购预算 (~¥2000)
- [ ] 焊接工具 (电烙铁、焊锡、助焊剂)
- [ ] 万用表、VNA (矢量网络分析仪,可选)

---

## 路径 A: 软件仿真验证

**目标**: 验证核心算法,生成论文图表  
**无需任何硬件**,纯软件环境

### 步骤 1: 安装 Python 环境 (10 分钟)

#### Windows 用户
```bash
# 1. 下载 Python 3.9
访问: https://www.python.org/downloads/release/python-3913/
下载 "Windows installer (64-bit)"

# 2. 安装时务必勾选 "Add Python to PATH"

# 3. 验证安装
python --version
# 应输出: Python 3.9.13
```

#### Linux 用户
```bash
sudo apt update
sudo apt install python3.9 python3-pip
```

#### macOS 用户
```bash
brew install python@3.9
```

### 步骤 2: 克隆项目代码 (5 分钟)

```bash
# 方法 1: 使用 Git
git clone https://github.com/realsunmiao/PLFM-RIS-Enhanced.git
cd PLFM-RIS-Enhanced

# 方法 2: 直接下载 ZIP
访问: https://github.com/realsunmiao/PLFM-RIS-Enhanced/archive/refs/heads/main.zip
解压后进入目录
```

### 步骤 3: 安装依赖包 (5 分钟)

```bash
pip install numpy scipy matplotlib
```

**验证安装**:
```python
python -c "import numpy; import scipy; import matplotlib; print('All packages installed!')"
```

### 步骤 4: 运行仿真脚本 (10 分钟)

```bash
cd 6_Simulation
python stc_simulation.py
```

**预期输出**:
```
============================================================
PLFM-RIS 雷达系统仿真
============================================================
载频: 10.5 GHz
带宽: 100 MHz
脉冲宽度: 10 μs
目标距离: 500 m
目标速度: 10 m/s
波束指向: 方位角 30°, 俯仰角 0°
============================================================

[1/4] 生成 LFM 信号...
  信号长度: 2000 采样点
[2/4] 计算波束方向图...
[3/4] 模拟目标回波并进行脉冲压缩...
  理论距离分辨率: 1.50 m
[4/4] 距离-多普勒处理...

生成可视化图表...
  已保存: stc_simulation_result.png

============================================================
仿真完成!
============================================================
```

### 步骤 5: 查看结果

仿真完成后会自动弹出 4 个子图:

1. **LFM 信号时域波形** - 验证线性调频特性
2. **波束方向图** - 验证 ±60° 扫描能力
3. **脉冲压缩结果** - 验证距离分辨率 (应看到 500m 处的尖峰)
4. **距离-多普勒图** - 验证速度测量 (应看到 10 m/s 处的亮点)

同时会在 `6_Simulation/` 目录下生成 `stc_simulation_result.png` 文件。

### ✅ 路径 A 完成标志

- [ ] 成功运行仿真脚本无报错
- [ ] 看到 4 个子图的可视化结果
- [ ] 保存了 `stc_simulation_result.png`

**下一步**: 
- 撰写论文时使用这些图表
- 修改参数 (如目标距离、速度) 进行敏感性分析
- 或者继续 [路径 B](#路径-b-fpga-开发验证) 进行硬件验证

---

## 路径 B: FPGA 开发验证

**目标**: 在 FPGA 上实现 STC 算法,验证实时性能  
**需要**: FPGA 开发板 + Vivado 软件

### 步骤 1: 安装 Vivado (30-60 分钟,仅需一次)

#### 下载 Vivado
```
访问: https://www.xilinx.com/support/download.html
选择: Vivado ML Standard 2020.1 (免费 WebPACK 版本)
下载大小: ~30 GB
```

#### 安装步骤
1. 运行 `Xilinx_Vivado_2020.1_Win64.exe`
2. 选择组件:
   - ✅ Vivado HL Design Edition
   - ✅ Artix-7 系列支持
   - ✅ Device Programming Utilities
   - ❌ Zynq UltraScale+ (不需要,节省空间)
3. 等待安装完成 (~30 分钟)

#### 申请许可证
```
启动 Vivado
Help → Manage License
点击 "Get Free WebPACK License"
登录 Xilinx 账号 (没有则注册)
下载 .lic 文件并加载
```

### 步骤 2: 准备 FPGA 硬件

#### 推荐开发板
- **Digilent Arty A7-100T** ($299)
  - 型号: Artix-7 XC7A100T-1CSG324
  - 购买链接: https://digilent.com/reference/programmable-logic/arty-a7/start
  - 特点: 开箱即用,自带 JTAG 下载器

- **自制开发板** (参考本项目 PCB 设计)
  - 成本: ~$150
  - 需要自行打板和焊接

#### 连接硬件
```
1. USB 线连接开发板到电脑
2. 观察 LED 是否亮起 (供电正常)
3. 打开设备管理器,确认出现 "Xilinx USB Cable"
```

### 步骤 3: 生成 Vivado 工程 (10 分钟)

#### 方法 1: 使用 Tcl 脚本 (推荐)
```bash
# 打开 Vivado Tcl Console
vivado -mode tcl

# 运行自动化脚本
source 4_STC_Firmware/create_vivado_project.tcl
```

脚本会自动:
- 创建工程 `PLFM_RIS_Project`
- 添加所有 Verilog 源文件
- 加载引脚约束 `constraints.xdc`
- 运行综合和实现
- 生成比特流 `.bit` 文件

#### 方法 2: 手动创建工程
```
File → New Project
Project Name: PLFM_RIS_Project
Project Type: RTL Project
Part: xc7a100tcsg324-1
Add Sources: 选择 4_STC_Firmware/*.v
Add Constraints: 选择 4_STC_Firmware/constraints.xdc
Finish
```

### 步骤 4: 生成比特流 (20-30 分钟)

在 Vivado GUI 中:
```
Flow Navigator → Generate Bitstream
等待综合、实现、比特流生成完成
```

**检查 Timing Report**:
```
Reports → Report Timing Summary
确保 WNS (Worst Negative Slack) > 0
如有违例,需优化代码或降低时钟频率
```

### 步骤 5: 烧录 FPGA (5 分钟)

```
Open Hardware Manager → Auto Connect
右键 FPGA 芯片 → Program Device
选择生成的 .bit 文件
点击 "Program"
```

**验证烧录成功**:
- 观察开发板 LED 闪烁
- 使用 ILA (Integrated Logic Analyzer) 观察内部信号

### 步骤 6: 测试 SPI 通信 (10 分钟)

使用 Python GUI 测试与 FPGA 的通信:

```bash
cd 9_GUI
pip install -r requirements.txt
python main.py
```

在 GUI 中:
1. 选择串口 (COMx)
2. 点击 "Connect"
3. 调节方位角滑块 (0-60°)
4. 观察 FPGA 内部相位控制字变化 (通过 ILA)

### ✅ 路径 B 完成标志

- [ ] Vivado 工程成功生成比特流
- [ ] Timing Report 无违例
- [ ] 比特流成功烧录到 FPGA
- [ ] SPI 通信正常,GUI 可控制 FPGA

**下一步**: 
- 使用示波器观测实际输出的 RF 信号
- 或者继续 [路径 C](#路径-c-完整硬件复现) 构建完整系统

---

## 路径 C: 完整硬件复现

**目标**: 从零制作 RIS 雷达实物样机  
**需要**: PCB 打板 + 元器件采购 + 焊接 + 联调

### ⚠️ 重要提示

路径 C 难度较高,建议:
- 有 PCB 设计和焊接经验
- 或有团队成员分工合作
- 预算充足 (¥3000-5000)

如果不确定,建议先完成 [路径 A](#路径-a-软件仿真验证) 和 [路径 B](#路径-b-fpga-开发验证)。

---

### 阶段 1: 采购元器件 (3-5 天)

#### 步骤 1.1: 导出 BOM 清单

打开 `2_RIS_Antenna_Design/BOM.csv`,你会看到完整的物料清单。

#### 步骤 1.2: 核心元器件采购

**优先级 1: 高频器件 (必须从正规渠道购买)**

| 器件 | 型号 | 数量 | 单价 | 总价 | 供应商 |
|-----|------|------|------|------|--------|
| PIN 二极管 | MA4P7454B-402T | 64 | $0.85 | $54.40 | DigiKey/Mouser |
| 变容二极管 | SMV1235-083LF | 64 | $1.20 | $76.80 | DigiKey/Mouser |
| SMA 连接器 | 142-0701-801 | 1 | $3.50 | $3.50 | DigiKey |

**购买链接**:
- DigiKey 中国: https://www.digikey.cn/
- Mouser 中国: https://www.mouser.cn/

**注意事项**:
- ⚠️ **不要**从淘宝/拼多多购买射频器件 (假货率高)
- ⚠️ 注意封装尺寸 (SOD-323)
- ⚠️ 预留 10% 余量 (多买 6-7 个备用)

**优先级 2: 通用元器件 (可从立创商城购买)**

```
访问: https://szlcsc.com/
搜索以下器件:
- 0603LS-102XGLC (RF 电感) × 128
- 0402CG100JAT2A (DC 隔直电容) × 128
- CRCW0603F1000FKEA (100Ω 电阻) × 63
```

**优先级 3: IC 芯片**

| 器件 | 型号 | 数量 | 单价 | 供应商 |
|-----|------|------|------|--------|
| FPGA | XC7A100T-1CSG324 | 1 | $45 | Mouser/DigiKey |
| STM32 | STM32F746ZGT6 | 1 | $12 | Mouser/DigiKey |
| 移位寄存器 | SN74HC595NSR | 8 | $0.35 | 立创商城 |
| DC-DC | TPS54330DRCT | 1 | $2.50 | 立创商城 |

**总采购成本**: ~$250-300 (约 ¥1800-2200)

### 阶段 2: PCB 打板 (5-7 天)

#### 步骤 2.1: 设计 PCB

**选项 A: 使用本项目的 KiCad 模板 (推荐新手)**

由于 KiCad 工程文件较大,请参考:
```
2_RIS_Antenna_Design/PCB_DESIGN_GUIDE.md
```

按照文档中的叠层结构和尺寸要求设计。

**选项 B: 委托专业设计师**

如果时间紧迫,可以:
- 在闲鱼/淘宝找 PCB 设计师
- 提供本项目的设计指南
- 费用: ¥500-1000

#### 步骤 2.2: 导出 Gerber 文件

参考 `2_RIS_Antenna_Design/GERBER_MANUFACTURING_GUIDE.md` 导出。

#### 步骤 2.3: 下单打板

**推荐厂家: 嘉立创 (JLCPCB)**

```
访问: https://jlcpcb.com/
上传: Gerber ZIP 文件
设置参数:
  - 层数: 6 层
  - 板材: Rogers 4350B (需在备注中说明)
  - 尺寸: 100 × 100 mm
  - 数量: 10 pcs
  - 铜厚: 1 oz
  - 表面处理: ENIG
  - 阻抗控制: 是 (50 Ω ±10%)

特殊备注:
"请使用 Rogers 4350B + 4003C 混合叠层,介电常数 εr=3.48±0.05,
需提供阻抗测试报告。"
```

**费用**: ~$150-200 (约 ¥1100-1500)  
**交期**: 3-5 天 + 快递 2-3 天

### 阶段 3: 焊接组装 (2-3 天)

#### 步骤 3.1: 准备焊接工具

```
必需:
- 恒温电烙铁 (推荐 Hakko FX-888D, ¥300)
- 焊锡丝 (0.6mm,含铅更易焊)
- 助焊剂 (松香或 Flux Pen)
- 镊子 (尖头)
- 放大镜或显微镜
- 吸锡带 (清理短路)

可选:
- 热风枪 (焊接 SMA 连接器)
- BGA 返修台 (如果需要焊接 FPGA)
```

#### 步骤 3.2: 焊接顺序

**第 1 步: 贴装无源器件 (回流焊或手工)**
```
1. 涂抹锡膏 (如果使用回流焊)
2. 放置电阻、电容、电感
3. 回流焊 (温度曲线: 预热 150°C/60s → 峰值 245°C/30s → 冷却)
```

**第 2 步: 焊接 PIN/变容二极管 (手工,最关键!)**
```
⚠️ 注意极性! 参考 datasheet 确认正负极

技巧:
1. 先在焊盘上镀少量锡
2. 用镊子夹住二极管
3. 烙铁加热一侧焊盘,推入二极管
4. 再焊另一侧
5. 用万用表二极管档测试导通性
```

**第 3 步: 焊接 IC 芯片**
```
FPGA 和 STM32 建议使用热风枪或 BGA 返修台
如无经验,建议购买已焊接好的最小系统板
```

**第 4 步: 安装连接器**
```
SMA 连接器: 垂直安装,确保良好接地
USB/JTAG: 注意方向
```

#### 步骤 3.3: 焊接后检查

```
1. 目视检查: 无虚焊、短路、焊锡球
2. 万用表测试:
   - 各电源轨对地电阻 > 1 kΩ (无短路)
   - PIN 二极管正向导通 (~0.7V),反向截止
3. 施加 3.3V,测量静态电流 (< 10 mA)
```

### 阶段 4: 固件烧录 (1 天)

#### 步骤 4.1: 烧录 FPGA

参考 [路径 B 步骤 5](#步骤-5-烧录-fpga-5-分钟)

#### 步骤 4.2: 烧录 STM32

参考 `5_Control_Circuit/STM32_SETUP_GUIDE.md`

### 阶段 5: 系统联调 (2-3 天)

#### 步骤 5.1: 上电测试

```
1. 连接 12V 电源
2. 观察电源指示灯 (LED_PWR_OK 应亮起)
3. 用万用表测量各电压轨:
   12V ± 5%
   5V ± 5%
   3.3V ± 5%
   1.8V ± 3%
   1.0V ± 3%
```

#### 步骤 5.2: RF 性能测试

**使用 VNA (矢量网络分析仪)**:
```
1. 连接 VNA 到 SMA 端口
2. 测量 S11 (@ 10.5 GHz)
3. 预期: S11 < -10 dB (良好匹配)
```

**如无 VNA,使用简易方法**:
```
1. 放置金属板在 1-5m 处
2. 运行 Python GUI
3. 观察距离剖面是否有明显峰值
```

#### 步骤 5.3: 波束扫描测试

```
1. 在 GUI 中调节方位角 (0° → 60°)
2. 观察目标回波强度变化
3. 最大回波应在设定角度附近
```

### ✅ 路径 C 完成标志

- [ ] PCB 成功打板并焊接完成
- [ ] 各电压轨正常,无短路
- [ ] FPGA 和 STM32 固件烧录成功
- [ ] VNA 测试 S11 < -10 dB
- [ ] GUI 可检测到目标并显示距离剖面
- [ ] 波束可扫描 ±60°

**恭喜! 你已成功复现 RIS 雷达系统!** 🎉

---

## 🐛 常见问题排查

### 问题 1: Python 仿真报错 "ModuleNotFoundError"

**解决**:
```bash
pip install --upgrade numpy scipy matplotlib
```

### 问题 2: Vivado 综合失败 "Syntax Error"

**解决**:
- 检查 Verilog 代码语法
- 确认所有模块文件已添加
- 查看 Console 窗口的具体错误行号

### 问题 3: FPGA 烧录失败 "Device not found"

**解决**:
1. 检查 JTAG 连接线
2. 确认 FPGA 供电 (1.8V/1.0V)
3. 重启 Vivado
4. 尝试手动添加设备

### 问题 4: PCB 收到后发现短路

**解决**:
1. 用万用表蜂鸣档定位短路点
2. 用吸锡带清理多余焊锡
3. 用酒精清洗 PCB
4. 如无法修复,联系厂家返工

### 问题 5: 检测不到目标回波

**解决**:
1. 检查天线连接是否牢固
2. 增加发射功率 (调整 FPGA 配置)
3. 使用更大的金属板 (如 30×30 cm)
4. 缩短测试距离 (从 1m 开始)
5. 调整 CFAR 阈值 (在 GUI 中)

---

## 📚 学习资源

### 视频教程
- [Vivado 入门教程](https://www.bilibili.com/video/BV1xx411c7mD)
- [KiCad PCB 设计教程](https://www.bilibili.com/video/BV1pt4y197YJ)
- [STM32 CubeMX 教程](https://www.bilibili.com/video/BV1th411z7sn)

### 文档
- [Xilinx Artix-7 Data Sheet](https://www.xilinx.com/support/documentation/data_sheets/ds181_Artix_7_Data_Sheet.pdf)
- [STM32F746 Reference Manual](https://www.st.com/resource/en/reference_manual/dm00105262.pdf)
- [Rogers PCB Material Guide](https://rogerscorp.com/resources/)

### 社区
- GitHub Issues: https://github.com/realsunmiao/PLFM-RIS-Enhanced/issues
- 原始项目: https://github.com/NawfalMotii79/PLFM_RADAR

---

## 🎓 进阶挑战

完成基础复现后,可以尝试:

1. **优化算法**: 改进 STC 编码策略,提升波束精度
2. **扩展频段**: 适配到 16.7 GHz 或更高
3. **增大阵列**: 从 8×8 扩展到 16×16
4. **融合通信**: 实现 JRC (Joint Radar and Communication)
5. **AI 增强**: 使用深度学习优化目标检测

---

## 💬 获取帮助

遇到问题? 

1. **查阅文档**: 本项目包含详细的设计指南
2. **提交 Issue**: https://github.com/realsunmiao/PLFM-RIS-Enhanced/issues
3. **参考原始项目**: https://github.com/NawfalMotii79/PLFM_RADAR
4. **邮件联系**: realsunmiao@example.com

---

<div align="center">

**祝你复现成功!** 🚀

如果这个项目对你有帮助,请给个 Star ⭐

[⬆ 返回顶部](#新人复现操作指南---plfm-ris-enhanced)

</div>
