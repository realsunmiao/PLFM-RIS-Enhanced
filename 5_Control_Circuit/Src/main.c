/**
 * @file main.c
 * @brief STM32F746 主程序 - RIS 雷达系统控制核心
 * 
 * 功能:
 *   1. 电源时序控制
 *   2. FPGA 配置与通信
 *   3. 温度/电压监控
 *   4. USB 命令处理
 * 
 * @author Wukong AI Assistant
 * @date 2026-08-19
 */

#include "main.h"
#include "stm32f7xx_hal.h"
#include "power_seq.h"
#include "fpga_config.h"
#include "monitor.h"

// 全局变量
UART_HandleTypeDef huart1;  // USB CDC
SPI_HandleTypeDef hspi1;    // FPGA 通信
ADC_HandleTypeDef hadc1;    // 温度/电压采集

/**
 * @brief 主函数
 */
int main(void) {
    // HAL 库初始化
    HAL_Init();
    
    // 系统时钟配置 (216 MHz)
    SystemClock_Config();
    
    // 外设初始化
    MX_GPIO_Init();
    MX_SPI1_Init();
    MX_USART1_UART_Init();
    MX_ADC1_Init();
    
    // 启动指示 LED
    HAL_GPIO_WritePin(LED_STATUS_GPIO_Port, LED_STATUS_Pin, GPIO_PIN_SET);
    
    // 电源时序上电
    Power_Sequence_Up();
    
    // 等待电源稳定
    HAL_Delay(500);
    
    // 初始化 FPGA
    if (FPGA_Init() != HAL_OK) {
        // FPGA 初始化失败,进入错误状态
        Error_Handler();
    }
    
    // 发送就绪信号
    UART_SendString("RIS Radar System Ready\r\n");
    
    // 主循环
    while (1) {
        // 1. 监控温度和电压
        Monitor_Temperature();
        Monitor_Voltage();
        
        // 2. 处理 USB 命令
        Process_USB_Command();
        
        // 3. 看门狗喂狗
        IWDG_Refresh();
        
        // 4. 延时 10ms
        HAL_Delay(10);
    }
}

/**
 * @brief 系统时钟配置
 */
void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    
    // 使能 HSE
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM = 25;
    RCC_OscInitStruct.PLL.PLLN = 432;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
    RCC_OscInitStruct.PLL.PLLQ = 9;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);
    
    // 配置系统时钟
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_7);
}

/**
 * @brief GPIO 初始化
 */
void MX_GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能 GPIO 时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    // LED 引脚
    GPIO_InitStruct.Pin = LED_STATUS_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(LED_STATUS_GPIO_Port, &GPIO_InitStruct);
    
    // 电源使能引脚
    GPIO_InitStruct.Pin = PWR_12V_EN_Pin | PWR_5V_EN_Pin | PWR_3V3_EN_Pin;
    HAL_GPIO_Init(PWR_EN_GPIO_Port, &GPIO_InitStruct);
}

/**
 * @brief SPI1 初始化 (与 FPGA 通信)
 */
void MX_SPI1_Init(void) {
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;  // 6.75 MHz
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    HAL_SPI_Init(&hspi1);
}

/**
 * @brief USART1 初始化 (USB CDC)
 */
void MX_USART1_UART_Init(void) {
    huart1.Instance = USART1;
    huart1.Init.BaudRate = 115200;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    HAL_UART_Init(&huart1);
}

/**
 * @brief ADC1 初始化 (温度/电压采集)
 */
void MX_ADC1_Init(void) {
    ADC_ChannelConfTypeDef sConfig = {0};
    
    hadc1.Instance = ADC1;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = ENABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;
    hadc1.Init.NbrOfConversion = 2;  // 温度 + 电压
    HAL_ADC_Init(&hadc1);
    
    // 配置通道 0 (温度传感器)
    sConfig.Channel = ADC_CHANNEL_TEMPSENSOR;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_480CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
    
    // 配置通道 1 (电压检测)
    sConfig.Channel = ADC_CHANNEL_1;
    sConfig.Rank = 2;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
}

/**
 * @brief 错误处理
 */
void Error_Handler(void) {
    // 闪烁 LED 表示错误
    while (1) {
        HAL_GPIO_TogglePin(LED_STATUS_GPIO_Port, LED_STATUS_Pin);
        HAL_Delay(100);
    }
}

#ifdef USE_FULL_ASSERT
void assert_failed(uint8_t* file, uint32_t line) {
    while (1) {}
}
#endif
