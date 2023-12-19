from flask import Flask
from flask_ask import Ask, statement, question
from flask import Flask, render_template
import os
import tensorflow as tf
import cv2
import mediapipe as mp
from keras.models import load_model
import numpy as np
import time
import pandas as pd


app = Flask(__name__)
ask = Ask(app, '/')

mphands = mp.solutions.hands
hands = mphands.Hands()
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)



FRASES_HECHAS = {
    'LETRA_INCORRECTA': 'Caracter invalido',
    'NOMBRE_SKILL': 'CODA',
    'MENSAJE_BIENVENIDA' : ['hola, ¿quieres jugar el lenguaje de señas? Si ? invoca mi por "senas" ',
    						'hola ¿Quieres aprender la lengua de signos? "invoca mi por "senas"',
    						],
    'PUEDO_AYUDARTE' : [' ¿quieres jugar un juego?',
                        ' Nostros aprendemos jugando',
                        ' ¿Una película, una serie, un documental o las noticias?']
}

class Engine:
    def __init__(self):
        self.current_letter = None
        self.current_group = 1 
        self.score = 0
        self.maxt = 5
        self.cur_t = 0
    def start_new(self):
        self.generate_letter()
        self.score = 0
        self.current_group = 1
    def generate_letter(self):
        self.current_letter = random.choice(string.ascii_uppercase)
        return self.current_letter
    def validate_user_resp(self,user_response):
        return user_response == self.current_letter
    def switch_to_group_2(self):
        self.current_group = 2
        self.current_letter = random.choice(string.ascii_uppercase)
        return self.current_letter


@ask.launch
def start_skill():
    return question(FRASES_HECHAS['MENSAJE_BIENVENIDA'][0])

@ask.intent("StartGameIntent")
def startGameIntent():
    moderator.start_new_game()
    speech_text = f"¡Genial! Empezamos: {moderator.current_letter}"
    _, frame = cap.read()    
    h, w, c = frame.shape
    captured_frame = ''
    letterpred = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
        while True:
        _, frame = cap.read()

        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
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
            captured_frame = cv2.resize(captured_frame, (28, 28))

            nlist = []
            rows, cols = captured_frame.shape
            for i in range(rows):
                for j in range(cols):
                    k = captured_frame[i, j]
                    nlist.append(k)

            datan = pd.DataFrame(nlist).T
            colname = []
            for val in range(784):
                colname.append(val)
            datan.columns = colname

            pixeldata = datan.values
            pixeldata = pixeldata / 255
            pixeldata = pixeldata.reshape(-1, 28, 28, 1)
            prediction = model.predict(pixeldata)
            predarray = np.array(prediction[0])
            letter_pred_dict = {letterpred[i]: predarray[i] for i in range(len(letterpred))}
            predarrayordered = sorted(predarray, reverse=True)
            pred1 = predarrayordered[0]
            pred_let = None
            for k, v in letter_pred_dict.items():
                if v == pred1:
                    pred_let = k

            if pred1 > YOUR_THRESHOLD:  # Replace YOUR_THRESHOLD with the desired confidence threshold
                send_alexa_directive("Your gesture is recognized!")
                break

    return statement(speech_text)

def repeat_letter(letter):
    if not letter or not moderator.validate_user_resp(letter):
        speech_text = FRASES_HECHAS['LETRA_INCORRECTA']
    else:
        moderator.cur_t += 1
        if moderator.cur_t <= moderator.maxt:
            moderator.score += ord(letter)
            speech_text = "Correcto ahora: " + moderator.generate_letter()
        else:
            speech_text = (
                "Hemos acabado. Tu puntuación de hoy: " +
                str(moderator.score) + "puntos ¡Enhorabuena!"
            )
    return statement(speech_text)


@ask.intent("AMAZON.StopIntent")
@ask.intent("AMAZON.CancelIntent")
def stop_intent():
    cap.release()
    cv2.destroyAllWindows()
    return statement("Goodbye!")

@ask.intent('AyudaIntent')
def ayuda():
    speech_text = (
        "Voy a decir algunos letras. Escucha con atención y cuando yo haya terminado, "
        "repítalo inmediatamente. "
        "Si necesitas saber cómo se juega, ¡pregúntame!"
    )
    return question(speech_text).reprompt(speech_text)

@ask.intent('HelloIntent')
def hello(firstname):
    speech_text = "Hello %s" % firstname
    return statement(speech_text).simple_card('Hello', speech_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
    app.run(debug=True)
