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
import random
import string


app = Flask(__name__)
ask = Ask(app, '/')

mphands = mp.solutions.hands
hands = mphands.Hands()
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
last_captured = None
display_live_feed= False
x_max = 0
y_max = 0
x_min = 0
y_min = 0
landmarks_scan = None
captured_frame = None
_, frame = cap.read()





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

    def repeat_letter(self,letter):
        if not letter or not self.validate_user_resp(letter):
            if self.current_group == 2:
                speech_text = "Juego perdido con score " + str(self.score)
                print(speech_text)
                exit(0)
            else:
                l = self.switch_to_group_2()
                speech_text = "Letra incorecta, ahora " + l
        else:
            #self.cur_t += 1
            #if self.cur_t <= self.maxt:
            self.score += ord(letter)
            speech_text = "Correcto ahora: " + self.generate_letter()
            #else:
            #    speech_text = (
            #        "Hemos acabado. Tu puntuación de hoy: " +
            #        str(self.score) + "puntos ¡Enhorabuena!"
            #    )
        return speech_text

    def help_fun(self):
        speech_text = (
            "Voy a decir algunos letras. Escucha con atención y cuando yo haya terminado, "
            "repítalo inmediatamente. "
            "Si necesitas saber cómo se juega, ¡pregúntame!"
        )
        return speech_text


@ask.launch
def start_skill():
    return question(FRASES_HECHAS['MENSAJE_BIENVENIDA'][0])


moderator = Engine()
moderator.start_new()


@ask.intent("StartGameIntent")
def startGameIntent():

    moderator.start_new()
    print("Entered the start game")
    global display_live_feed
    global last_captured
    global landmarks_scan
    global x_max
    global x_min
    global y_max
    global y_min
    global frame
    global captured_frame

    cap = cv2.VideoCapture(0)
    _,frame = cap.read()
    h, w, c = frame.shape

    display_live_feed = True
    while display_live_feed:
        ret, frame = cap.read()
        cv2.imshow("Live feed", frame)
        k = cv2.waitKey(1)

        if k % 256 == 32:
            last_captured = frame
            showframe = captured_frame
            cv2.imshow("Frame", showframe)
            framergbanalysis = cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB)
            resultanalysis = hands.process(framergbanalysis)
            landmarks_scan = resultanalysis.multi_hand_landmarks

        elif k % 256 == 27:
            print("Escaping the game")
            break
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

    return statement(speech_text)

@ask.intent("capIntent")
def cap():
    global display_live_feed
    global last_captured
    global landmarks_scan
    global x_max
    global x_min
    global y_max
    global y_min
    global captured_frame
    speech = ''
    letterpred = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
    speech_text = f"¡Genial! Empezamos: {moderator.current_letter} , dime cap cuando me quieres analisar"
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
    if not captured_frame:
        print("There is no captured frame")
        return
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
    for key,value in letter_pred_dict.items():
        if value==pred1:
            speech = moderator.repeat_letter(key)

    return statement(speech)

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


@ask.intent('StopIntent')
def stop():
    cap.release()
    cv2.destroyAllWindows()
    return statement("El juego esta terminado con score " + moderator.score)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
    app.run(port = 7045, debug=True)
