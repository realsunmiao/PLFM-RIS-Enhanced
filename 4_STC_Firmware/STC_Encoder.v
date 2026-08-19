////////////////////////////////////////////////////////////////////////////////
// Module: STC_Encoder.v
// Description: 时空编码(STC)核心模块 - 生成空间编码和时问编码相位序列
// 
// 功能:
//   1. 空间编码: 计算每个 RIS 单元的波束赋形相位
//   2. 时间编码: 生成 LFM 波形所需的时变相位
//   3. 输出: 64 路相位控制字 (PIN + VarCap)
//
// 作者: Wukong AI Assistant
// 日期: 2026-08-19
////////////////////////////////////////////////////////////////////////////////

module STC_Encoder (
    input wire          clk,            // 系统时钟 (100 MHz)
    input wire          rst_n,          // 复位信号 (低有效)
    input wire          enable,         // 使能信号
    
    // 波束指向参数
    input wire [15:0]   azimuth_angle,  // 方位角 (0-360°, 16-bit fixed point)
    input wire [15:0]   elevation_angle,// 俯仰角 (-90°~+90°, 16-bit signed)
    
    // LFM 波形参数
    input wire [31:0]   f0,             // 起始频率 (Hz)
    input wire [31:0]   k_slope,        // 调频斜率 (Hz/s)
    input wire [31:0]   T_period,       // 调频周期 (samples)
    
    // 输出: 64 路相位控制
    output reg [63:0]   pin_control,    // PIN 二极管控制 (1-bit per unit)
    output reg [511:0]  varcap_control  // 变容二极管控制 (8-bit per unit)
);

// ============================================================================
// 参数定义
// ============================================================================
localparam NUM_UNITS = 64;          // RIS 单元总数 (8x8)
localparam ROWS = 8;                // 行数
localparam COLS = 8;                // 列数
localparam PHASE_BITS = 12;         // 相位量化位数 (12-bit DAC)
localparam PI_FIXED = 16'h3243;     // π 的定点表示 (Q1.15 format)

// ============================================================================
// 内部信号
// ============================================================================
reg [31:0] time_counter;            // 时间计数器
wire [31:0] current_time;           // 当前时间戳
wire [31:0] instantaneous_freq;     // 瞬时频率 f(t) = f0 + k*t

// 空间相位存储 (64 x 12-bit)
reg [PHASE_BITS-1:0] spatial_phase [0:NUM_UNITS-1];

// 时间相位累加器
reg [31:0] phase_accumulator;

// ============================================================================
// 时间编码器: 生成 LFM 时变相位
// ============================================================================
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        time_counter <= 32'd0;
        phase_accumulator <= 32'd0;
    end else if (enable) begin
        // 时间计数器递增
        time_counter <= time_counter + 32'd1;
        
        // 计算瞬时频率: f(t) = f0 + k * t
        // 简化: 使用相位加法实现积分
        phase_accumulator <= phase_accumulator + f0 + (k_slope * time_counter[15:0]);
        
        // 周期重置
        if (time_counter >= T_period) begin
            time_counter <= 32'd0;
            phase_accumulator <= 32'd0;
        end
    end
end

assign instantaneous_freq = f0 + (k_slope * time_counter[15:0]);
assign current_time = time_counter;

// ============================================================================
// 空间编码器: 计算波束赋形相位
// ============================================================================
// 相位公式: φ_mn = (2π/λ) * (x_m*sinθ*cosφ + y_n*sinθ*sinφ)
// 
// 简化实现: 使用查找表 (LUT) 预计算常用角度的 sin/cos 值

function automatic real sin_lookup(input [15:0] angle_deg);
    // 简化的正弦查找表 (实际应使用 CORDIC 或完整 LUT)
    real angle_rad;
    angle_rad = angle_deg * 3.14159265 / 180.0;
    sin_lookup = $sin(angle_rad);
endfunction

function automatic real cos_lookup(input [15:0] angle_deg);
    real angle_rad;
    angle_rad = angle_deg * 3.14159265 / 180.0;
    cos_lookup = $cos(angle_rad);
endfunction

// 计算空间相位 (组合逻辑)
always @(*) begin
    integer m, n;
    real sin_az, cos_az, sin_el, cos_el;
    real x_pos, y_pos;
    real spatial_phase_real;
    
    // 计算三角函数值
    sin_az = sin_lookup(azimuth_angle);
    cos_az = cos_lookup(azimuth_angle);
    sin_el = sin_lookup(elevation_angle);
    cos_el = cos_lookup(elevation_angle);
    
    // 遍历所有单元
    for (m = 0; m < ROWS; m = m + 1) begin
        for (n = 0; n < COLS; n = n + 1) begin
            // 计算单元位置 (假设间距为 lambda/2)
            x_pos = n * 0.5;  // 归一化位置
            y_pos = m * 0.5;
            
            // 计算空间相位
            spatial_phase_real = 2.0 * 3.14159265 * (
                x_pos * sin_el * cos_az + 
                y_pos * sin_el * sin_az
            );
            
            // 转换为定点数 (12-bit, 0-2π 映射到 0-4095)
            spatial_phase[m * COLS + n] = 
                (spatial_phase_real / (2.0 * 3.14159265)) * 4096.0;
        end
    end
end

// ============================================================================
// 相位合成: 空间相位 + 时间相位
// ============================================================================
always @(posedge clk or negedge rst_n) begin
    integer i;
    reg [PHASE_BITS:0] total_phase;  // 13-bit to handle overflow
    reg [7:0] varcap_value;
    reg pin_state;
    
    if (!rst_n) begin
        pin_control <= 64'd0;
        varcap_control <= 512'd0;
    end else if (enable) begin
        // 对每个单元合成总相位
        for (i = 0; i < NUM_UNITS; i = i + 1) begin
            // 总相位 = 空间相位 + 时间相位
            total_phase = spatial_phase[i] + phase_accumulator[PHASE_BITS+12:12];
            
            // 提取 PIN 控制位 (MSB: 0°/180°)
            pin_state = total_phase[PHASE_BITS];
            
            // 提取 VarCap 控制值 (低 8 位, 0-255 对应 0-10V)
            varcap_value = total_phase[PHASE_BITS-1:PHASE_BITS-8];
            
            // 输出控制信号
            pin_control[i] = pin_state;
            varcap_control[i*8+7:i*8] = varcap_value;
        end
    end
end

// ============================================================================
// 调试输出 (可选)
// ============================================================================
`ifdef DEBUG
    wire [31:0] debug_freq = instantaneous_freq;
    wire [11:0] debug_spatial_phase_0 = spatial_phase[0];
`endif

endmodule
