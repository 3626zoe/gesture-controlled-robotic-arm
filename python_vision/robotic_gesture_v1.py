import cv2
import mediapipe as mp
import time
import math
import serial

# ==========================================
COM_PORT = 'COM3'       # Arduino port
BAUD_RATES = 115200     # Arduino baud rate
MOVE_SPEED = 2          # Movement speed (1-5); higher number is faster
# ==========================================

# Establish Serial connection
def reconnect_serial(arduino_port, baud_rate):
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2) # Wait for Arduino to restart
        print(f"✅ Successfully connected to {arduino_port}")
        return ser
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def main():
    # Initialize MediaPipe hand detection
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

    # Open the camera
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('Gesture Control', cv2.WINDOW_NORMAL)
    # Default window size: 1024x768
    cv2.resizeWindow('Gesture Control', 1024, 768)
    # Connect to Arduino
    ser = reconnect_serial(COM_PORT, BAUD_RATES)

    # === Current robot arm angles ===
    curr_base = 90      # Base (Left/Right)
    curr_shoulder = 90  # Shoulder (Up/Down)
    curr_elbow = 90     # Elbow (Fixed for stability)
    curr_claw = 30      # Claw

    print("---------------------------------------")
    print("System started：")
    print("👉 Hand in center = Stop")
    print("👉 Hand outside green box = Arm starts moving")
    print("---------------------------------------")

    last_send_time = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Failed to read camera")
            break

        # 1. Flip the camera frame 
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 2. Detect Hand
        results = hands.process(rgb)

        # 3. Draw the Center Zone (green box)
        # Set 30% to 70% of the screen as the stop zone
        cv2.rectangle(frame, (int(w*0.3), int(h*0.3)), (int(w*0.7), int(h*0.7)), (0, 255, 0), 2)
        cv2.putText(frame, "STOP ZONE", (int(w*0.3), int(h*0.3)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        
        status_text = "STOP" # Default Status

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get wrist coordinates (center point)
            wrist = hand_landmarks.landmark[0]
            cx, cy = wrist.x, wrist.y # Range is 0.0 to 1.0

            # ==========================================
            # Control Logic 
            # ==========================================

            # --- 1. Left/right control (Base motor) ---
            if cx < 0.3: # Hand is on the left
                curr_base += MOVE_SPEED
                status_text = "LEFT  <<"
            elif cx > 0.7: # Hand is on the right
                curr_base -= MOVE_SPEED
                status_text = "RIGHT >>"

            # --- 2. Up/down control (Shoulder motor) ---
            if cy < 0.3: # Hand is at the top
                curr_shoulder += MOVE_SPEED
                status_text = "UP    ^^"
            elif cy > 0.7: # Hand is at the bottom
                curr_shoulder -= MOVE_SPEED
                status_text = "DOWN  vv"

            # --- 3. Claw control ---
            # Calculate distance between thumb (4) and index finger (8)
            thumb = hand_landmarks.landmark[4]
            index = hand_landmarks.landmark[8]
            # Use Euclidean distance to find the distance
            dist = math.sqrt((thumb.x - index.x)**2 + (thumb.y - index.y)**2)
            
            if dist < 0.05: # Very close -> Close claw
                curr_claw = 90  # Closed angle (based on your 10~100 setting)
                cv2.putText(frame, "GRIP!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            else:           # Far apart -> Open claw
                curr_claw = 30  # Open angle
            

            # ==========================================
            # ⚠️ Safe range limits 
            # ==========================================
            curr_base = max(0, min(180, curr_base))
            curr_shoulder = max(30, min(150, curr_shoulder))
            curr_elbow = max(30, min(150, curr_elbow))
            curr_claw = max(10, min(100, curr_claw))

        # 4. Show current information
        cv2.putText(frame, f"Action: {status_text}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"Angle: {int(curr_base)}, {int(curr_shoulder)}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        # 5. Send data to Arduino 
        if time.time() - last_send_time > 0.05: 
        
            if ser and ser.is_open:
                # Format string: "base,shoulder,elbow,claw\n"
                msg = f"{int(curr_base)},{int(curr_shoulder)},{int(curr_elbow)},{int(curr_claw)}\n"
                try:
                    ser.write(msg.encode())
                    # print(f"Sent: {msg.strip()}") # Uncomment this to check values during testing
                except Exception as e:
                    print(f"Send error: {e}")
            last_send_time = time.time()

        # Show the video frame
        cv2.imshow('Gesture Control', frame)
        
        # Press ESC to exit
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Exit
    cap.release()
    cv2.destroyAllWindows()
    if ser:
        ser.close()

if __name__ == "__main__":
    main()