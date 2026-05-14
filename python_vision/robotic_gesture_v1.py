import cv2
import mediapipe as mp
import time
import math
import serial

# ==========================================
COM_PORT = 'COM5'       # Arduino 連接埠
BAUD_RATES = 115200     # 配合 Arduino 的鮑率
MOVE_SPEED = 2          # 移動速度 (1~5)，數字越大跑越快
# ==========================================

# 建立 Serial 連線
def reconnect_serial(arduino_port, baud_rate):
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2) # 等待 Arduino 重啟
        print(f"✅ 成功連接到 {arduino_port}")
        return ser
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        return None

def main():
    # 初始化 MediaPipe 手部偵測
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

    # 開啟攝影機
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('Gesture Control', cv2.WINDOW_NORMAL)
    # 預設開啟時的寬高 1024x768
    cv2.resizeWindow('Gesture Control', 1024, 768)

    # 連接 Arduino
    ser = reconnect_serial(COM_PORT, BAUD_RATES)

    # === 機器手臂當前角度 ===
    curr_base = 90      # 底座 (左右)
    curr_shoulder = 90  # 大臂 (上下)
    curr_elbow = 90     # 小臂 (先固定，保持穩定)
    curr_claw = 30      # 夾爪

    print("---------------------------------------")
    print("系統啟動：")
    print("👉 手放中間 = 停止")
    print("👉 手移出綠框 = 手臂開始移動")
    print("---------------------------------------")

    last_send_time = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("無法讀取鏡頭")
            break

        # 1. 鏡頭翻轉 
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 2. 偵測手勢
        results = hands.process(rgb)

        # 3. 畫出「中心區」 (綠色框框)
        # 設定畫面寬度的 30% ~ 70% 為靜止區
        cv2.rectangle(frame, (int(w*0.3), int(h*0.3)), (int(w*0.7), int(h*0.7)), (0, 255, 0), 2)
        cv2.putText(frame, "STOP ZONE", (int(w*0.3), int(h*0.3)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        
        status_text = "STOP" # 預設狀態

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 取得手腕座標 (中心點)
            wrist = hand_landmarks.landmark[0]
            cx, cy = wrist.x, wrist.y # 範圍是 0.0 ~ 1.0

            # ==========================================
            # 控制邏輯 
            # ==========================================

            # --- 1. 左右控制 (Base 馬達) ---
            if cx < 0.3: # 手在畫面左邊
                curr_base += MOVE_SPEED
                status_text = "LEFT  <<"
            elif cx > 0.7: # 手在畫面右邊
                curr_base -= MOVE_SPEED
                status_text = "RIGHT >>"

            # --- 2. 上下控制 (Shoulder 馬達) ---
            if cy < 0.3: # 手在畫面上面
                curr_shoulder += MOVE_SPEED
                status_text = "UP    ^^"
            elif cy > 0.7: # 手在畫面下面
                curr_shoulder -= MOVE_SPEED
                status_text = "DOWN  vv"

            # --- 3. 夾爪控制 (Claw) ---
            # 計算拇指(4)與食指(8)指尖距離
            thumb = hand_landmarks.landmark[4]
            index = hand_landmarks.landmark[8]
            # 畢氏定理計算距離
            dist = math.sqrt((thumb.x - index.x)**2 + (thumb.y - index.y)**2)
            
            if dist < 0.05: # 距離很近 -> 閉合
                curr_claw = 90  # 閉合角度 (根據你的設定 10~100)
                cv2.putText(frame, "GRIP!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            else:           # 距離遠 -> 張開
                curr_claw = 30  # 張開角度
            
            # (選用) 小臂控制：目前為了穩定，先固定在 90 度

            # ==========================================
            # ⚠️ 安全範圍限制 
            # ==========================================
            curr_base = max(0, min(180, curr_base))
            curr_shoulder = max(30, min(150, curr_shoulder))
            curr_elbow = max(30, min(150, curr_elbow))
            curr_claw = max(10, min(100, curr_claw))

        # 4. 顯示目前資訊
        cv2.putText(frame, f"Action: {status_text}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"Angle: {int(curr_base)}, {int(curr_shoulder)}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        # 5. 傳送數據給 Arduino (限制傳送頻率，避免塞車)
        if time.time() - last_send_time > 0.05: 
        
            if ser and ser.is_open:
                # 組合字串: "底座,大臂,小臂,夾爪\n"
                msg = f"{int(curr_base)},{int(curr_shoulder)},{int(curr_elbow)},{int(curr_claw)}\n"
                try:
                    ser.write(msg.encode())
                    # print(f"Sent: {msg.strip()}") # 測試時可以打開這行看數值
                except Exception as e:
                    print(f"傳送錯誤: {e}")
            last_send_time = time.time()

        # 顯示畫面
        cv2.imshow('Gesture Control', frame)
        
        # 按 ESC 離開
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # 結束
    cap.release()
    cv2.destroyAllWindows()
    if ser:
        ser.close()

if __name__ == "__main__":
    main()