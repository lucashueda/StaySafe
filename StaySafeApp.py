# Kivy widgets
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from functools import partial
# Outros pacotes
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2
import pandas as pd
dlib.DLIB_USE_CUDA = True

# Lib autoral de requisição à API do googlemaps
from staysafegmaps import *

# Setando tamanho de app
from kivy.config import Config
Config.set('graphics', 'width',  500)
Config.set('graphics', 'height', 760)

# Instanciando Landmark detector do dlib
p = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(p)

# Função que reconhece o bloco onde se encontra o rosto das pessoas
def rect_to_bb(rect):
		x = rect.left()
		y = rect.top()
		w = rect.right() - x
		h = rect.bottom() - y

		return (x, y, w, h)

# Função que computa o Eye Aspect Ratio (https://vision.fe.uni-lj.si/cvww2016/proceedings/papers/05.pdf)
def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])
	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)
	# return the eye aspect ratio
	return ear

# Função que aciona o alarme
def sound_alarm(path):
	# play an alarm sound
	playsound.playsound(path)


# Coletando os lugares seguros (postos) mais próximos, num raio de 10k KM)
test = StaySafe_places()
places = test.get_places_rec(max_results=10,max_radius=10000)


# Widget do tipo Image que cuida de todo o processamento da imagem e alerta de sonolência
class KivyCamera(Image):
    def __init__(self, capture = cv2.VideoCapture(0), fps = 30, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)

        self.capture = cv2.VideoCapture(0,  cv2.CAP_DSHOW)
        Clock.schedule_interval(self.update, 1.0 / 60)

        self.EYE_AR_THRESH = 0.2
        self.EYE_AR_CONSEC_FRAMES = 20

        self.COUNTER = 0
        self.ALARM_ON = False
        self.count = 0

        self.initial_recognition = True
        self.init_frames = 0

        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        self.teste = 'teste camera'

        global predictor
        global detector

        self.predictor = predictor
        self.detector = detector

        # Checa se já existe um popup
        self.ispop = False

        box = BoxLayout(orientation = 'vertical', padding = 20, spacing= 30)
        botoes = BoxLayout()

        self.pop = Popup(title="Vamos descansar?", content= box, size_hint = (None, None), size = (400,300))

        sim = Button(text='Descansar', font_size=28)
        sim.bind(on_release = self.on_stop)
        nao = Button(text='Continuar\nviagem', font_size=28)
        # nao.bind(on_release =self.ispop_false)
        nao.bind(on_release = self.ispop_false)

        botoes.add_widget(sim)
        botoes.add_widget(nao)

        atencao = Image(source='perigo.gif')

        box.add_widget(atencao)
        box.add_widget(botoes)

  
    def ispop_false(self, *args):
        # self.start()
        self.pop.dismiss()
        self.ispop = False

    def warning_popup(self, *args):
        if(self.ispop == False):
          # self.ispop = False
          self.pop.open()
        else:
          x = None


    def start(self):
        self.capture = cv2.VideoCapture(0,  cv2.CAP_DSHOW)
        Clock.schedule_interval(self.update, 1.0 / 60)

    def update(self, dt):
        ret, frame = self.capture.read()

        if(ret):

          gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

          rects = self.detector(gray, 0)
        else:
          rects = []


        for rect in rects:
 
          shape = self.predictor(gray, rect)

          if(self.initial_recognition):

            (x, y, w, h) = rect_to_bb(rect)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

            for i in range(1,68):
              cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 1, (0,255,255), thickness=-1) 


            if(self.init_frames < 50):
              cv2.putText(frame, "Iniciando monitoramento...", (10, 30),
                cv2.FONT_HERSHEY_TRIPLEX , 0.7, (0, 255, 255), 2)
            elif((self.init_frames >= 50)&(self.init_frames <70)):
              cv2.putText(frame, "Face detectada, dirija com cuidado!", (10, 30),
                cv2.FONT_HERSHEY_TRIPLEX , 0.7, (0, 255, 255), 2)
            elif((self.init_frames >= 70)&(self.init_frames <80)):
              x = None
            else:
              self.initial_recognition = False
            self.init_frames += 1
          else:

            shape = face_utils.shape_to_np(shape)

            leftEye = shape[self.lStart:self.lEnd]
            rightEye = shape[self.rStart:self.rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if ear < self.EYE_AR_THRESH:
              self.COUNTER += 1

              if self.COUNTER >= self.EYE_AR_CONSEC_FRAMES:

                if not self.ALARM_ON:
                  self.ALARM_ON = True

                  t = Thread(target=sound_alarm,
                    args=('alarm.wav',))
                  t.deamon = True
                  t.start()

                  # Dispara o popup no app
                  self.warning_popup()

                cv2.putText(frame, "Sonolência detectada, acionando alarme!", (10, 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            else:
              self.COUNTER = 0
              self.ALARM_ON = False
            
            # cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
            #   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            self.texture = image_texture

    def on_stop(self, *args):
        app = App.get_running_app()
        app.root.current = 'safe_places'
        self.pop.dismiss()
        self.capture.release()
        cv2.destroyAllWindows()

# Screen que cuida da parte de visão computacional
class FaceCam(Screen):
    def get_string(self):
      self.ids.label.text = self.ids.fcam.teste

# Screen que cuida dos postos próximos
class Places(Screen):
    def __init__(self, **kwargs):
      super().__init__(**kwargs)
      Clock.schedule_once(self._do_setup)

    def _do_setup(self, *l,  p = places):

      keys = []
      distances = []
      ratings = []
      time = []
      for key in places.keys():
        keys.append(key)
        distances.append(float(places[key]['distance'][:3]))
        time.append(places[key]['travel_time'])

      sorted_df = pd.DataFrame({'chaves': keys, 'd': distances, 'time': time})
      
      sorted_df = sorted_df.sort_values(by='d', ascending=True)

      for i in range(sorted_df.shape[0]):
        # print(places)
        button = Button(text= sorted_df.time.values[i] + 55*' '  + 'rating' + '\n' + \
                        sorted_df.chaves.values[i][:30] + ' | ' + sorted_df.d.values[i].astype(str) + ' km', font_size = 25, 
          size_hint_y = None, height=100, background_color = (0.3,0.3,0.3,1))

        button.bind(on_release= partial(self.open_map, sorted_df.chaves.values[i]))

        self.ids.safe_places.add_widget(button)

    def open_map(self, key, *args):

      global test, places

      name =  "_".join(key.split())

      file_path = 'figures/' +  name  +'.png'
      place = places[key]
      test.get_map(place_info=place, file_path=file_path)

      app = App.get_running_app()
      
      app.root.get_screen('map').ids.choose_map.source = file_path
      app.root.current = 'map'

# Screen que plota o mapa na tela
class Map(Screen):
  pass

# Screen que gerencia as Screens
class SM(ScreenManager):
  pass

class StaySafeApp(App):
  def build(self):
    return SM()

if __name__ == '__main__':
    StaySafeApp().run()