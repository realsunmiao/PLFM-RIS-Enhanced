////////////////////////////////////////////////////////////////////////////////
// Module: Waveform_Gen.v
// Description: LFM 波形生成模块 - 产生线性调频信号的相位累加值
// 
// 功能:
//   1. 根据 f0, k_slope 生成时变相位
//   2. 支持周期重置
//   3. 输出 32-bit 相位累加器值
//
// 作者: Wukong AI Assistant
// 日期: 2026-08-19
////////////////////////////////////////////////////////////////////////////////

module Waveform_Gen (
    input wire          clk,            // 系统时钟 (100 MHz)
    input wire          rst_n,          // 复位
    input wire          enable,         // 使能
    input wire [31:0]   f0,             // 起始频率 (Hz, 定点表示)
    input wire [31:0]   k_slope,        // 调频斜率 (Hz/s, 定点表示)
    input wire [31:0]   T_period,       // 调频周期 (采样点数)
    output reg [31:0]   phase_accum     // 相位累加器输出
);

// ============================================================================
// 内部信号
// ============================================================================
reg [31:0] time_counter;                // 时间计数器
reg [31:0] freq_instant;                // 瞬时频率
reg [47:0] phase_increment;             // 相位增量 (48-bit 防止溢出)

// ============================================================================
// 时间计数器和瞬时频率计算
// ============================================================================
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        time_counter <= 32'd0;
        freq_instant <= 32'd0;
    end else if (enable) begin
        // 时间递增
        time_counter <= time_counter + 32'd1;
        
        // 计算瞬时频率: f(t) = f0 + k * t
        // 简化: 使用移位代替乘法 (假设 k_slope 已缩放)
        freq_instant <= f0 + ((k_slope * time_counter[15:0]) >> 16);
        
        // 周期重置
        if (time_counter >= T_period) begin
            time_counter <= 32'd0;
        end
    end else begin
        time_counter <= 32'd0;
        freq_instant <= 32'd0;
    end
end

// ============================================================================
// 相位累加
// ============================================================================
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        phase_accum <= 32'd0;
    end else if (enable) begin
        // 相位累加: φ(n+1) = φ(n) + 2π*f/fs
        // 简化实现: 直接累加频率值
        phase_accum <= phase_accum + freq_instant;
        
        // 周期重置时清零相位
        if (time_counter >= T_period) begin
            phase_accum <= 32'd0;
        end
    end else begin
        phase_accum <= 32'd0;
    end
end

// ============================================================================
// 调试输出
// ============================================================================
`ifdef DEBUG
    wire [31:0] debug_time = time_counter;
    wire [31:0] debug_freq = freq_instant;
`endif

endmodule
