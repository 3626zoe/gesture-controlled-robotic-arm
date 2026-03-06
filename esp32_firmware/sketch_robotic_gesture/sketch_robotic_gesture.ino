#include <ESP32Servo.h>

// 定義 4 個伺服馬達
Servo s_base;     // 底座 (對應擴充板 Pin 4)
Servo s_shoulder; // 大臂 (對應擴充板 Pin 5)
Servo s_elbow;    // 小臂 (對應擴充板 Pin 6)
Servo s_claw;     // 夾爪 (對應擴充板 Pin 7)

void setup() {
    Serial.begin(115200); 

    // --- D1 R32 腳位映射 ---
    s_base.attach(17);          // 擴充板 Pin 4 -> ESP32 GPIO 17
    s_shoulder.attach(16);      // 擴充板 Pin 5 -> ESP32 GPIO 16
    s_elbow.attach(27);         // 擴充板 Pin 6 -> ESP32 GPIO 27
    s_claw.attach(14);          // 擴充板 Pin 7 -> ESP32 GPIO 14

    // 初始角度
    s_base.write(90);
    s_shoulder.write(90);
    s_elbow.write(150);
    s_claw.write(30); // 夾爪張開
}

void loop() {
    if (Serial.available()) {
        String data = Serial.readStringUntil('\n');

        // 變數簡化為 4 個
        int m1, m2, m3, m4; 
        
        if (sscanf(data.c_str(), "%d,%d,%d,%d", &m1, &m2, &m3, &m4) == 4) {
            
            // --- 安全範圍限制 ---
            m1 = constrain(m1, 0, 180);   // 底座
            m2 = constrain(m2, 30, 150);  // 大臂
            m3 = constrain(m3, 30, 150);  // 小臂
            m4 = constrain(m4, 10, 100);  // 夾爪

            // --- 執行動作 ---
            s_base.write(m1);
            s_shoulder.write(m2);
            s_elbow.write(m3);
            s_claw.write(m4);
            delay(50);
        }
    }
}