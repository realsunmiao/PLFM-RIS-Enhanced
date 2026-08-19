/**
 * @file power_seq.c
 * @brief 电源时序控制模块
 * 
 * 功能: 按正确顺序上电/下电,避免浪涌电流损坏器件
 */

#include "power_seq.h"
#include "stm32f7xx_hal.h"

/**
 * @brief 电源时序上电
 * 
 * 上电顺序:
 *   1. 12V (功放供电)
 *   2. 5V (数字电路)
 *   3. 3.3V (I/O)
 *   4. 1.8V (FPGA 核心)
 *   5. 1.0V (FPGA AUX)
 */
void Power_Sequence_Up(void) {
    // Step 1: 使能 12V
    HAL_GPIO_WritePin(PWR_12V_EN_GPIO_Port, PWR_12V_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(100);  // 等待 100ms
    
    // Step 2: 使能 5V
    HAL_GPIO_WritePin(PWR_5V_EN_GPIO_Port, PWR_5V_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(50);
    
    // Step 3: 使能 3.3V
    HAL_GPIO_WritePin(PWR_3V3_EN_GPIO_Port, PWR_3V3_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(50);
    
    // Step 4: 使能 1.8V
    HAL_GPIO_WritePin(PWR_1V8_EN_GPIO_Port, PWR_1V8_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(50);
    
    // Step 5: 使能 1.0V
    HAL_GPIO_WritePin(PWR_1V0_EN_GPIO_Port, PWR_1V0_EN_Pin, GPIO_PIN_SET);
    HAL_Delay(100);
    
    // 所有电源就绪
    HAL_GPIO_WritePin(LED_PWR_OK_GPIO_Port, LED_PWR_OK_Pin, GPIO_PIN_SET);
}

/**
 * @brief 电源时序下电 (反向顺序)
 */
void Power_Sequence_Down(void) {
    // Step 1: 关闭 1.0V
    HAL_GPIO_WritePin(PWR_1V0_EN_GPIO_Port, PWR_1V0_EN_Pin, GPIO_PIN_RESET);
    HAL_Delay(20);
    
    // Step 2: 关闭 1.8V
    HAL_GPIO_WritePin(PWR_1V8_EN_GPIO_Port, PWR_1V8_EN_Pin, GPIO_PIN_RESET);
    HAL_Delay(20);
    
    // Step 3: 关闭 3.3V
    HAL_GPIO_WritePin(PWR_3V3_EN_GPIO_Port, PWR_3V3_EN_Pin, GPIO_PIN_RESET);
    HAL_Delay(20);
    
    // Step 4: 关闭 5V
    HAL_GPIO_WritePin(PWR_5V_EN_GPIO_Port, PWR_5V_EN_Pin, GPIO_PIN_RESET);
    HAL_Delay(20);
    
    // Step 5: 关闭 12V
    HAL_GPIO_WritePin(PWR_12V_EN_GPIO_Port, PWR_12V_EN_Pin, GPIO_PIN_RESET);
}

/**
 * @brief 检查电源状态
 * @return 0: 正常, -1: 异常
 */
int Power_Check_Status(void) {
    // TODO: 读取各电压轨的反馈信号
    // 这里简化为检查使能引脚状态
    
    if (HAL_GPIO_ReadPin(PWR_12V_EN_GPIO_Port, PWR_12V_EN_Pin) == GPIO_PIN_SET &&
        HAL_GPIO_ReadPin(PWR_5V_EN_GPIO_Port, PWR_5V_EN_Pin) == GPIO_PIN_SET &&
        HAL_GPIO_ReadPin(PWR_3V3_EN_GPIO_Port, PWR_3V3_EN_Pin) == GPIO_PIN_SET) {
        return 0;  // 正常
    }
    
    return -1;  // 异常
}
