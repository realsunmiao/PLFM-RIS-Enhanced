////////////////////////////////////////////////////////////////////////////////
// Module: SPI_Interface.v
// Description: SPI 通信接口模块 - 与 STM32 或上位机通信
// 
// 功能:
//   1. 接收 SPI 命令和配置数据
//   2. 解析命令并更新配置寄存器
//   3. 发送状态响应
//
// 作者: Wukong AI Assistant
// 日期: 2026-08-19
////////////////////////////////////////////////////////////////////////////////

module SPI_Interface (
    input wire          clk,            // 系统时钟 (100 MHz)
    input wire          rst_n,          // 复位信号
    input wire          spi_cs,         // SPI 片选
    input wire          spi_clk,        // SPI 时钟
    input wire          spi_mosi,       // SPI 主出从入
    output reg          spi_miso,       // SPI 主入从出
    
    // 配置输出
    output reg [15:0]   azimuth,        // 方位角
    output reg [15:0]   elevation,      // 俯仰角
    output reg [31:0]   f0,             // 起始频率
    output reg [31:0]   k_slope,        // 调频斜率
    output reg [31:0]   t_period,       // 调频周期
    output reg          enable,         // 使能信号
    
    // 状态指示
    output reg          led_active      // 数据传输指示灯
);

// ============================================================================
// 参数定义
// ============================================================================
localparam CMD_CONFIG_AZIMUTH = 8'h01;
localparam CMD_CONFIG_ELEVATION = 8'h02;
localparam CMD_CONFIG_F0 = 8'h03;
localparam CMD_CONFIG_K_SLOPE = 8'h04;
localparam CMD_CONFIG_T_PERIOD = 8'h05;
localparam CMD_ENABLE = 8'h10;
localparam CMD_DISABLE = 8'h11;
localparam CMD_GET_DATA = 8'h20;

// ============================================================================
// 内部信号
// ============================================================================
reg [7:0] rx_buffer;                    // 接收缓冲区
reg [2:0] bit_counter;                  // 位计数器
reg [7:0] cmd_buffer;                   // 命令缓冲区
reg [7:0] length_buffer;                // 长度缓冲区
reg [7:0] data_buffer [0:7];            // 数据缓冲区 (最大 8 字节)
reg [2:0] byte_counter;                 // 字节计数器
reg [2:0] state;                        // 状态机

// 状态定义
localparam STATE_IDLE = 3'd0;
localparam STATE_CMD = 3'd1;
localparam STATE_LENGTH = 3'd2;
localparam STATE_DATA = 3'd3;
localparam STATE_CHECKSUM = 3'd4;
localparam STATE_EXECUTE = 3'd5;

// ============================================================================
// SPI 接收逻辑 (上升沿采样)
// ============================================================================
always @(posedge spi_clk or negedge rst_n) begin
    if (!rst_n) begin
        rx_buffer <= 8'd0;
        bit_counter <= 3'd0;
    end else if (!spi_cs) begin
        // 移位寄存器
        rx_buffer <= {rx_buffer[6:0], spi_mosi};
        bit_counter <= bit_counter + 3'd1;
        
        // 每 8 位保存一次
        if (bit_counter == 3'd7) begin
            case (state)
                STATE_IDLE: begin
                    cmd_buffer <= rx_buffer;
                    state <= STATE_CMD;
                end
                STATE_CMD: begin
                    length_buffer <= rx_buffer;
                    state <= STATE_LENGTH;
                    byte_counter <= 3'd0;
                end
                STATE_LENGTH: begin
                    data_buffer[byte_counter] <= rx_buffer;
                    byte_counter <= byte_counter + 3'd1;
                    if (byte_counter >= length_buffer - 1) begin
                        state <= STATE_CHECKSUM;
                    end
                end
                STATE_CHECKSUM: begin
                    // TODO: 验证校验和
                    state <= STATE_EXECUTE;
                end
                default: state <= STATE_IDLE;
            endcase
            bit_counter <= 3'd0;
        end
    end else begin
        // CS 拉高时重置
        state <= STATE_IDLE;
        bit_counter <= 3'd0;
    end
end

// ============================================================================
// 命令执行逻辑
// ============================================================================
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        azimuth <= 16'd0;
        elevation <= 16'd0;
        f0 <= 32'd0;
        k_slope <= 32'd0;
        t_period <= 32'd0;
        enable <= 1'b0;
        led_active <= 1'b0;
        spi_miso <= 1'b1;  // 空闲时为高
    end else if (state == STATE_EXECUTE) begin
        led_active <= 1'b1;
        
        case (cmd_buffer)
            CMD_CONFIG_AZIMUTH: begin
                azimuth <= {data_buffer[1], data_buffer[0]};
            end
            CMD_CONFIG_ELEVATION: begin
                elevation <= {data_buffer[1], data_buffer[0]};
            end
            CMD_CONFIG_F0: begin
                f0 <= {data_buffer[3], data_buffer[2], data_buffer[1], data_buffer[0]};
            end
            CMD_CONFIG_K_SLOPE: begin
                k_slope <= {data_buffer[3], data_buffer[2], data_buffer[1], data_buffer[0]};
            end
            CMD_CONFIG_T_PERIOD: begin
                t_period <= {data_buffer[3], data_buffer[2], data_buffer[1], data_buffer[0]};
            end
            CMD_ENABLE: begin
                enable <= 1'b1;
            end
            CMD_DISABLE: begin
                enable <= 1'b0;
            end
            CMD_GET_DATA: begin
                // TODO: 返回雷达数据
                spi_miso <= 1'b0;  // 开始传输
            end
            default: ;
        endcase
        
        // 执行完成后回到空闲
        state <= STATE_IDLE;
        led_active <= 1'b0;
    end
end

endmodule
