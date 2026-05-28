#include <ESP32Servo.h>

// Define 4 servo motors
Servo s_base;     // Base (expansion board Pin 4)
Servo s_shoulder; // Shoulder (expansion board Pin 5)
Servo s_elbow;    // Elbow (expansion board Pin 6)
Servo s_claw;     // Claw (expansion board Pin 7)

void setup() {
    Serial.begin(115200); 

    // --- D1 R32 pin mapping ---
    s_base.attach(17);          // Expansion board Pin 4 -> ESP32 GPIO 17
    s_shoulder.attach(16);      // Expansion board Pin 5 -> ESP32 GPIO 16
    s_elbow.attach(27);         // Expansion board Pin 6 -> ESP32 GPIO 27
    s_claw.attach(14);          // Expansion board Pin 7 -> ESP32 GPIO 14

    // Initial angles
    s_base.write(90);
    s_shoulder.write(90);
    s_elbow.write(150);
    s_claw.write(30); 
}

void loop() {
    if (Serial.available()) {
        String data = Serial.readStringUntil('\n');

        int m1, m2, m3, m4; 
        
        if (sscanf(data.c_str(), "%d,%d,%d,%d", &m1, &m2, &m3, &m4) == 4) {
            
            // --- Safe range limits ---
            m1 = constrain(m1, 0, 180);   // 底座
            m2 = constrain(m2, 30, 150);  // 大臂
            m3 = constrain(m3, 30, 150);  // 小臂
            m4 = constrain(m4, 10, 100);  // 夾爪

            // --- Execute movement ---
            s_base.write(m1);
            s_shoulder.write(m2);
            s_elbow.write(m3);
            s_claw.write(m4);
            delay(50);
        }
    }
}