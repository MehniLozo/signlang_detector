# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import random 
import string
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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



class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hola vamos a jugar unos minutos, escribe 'juego' "

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class AyudaIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AyudaIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = (
            "Voy a decir algunos letras. Escucha con atención y cuando yo haya terminado, "
            "repítalo inmediatamente. "
            "Si necesitas saber cómo se juega, ¡pregúntame!"
        )

        handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response

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

class EmpezarJuegoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("StartGameIntent")(handler_input)
        
    def handle(self, handler_input):
        moderator.start_new_game()
        speech_text = f"¡Genial! Empezamos: {moderator.current_letter}"
        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response

class RepeatingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("RepeatLetterIntent")(handler_input) \
            and handler_input.request_envelope.request.dialog_state !=  DialogState.COMPLETED 
    def handle(self, handler_input):
        letter = None
        logger.info("------------We went inside repeating sequence handler--------")
        if (handler_input.request_envelope.request.intent.slots["letter"] \
            and handler_input.request_envelope.request.intent.slots["letter"].value ):
            letter = handler_input.request_envelope.request.intent.slots["letter"].value
        #if not Letter or not moderator.validate_user_resp(letter):
        #    speech_text = FRASES_HECHAS['LETTRA_INCORRECTA']
        logger.info("Inside repeating with letter -> ")
        logger.info(letter)
        if moderator.validate_user_resp(letter):
            self.cur_t += 1
            if self.cur_t <= self.maxt:
                self.score += ord(self.letter)
                speech_text = "Correcto ahora : " + moderator.generate_letter()
            else:
                speech_text = "Hemos acabado. Tu puntuación de hoy: " + str(moderator.score) + "puntos ¡Enhorabuena!"
                
        else:
            if moderator.current_group == 2:
                speech_text = "juegos perdidos"
                moderator.start_new_game()
            else:
                new_letter = moderator.switch_to_group_2()
                speech_text = f"secuencia incorrecta ahora grupo 2: {new_letter}"
        
        logger.info("------------ Repeating handler -------")

        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response

class EndGameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("EndGameIntent")(handler_input)
    def handle(self,handler_input):
        pass
    
class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "Voy a decir algunas letras. Escucha con atención y cuando yo haya terminado, " 
            "repítalo inmediatamente."
            "Si necesitas otra vez saber cómo se juega, ¡pregúntame!"
        )

        handler_input.response_builder.speak(speech_text).ask(speech_text)

        return handler_input.response_builder.response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

moderator = Engine()

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StartGameIntentHandler())
sb.add_request_handler(EmpezarJuegoIntentHandler())
sb.add_request_handler(RepeatSequenceIntentHandler())
sb.add_request_handler(AyudaIntentHandler())
# sb.add_request_handler(CancelOrStopIntentHandler())
# sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
