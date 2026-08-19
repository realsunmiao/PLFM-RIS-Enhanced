################################################################################
# File: create_vivado_project.tcl
# Description: 自动化创建 Vivado 工程脚本
# 
# 使用方法:
#   1. 打开 Vivado Tcl Console
#   2. 运行: source create_vivado_project.tcl
#   3. 工程将自动创建在 4_STC_Firmware/PLFM_RIS_Project/
#
# 作者: Wukong AI Assistant
# 日期: 2026-08-19
################################################################################

# ============================================================================
# 参数配置
# ============================================================================
set project_name "PLFM_RIS_Project"
set project_dir "./4_STC_Firmware/${project_name}"
set part_name "xc7a100tcsg324-1"  ;# Artix-7 XC7A100T
set top_module "Top_Module"

# ============================================================================
# 创建工程
# ============================================================================
puts "=========================================="
puts "Creating Vivado Project: ${project_name}"
puts "=========================================="

create_project ${project_name} ${project_dir} -part ${part_name} -force

# 设置工程属性
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]

# ============================================================================
# 添加源文件
# ============================================================================
puts "Adding source files..."

# FPGA 固件源文件
set src_files [list \
    "../STC_Encoder.v" \
    "../Top_Module.v" \
    "../SPI_Interface.v" \
]

foreach file ${src_files} {
    if {[file exists $file]} {
        add_files -norecurse $file
        puts "  Added: $file"
    } else {
        puts "  WARNING: File not found: $file"
    }
}

# ============================================================================
# 添加约束文件
# ============================================================================
puts "Adding constraint files..."

if {[file exists "../constraints.xdc"]} {
    add_files -norecurse ../constraints.xdc
    set_property file_type XDC [get_files ../constraints.xdc]
    puts "  Added: constraints.xdc"
} else {
    puts "  WARNING: constraints.xdc not found, will create default"
}

# ============================================================================
# 创建设计运行
# ============================================================================
puts "Creating design runs..."

# 综合运行
launch_runs synth_1 -jobs 4
wait_on_run synth_1

# 实现运行
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1

# ============================================================================
# 生成报告
# ============================================================================
puts "Generating reports..."

# Timing 报告
open_run impl_1
report_timing_summary -file ${project_dir}/timing_summary.rpt
report_utilization -file ${project_dir}/utilization.rpt

# ============================================================================
# 完成
# ============================================================================
puts "=========================================="
puts "Project created successfully!"
puts "Project location: ${project_dir}"
puts "Bitstream: ${project_dir}/${project_name}.runs/impl_1/${top_module}.bit"
puts "=========================================="

# 打开工程
start_gui
