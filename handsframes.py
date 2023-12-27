import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import cv2
import mediapipe as mp
from keras.models import load_model
import numpy as np
import time
import pandas as pd
from mod import Engine

model = load_model('americansign.h5')
moderator = Engine()
moderator.start_new()
mphands = mp.solutions.hands
hands = mphands.Hands()
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

_, frame = cap.read()

h, w, c = frame.shape

captured_frame = ''
letterpred = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']


print("********************** Current letter ************************")
print(moderator.current_letter)
print("***************************************************************")

while True:
    _, frame = cap.read()

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        captured_frame = frame
        showframe = captured_frame
        cv2.imshow("Frame", showframe)
        framergbanalysis = cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB)
        resultanalysis = hands.process(framergbanalysis)
        landmarks_scan = resultanalysis.multi_hand_landmarks
        if landmarks_scan:
            for handLMsanalysis in landmarks_scan:
                x_max = 0
                y_max = 0
                x_min = w
                y_min = h
                for lmanalysis in handLMsanalysis.landmark:
                    x, y = int(lmanalysis.x * w), int(lmanalysis.y * h)
                    if x > x_max:
                        x_max = x
                    if x < x_min:
                        x_min = x
                    if y > y_max:
                        y_max = y
                    if y < y_min:
                        y_min = y
                y_min -= 20
                y_max += 20
                x_min -= 20
                x_max += 20 

        captured_frame = cv2.cvtColor(captured_frame, cv2.COLOR_BGR2GRAY)
        captured_frame = captured_frame[y_min:y_max, x_min:x_max]
        captured_frame = cv2.resize(captured_frame,(28,28))


        nlist = []
        rows,cols = captured_frame.shape
        for i in range(rows):
            for j in range(cols):
                k = captured_frame[i,j]
                nlist.append(k)
        
        datan = pd.DataFrame(nlist).T
        colname = []
        for val in range(784):
            colname.append(val)
        datan.columns = colname

        pixeldata = datan.values
        pixeldata = pixeldata / 255
        pixeldata = pixeldata.reshape(-1,28,28,1)
        prediction = model.predict(pixeldata)
        predarray = np.array(prediction[0])
        letter_pred_dict = {letterpred[i]: predarray[i] for i in range(len(letterpred))}
        predarrayordered = sorted(predarray, reverse=True)
        pred1 = predarrayordered[0]
        pred2 = predarrayordered[1]
        pred3 = predarrayordered[2]
        for key,value in letter_pred_dict.items():
            if value==pred1:
                print("Predicted Character 1: ", key)
                print('Confidence 1: ', 100*value)
                print()
                print()
                print("COMPARISON WITH GAME LETTER")
                print()
                print(moderator.repeat_letter(key))
                print()
                print()
            elif value==pred2:
                print("Predicted Character 2: ", key)
                print('Confidence 2: ', 100*value)
            elif value==pred3:
                print("Predicted Character 3: ", key)
                print('Confidence 3: ', 100*value)
        #time.sleep(5)

    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(framergb)
    hand_landmarks = result.multi_hand_landmarks
    if hand_landmarks:
        for handLMs in hand_landmarks:
            x_max = 0
            y_max = 0
            x_min = w
            y_min = h
            for lm in handLMs.landmark:
                x, y = int(lm.x * w), int(lm.y * h)
                if x > x_max:
                    x_max = x
                if x < x_min:
                    x_min = x
                if y > y_max:
                    y_max = y
                if y < y_min:
                    y_min = y
            y_min -= 20
            y_max += 20
            x_min -= 20
            x_max += 20
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            mp_drawing.draw_landmarks(frame, handLMs, mphands.HAND_CONNECTIONS)
    cv2.imshow("Frame", frame)

cap.release()
cv2.destroyAllWindows()
