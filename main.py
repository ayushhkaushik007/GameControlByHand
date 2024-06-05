import cv2
import mediapipe as mp
import time
from directkeys import PressKey, ReleaseKey  

accelerate_key = 0x11  
brake_key = 0x1F  
left_key = 0x1E  
right_key = 0x20 

time.sleep(2.0)
current_key_pressed = set()

mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

tipIds = [4, 8, 12, 16, 20]

video = cv2.VideoCapture(0)

with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        keyPressed = False
        key_pressed = 0
        ret, image = video.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        lmList = []
        
        if results.multi_hand_landmarks:
            for hand_landmark in results.multi_hand_landmarks:
                myHands = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHands.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)
        
        fingers = []
        if len(lmList) != 0:
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            total = fingers.count(1)
        
            print(f"Fingers: {fingers}, Total: {total}")
            
            if total == 0:
                cv2.rectangle(image, (20, 300), (440, 425), (255, 255, 255), cv2.FILLED)
                cv2.putText(image, "Retardation", (45, 375), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 5)
                PressKey(brake_key)
                key_pressed = brake_key
                keyPressed = True
            elif total == 5:
                cv2.rectangle(image, (20, 300), (440, 425), (255, 255, 255), cv2.FILLED)
                cv2.putText(image, "Acceleration", (45, 375), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 5)
                PressKey(accelerate_key)
                key_pressed = accelerate_key
                keyPressed = True
            elif fingers == [0, 1, 0, 0, 0]: 
                cv2.rectangle(image, (20, 300), (440, 425), (255, 255, 255), cv2.FILLED)
                cv2.putText(image, "Turn Left", (45, 375), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 5)
                PressKey(left_key)
                key_pressed = left_key
                keyPressed = True
            elif fingers == [0, 0, 0, 0, 1]:  
                cv2.rectangle(image, (20, 300), (440, 425), (255, 255, 255), cv2.FILLED)
                cv2.putText(image, "Turn Right", (45, 375), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 5)
                PressKey(right_key)
                key_pressed = right_key
                keyPressed = True
        
        if not keyPressed and len(current_key_pressed) != 0:
            for key in current_key_pressed:
                ReleaseKey(key)
            current_key_pressed = set()
        elif keyPressed:
            if key_pressed not in current_key_pressed:
                current_key_pressed.add(key_pressed)
            keys_to_release = current_key_pressed - {key_pressed}
            for key in keys_to_release:
                ReleaseKey(key)
            current_key_pressed = {key_pressed}
        
        cv2.imshow("You", image)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break

video.release()
cv2.destroyAllWindows()
