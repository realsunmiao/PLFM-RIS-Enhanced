################################################################################
# File: constraints.xdc
# Description: FPGA 引脚约束文件 - Artix-7 XC7A100T (CSG324 封装)
# 
# 硬件平台: 自定义 RIS 雷达控制板
# FPGA 型号: Xilinx Artix-7 XC7A100T-1CSG324
#
# 作者: Wukong AI Assistant
# 日期: 2026-08-19
################################################################################

# ============================================================================
# 时钟配置
# ============================================================================

# 100 MHz 系统时钟输入
set_property PACKAGE_PIN U18 [get_ports clk_100m]
set_property IOSTANDARD LVCMOS33 [get_ports clk_100m]
create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports clk_100m]

# ============================================================================
# SPI 通信接口 (与 STM32 通信)
# ============================================================================

set_property PACKAGE_PIN M14 [get_ports spi_cs]
set_property IOSTANDARD LVCMOS33 [get_ports spi_cs]

set_property PACKAGE_PIN N14 [get_ports spi_clk]
set_property IOSTANDARD LVCMOS33 [get_ports spi_clk]

set_property PACKAGE_PIN P14 [get_ports spi_mosi]
set_property IOSTANDARD LVCMOS33 [get_ports spi_mosi]

set_property PACKAGE_PIN R14 [get_ports spi_miso]
set_property IOSTANDARD LVCMOS33 [get_ports spi_miso]

# ============================================================================
# RIS 阵列控制输出 - PIN 二极管 (64 路, 1-bit per unit)
# ============================================================================

# Bank 15 (VCCO = 3.3V)
set_property PACKAGE_PIN A1  [get_ports {pin_ctrl[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[0]}]

set_property PACKAGE_PIN B1  [get_ports {pin_ctrl[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[1]}]

set_property PACKAGE_PIN C1  [get_ports {pin_ctrl[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[2]}]

set_property PACKAGE_PIN D1  [get_ports {pin_ctrl[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[3]}]

set_property PACKAGE_PIN E1  [get_ports {pin_ctrl[4]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[4]}]

set_property PACKAGE_PIN F1  [get_ports {pin_ctrl[5]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[5]}]

set_property PACKAGE_PIN G1  [get_ports {pin_ctrl[6]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[6]}]

set_property PACKAGE_PIN H1  [get_ports {pin_ctrl[7]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[7]}]

# Bank 16
set_property PACKAGE_PIN J1  [get_ports {pin_ctrl[8]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[8]}]

set_property PACKAGE_PIN K1  [get_ports {pin_ctrl[9]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[9]}]

set_property PACKAGE_PIN L1  [get_ports {pin_ctrl[10]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[10]}]

set_property PACKAGE_PIN M1  [get_ports {pin_ctrl[11]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[11]}]

set_property PACKAGE_PIN N1  [get_ports {pin_ctrl[12]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[12]}]

set_property PACKAGE_PIN P1  [get_ports {pin_ctrl[13]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[13]}]

set_property PACKAGE_PIN R1  [get_ports {pin_ctrl[14]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[14]}]

set_property PACKAGE_PIN T1  [get_ports {pin_ctrl[15]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[15]}]

# Bank 33
set_property PACKAGE_PIN A2  [get_ports {pin_ctrl[16]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[16]}]

set_property PACKAGE_PIN B2  [get_ports {pin_ctrl[17]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[17]}]

set_property PACKAGE_PIN C2  [get_ports {pin_ctrl[18]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[18]}]

set_property PACKAGE_PIN D2  [get_ports {pin_ctrl[19]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[19]}]

set_property PACKAGE_PIN E2  [get_ports {pin_ctrl[20]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[20]}]

set_property PACKAGE_PIN F2  [get_ports {pin_ctrl[21]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[21]}]

set_property PACKAGE_PIN G2  [get_ports {pin_ctrl[22]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[22]}]

set_property PACKAGE_PIN H2  [get_ports {pin_ctrl[23]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[23]}]

# Bank 34
set_property PACKAGE_PIN J2  [get_ports {pin_ctrl[24]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[24]}]

set_property PACKAGE_PIN K2  [get_ports {pin_ctrl[25]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[25]}]

set_property PACKAGE_PIN L2  [get_ports {pin_ctrl[26]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[26]}]

set_property PACKAGE_PIN M2  [get_ports {pin_ctrl[27]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[27]}]

set_property PACKAGE_PIN N2  [get_ports {pin_ctrl[28]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[28]}]

set_property PACKAGE_PIN P2  [get_ports {pin_ctrl[29]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[29]}]

set_property PACKAGE_PIN R2  [get_ports {pin_ctrl[30]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[30]}]

set_property PACKAGE_PIN T2  [get_ports {pin_ctrl[31]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[31]}]

# Bank 35
set_property PACKAGE_PIN A3  [get_ports {pin_ctrl[32]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[32]}]

set_property PACKAGE_PIN B3  [get_ports {pin_ctrl[33]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[33]}]

set_property PACKAGE_PIN C3  [get_ports {pin_ctrl[34]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[34]}]

set_property PACKAGE_PIN D3  [get_ports {pin_ctrl[35]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[35]}]

set_property PACKAGE_PIN E3  [get_ports {pin_ctrl[36]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[36]}]

set_property PACKAGE_PIN F3  [get_ports {pin_ctrl[37]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[37]}]

set_property PACKAGE_PIN G3  [get_ports {pin_ctrl[38]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[38]}]

set_property PACKAGE_PIN H3  [get_ports {pin_ctrl[39]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[39]}]

# Bank 36
set_property PACKAGE_PIN J3  [get_ports {pin_ctrl[40]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[40]}]

set_property PACKAGE_PIN K3  [get_ports {pin_ctrl[41]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[41]}]

set_property PACKAGE_PIN L3  [get_ports {pin_ctrl[42]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[42]}]

set_property PACKAGE_PIN M3  [get_ports {pin_ctrl[43]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[43]}]

set_property PACKAGE_PIN N3  [get_ports {pin_ctrl[44]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[44]}]

set_property PACKAGE_PIN P3  [get_ports {pin_ctrl[45]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[45]}]

set_property PACKAGE_PIN R3  [get_ports {pin_ctrl[46]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[46]}]

set_property PACKAGE_PIN T3  [get_ports {pin_ctrl[47]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[47]}]

# Bank 14
set_property PACKAGE_PIN A4  [get_ports {pin_ctrl[48]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[48]}]

set_property PACKAGE_PIN B4  [get_ports {pin_ctrl[49]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[49]}]

set_property PACKAGE_PIN C4  [get_ports {pin_ctrl[50]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[50]}]

set_property PACKAGE_PIN D4  [get_ports {pin_ctrl[51]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[51]}]

set_property PACKAGE_PIN E4  [get_ports {pin_ctrl[52]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[52]}]

set_property PACKAGE_PIN F4  [get_ports {pin_ctrl[53]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[53]}]

set_property PACKAGE_PIN G4  [get_ports {pin_ctrl[54]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[54]}]

set_property PACKAGE_PIN H4  [get_ports {pin_ctrl[55]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[55]}]

# Bank 13
set_property PACKAGE_PIN J4  [get_ports {pin_ctrl[56]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[56]}]

set_property PACKAGE_PIN K4  [get_ports {pin_ctrl[57]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[57]}]

set_property PACKAGE_PIN L4  [get_ports {pin_ctrl[58]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[58]}]

set_property PACKAGE_PIN M4  [get_ports {pin_ctrl[59]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[59]}]

set_property PACKAGE_PIN N4  [get_ports {pin_ctrl[60]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[60]}]

set_property PACKAGE_PIN P4  [get_ports {pin_ctrl[61]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[61]}]

set_property PACKAGE_PIN R4  [get_ports {pin_ctrl[62]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[62]}]

set_property PACKAGE_PIN T4  [get_ports {pin_ctrl[63]}]
set_property IOSTANDARD LVCMOS33 [get_ports {pin_ctrl[63]}]

# ============================================================================
# VarCap 串行控制 (通过移位寄存器扩展)
# ============================================================================

# 串行数据输出
set_property PACKAGE_PIN U1  [get_ports varcap_data]
set_property IOSTANDARD LVCMOS33 [get_ports varcap_data]

# 串行时钟
set_property PACKAGE_PIN V1  [get_ports varcap_clock]
set_property IOSTANDARD LVCMOS33 [get_ports varcap_clock]

# 锁存信号
set_property PACKAGE_PIN W1  [get_ports varcap_latch]
set_property IOSTANDARD LVCMOS33 [get_ports varcap_latch]

# ============================================================================
# 状态指示 LED
# ============================================================================

set_property PACKAGE_PIN U2  [get_ports led_ready]
set_property IOSTANDARD LVCMOS33 [get_ports led_ready]

set_property PACKAGE_PIN V2  [get_ports led_active]
set_property IOSTANDARD LVCMOS33 [get_ports led_active]

# ============================================================================
# 复位按钮
# ============================================================================

set_property PACKAGE_PIN W2  [get_ports rst_n]
set_property IOSTANDARD LVCMOS33 [get_ports rst_n]

# ============================================================================
# 时序约束
# ============================================================================

# 设置输入延迟
set_input_delay -clock [get_clocks sys_clk] -max 2.0 [get_ports spi_*]
set_input_delay -clock [get_clocks sys_clk] -min 0.5 [get_ports spi_*]

# 设置输出延迟
set_output_delay -clock [get_clocks sys_clk] -max 2.0 [get_ports pin_ctrl*]
set_output_delay -clock [get_clocks sys_clk] -min 0.5 [get_ports pin_ctrl*]

# ============================================================================
# 伪路径 (False Paths)
# ============================================================================

# SPI 异步接口,设置为伪路径
set_false_path -from [get_ports spi_cs]
set_false_path -from [get_ports spi_clk]

# 复位异步,设置为伪路径
set_false_path -from [get_ports rst_n]
