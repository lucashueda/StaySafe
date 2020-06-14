# coding:utf-8
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

from staysafegmaps import *

from kivy.config import Config
Config.set('graphics', 'width',  500)
Config.set('graphics', 'height', 760)

p = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(p)


def rect_to_bb(rect):
		# take a bounding predicted by dlib and convert it
		# to the format (x, y, w, h) as we would normally do
		# with OpenCV
		x = rect.left()
		y = rect.top()
		w = rect.right() - x
		h = rect.bottom() - y
 
		# return a tuple of (x, y, w, h)
		return (x, y, w, h)

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


def sound_alarm(path):
	# play an alarm sound
	playsound.playsound(path)

test = StaySafe_places()

places = test.get_places_rec(max_results=10,max_radius=10000)

# for i in places:
#     file_path = 'figures/' + i+'.png'
#     place = places[i]
#     test.get_map(place_info=place, file_path=file_path)


class KivyCamera(Image):
    def __init__(self, capture = cv2.VideoCapture(0), fps = 30, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)

        self.capture = cv2.VideoCapture(0,  cv2.CAP_DSHOW)
        Clock.schedule_interval(self.update, 1.0 / 60)

        # self.capture = capture
        # Clock.schedule_interval(self.update, 1.0 / fps)
        self.EYE_AR_THRESH = 0.2
        self.EYE_AR_CONSEC_FRAMES = 20
        # initialize the frame counter as well as a boolean used to
        # indicate if the alarm is going off
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

        self.pop = Popup(title="Voce parece estar com sono, vamos descansar?", content= box, size_hint = (None, None), size = (400,300))

        sim = Button(text='Sim, preciso descansar')
        sim.bind(on_release = self.on_stop)
        nao = Button(text='Nao, estou bem')
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

        # frame = cv2.resize(frame, (50, 100)) 

        if(ret):
        # frame = imutils.resize(frame, width=1000)
          gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect faces in the grayscale frame
          rects = self.detector(gray, 0)
        else:
          rects = []

          # loop over the face detections
        for rect in rects:
          # determine the facial landmarks for the face region, then
          # convert the facial landmark (x, y)-coordinates to a NumPy
          # array
          shape = self.predictor(gray, rect)

          if(self.initial_recognition):

            (x, y, w, h) = rect_to_bb(rect)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

            for i in range(1,68):
              cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 1, (0,255,255), thickness=-1) #For each point, draw a red circle with thickness2 on the original frame

            # time.sleep(5)

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
            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[self.lStart:self.lEnd]
            rightEye = shape[self.rStart:self.rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0
                    # compute the convex hull for the left and right eye, then


            # visualize each of the eyes
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                    # check to see if the eye aspect ratio is below the blink
            # threshold, and if so, increment the blink frame counter
            if ear < self.EYE_AR_THRESH:
              self.COUNTER += 1
              # if the eyes were closed for a sufficient number of
              # then sound the alarm
              if self.COUNTER >= self.EYE_AR_CONSEC_FRAMES:
                # if the alarm is not on, turn it on
                if not self.ALARM_ON:
                  self.ALARM_ON = True
                  # check to see if an alarm file was supplied,
                  # and if so, start a thread to have the alarm
                  # sound played in the background
                  # if args["alarm"] != "":
                  t = Thread(target=sound_alarm,
                    args=('alarm.wav',))
                  t.deamon = True
                  t.start()
                  self.warning_popup()

                    # ALARM_ON = False
                    # time.sleep(1)

                # draw an alarm on the frame
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # otherwise, the eye aspect ratio is not below the blink
            # threshold, so reset the counter and alarm
            else:
              self.COUNTER = 0
              self.ALARM_ON = False
            
            cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture

    def on_stop(self, *args):
        app = App.get_running_app()
        app.root.current = 'safe_places'
        self.pop.dismiss()
        self.capture.release()
        # captura.release()
        cv2.destroyAllWindows()

class FaceCam(Screen):
    # def __init__(self, **kwargs):
    #   super(FaceCam, self).__init__( **kwargs)

    def get_string(self):
      self.ids.label.text = self.ids.fcam.teste
    # pass

class Places(Screen):
    def __init__(self, **kwargs):
      super().__init__(**kwargs)
      Clock.schedule_once(self._do_setup)

    def _do_setup(self, *l,  p = places):

      keys = []
      distances = []
      for key in places.keys():
        keys.append(key)
        distances.append(float(places[key]['distance'][:3]))

      sorted_df = pd.DataFrame({'chaves': keys, 'd': distances})
      
      sorted_df = sorted_df.sort_values(by='d', ascending=True)

      for i in range(sorted_df.shape[0]):
        # print(places)
        button = Button(text=sorted_df.chaves.values[i][:30] + ' | ' + sorted_df.d.values[i].astype(str) + ' km', font_size = 15, 
          size_hint_y = None, height=100)

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

class Map(Screen):
  pass

class SM(ScreenManager):
  pass

class debugger(App):
  def build(self):
    return SM()

if __name__ == '__main__':
    debugger().run()