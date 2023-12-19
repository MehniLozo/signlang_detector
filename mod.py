import random 
import string

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
            self.cur_t += 1
            if self.cur_t <= moderator.maxt:
                self.score += ord(letter)
                speech_text = "Correcto ahora: " + self.generate_letter()
            else:
                speech_text = (
                    "Hemos acabado. Tu puntuación de hoy: " +
                    str(self.score) + "puntos ¡Enhorabuena!"
                )
        return speech_text

    def help_fun(self):
        speech_text = (
            "Voy a decir algunos letras. Escucha con atención y cuando yo haya terminado, "
            "repítalo inmediatamente. "
            "Si necesitas saber cómo se juega, ¡pregúntame!"
        )
        return speech_text

	
