# Hand Recognition Controlled Robotic Arm

This project demonstrates a robust system architecture for Human-Robot Interaction (HRI). It leverages Python-based computer vision (MediaPipe) for real-time hand tracking and seamlessly translates spatial coordinates into hardware actuation via an ESP32 microcontroller. The repository is structured to validate architecture design and ensure high reproducibility across different devices.

本專案展示了一套穩健的人機互動 (HRI) 系統架構，透過 Python (MediaPipe) 進行即時手部節點追蹤，並將空間座標無縫轉換為硬體控制邏輯，透過序列埠傳輸至 ESP32 微控制器以驅動機械手臂，本儲存庫的架構設計旨在驗證系統的整合性，並確保在不同裝置上的高重現性。

---

## 🛠️ System Requirements 

### Software 
* **Python:** `3.11.9` (Strictly required)
* **Arduino IDE:** Version 2.3.6

### Hardware & Firmware 
* **Microcontroller:** ESP32 Development Board
* **Actuator:** Servo-based Robotic Arm
* **Camera:** Standard USB Webcam
* **Communication:** USB Serial connection (Baud Rate: `115200`)

#### Arduino Dependencies 
Please install the following exact versions in your Arduino IDE:
1. **Board Manager (開發板管理員):** `esp32 by Espressif Systems` - **Version 3.0.1**
2. **Library Manager (函式庫管理員):** `ESP32Servo by Kevin Harrington` - **Version 3.0.9**

---

## 📦 Installation & Setup 

### 1. ESP32 Firmware Setup 
1. Open `esp32_firmware/sketch_robotic_gesture/sketch_robotic_gesture.ino` in Arduino IDE.
2. Install the required board and library versions mentioned above.
3. Select the correct ESP32 board (`ESP32 Dev Module`) and COM port.
4. Verify the Baud Rate is set to `115200` in the code.
5. Upload the code to your ESP32.

### 2. Python Vision Setup 
It is highly recommended to use a virtual environment to prevent package conflicts.

```bash
# Clone the repository (請將網址替換為您的 GitHub 專案網址)
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME/python_vision

# Create and activate a virtual environment (Python 3.11.9)
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install exact dependencies
pip install -r requirements.txt