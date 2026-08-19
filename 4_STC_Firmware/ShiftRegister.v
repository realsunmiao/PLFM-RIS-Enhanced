////////////////////////////////////////////////////////////////////////////////
// Module: ShiftRegister.v
// Description: 串并转换移位寄存器 - 用于扩展 VarCap 控制输出
// 
// 功能: 将串行数据转换为 512 位并行输出 (64 单元 × 8-bit)
//
// 作者: Wukong AI Assistant
// 日期: 2026-08-19
////////////////////////////////////////////////////////////////////////////////

module ShiftRegister (
    input wire          clk,            // 系统时钟
    input wire          rst_n,          // 复位
    input wire          serial_data,    // 串行数据输入
    input wire          serial_clock,   // 串行时钟
    input wire          latch,          // 锁存信号
    output reg [511:0]  parallel_out    // 并行输出 (512-bit)
);

// ============================================================================
// 内部信号
// ============================================================================
reg [511:0] shift_reg;                  // 移位寄存器
reg [8:0] bit_counter;                  // 位计数器 (0-511)

// ============================================================================
// 移位逻辑
// ============================================================================
always @(posedge serial_clock or negedge rst_n) begin
    if (!rst_n) begin
        shift_reg <= 512'd0;
        bit_counter <= 9'd0;
    end else begin
        // 左移一位,新数据从 LSB 进入
        shift_reg <= {shift_reg[510:0], serial_data};
        bit_counter <= bit_counter + 9'd1;
        
        // 计数到 512 位后重置
        if (bit_counter >= 9'd511) begin
            bit_counter <= 9'd0;
        end
    end
end

// ============================================================================
// 锁存逻辑
// ============================================================================
always @(posedge latch or negedge rst_n) begin
    if (!rst_n) begin
        parallel_out <= 512'd0;
    end else begin
        // 锁存当前移位寄存器内容
        parallel_out <= shift_reg;
    end
end

endmodule
