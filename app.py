import kivy
# kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.image import Image

from kivy.config import Config
Config.set('graphics', 'width',  500)
Config.set('graphics', 'height', 760)

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import time
import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture

####
####   KV LANG
####

Builder.load_string("""
#:import SlideTransition kivy.uix.screenmanager.SlideTransition
<Main>:
    BoxLayout:
		background_color: 1, 1,1, .85
    	padding: 10
    	spacing: 70
    	orientation: 'vertical'
    	ActionBar:
        	ActionView:
	    		ActionPrevious:
	    			title: 'Início'
	    		ActionButton:
	    			text: 'Menu'
    	Image:
	        source: 'figs/capa2.jpg'
    	GridLayout:
    		spacing: 50
    		padding: 20
	    	cols: 1
	        Button:
	        	background_normal: ''
	    		background_color: 1, .3, .0, .85
	            text: 'Câmera'
	            height: '75dp'
	            size_hint_y: None
		        on_release:
	        		app.root.transition = SlideTransition(direction='down')
	        		app.root.current = 'facecam'
	        Button:
	        	background_normal: ''
	    		background_color: 1, .0, .4, .85
	            text: 'Reconhecer espécie'
	            height: '75dp'
	            size_hint_y: None
		        on_release:
	        		app.root.transition = SlideTransition(direction='up')
	        		app.root.current = 'cameraclick'

<FaceCam>:
	BoxLayout:
		orientation: 'vertical'
    	padding: 10
    	spacing: 80
    	ActionBar:
    	    ActionView:
	    		ActionPrevious:
	    			title: 'Câmera'
	    			on_release: app.root.current = 'main'
	    		ActionButton:
	    			text: 'Menu'
	    			on_release: app.root.current = 'main'
		KivyCamera:
		    id: camera
    	GridLayout:
	    	cols: 1
	    	spacing: 50
    		padding: 10

		    ToggleButton:
		        text: 'Iniciar gravação'    
				height: '75dp'
		        on_press: 
		        	root.build()
            Button:
                background_normal: ''
                background_color: 1, .0, .4, .85
                text: 'Enviar'
                on_release:
                    app.root.transition = SlideTransition(direction='right')
                    app.root.current = 'fim'
""")

###
###   FIM KV LANG
###


## Criando telas

#
class Main(Screen):

  pass

class KivyCamera(Image):
    def __init__(self, capture = cv2.VideoCapture(0), fps =30, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # convert it to texture
            cv2.putText(frame, "Iniciando monitoramento...", (10, 30),
					    cv2.FONT_HERSHEY_TRIPLEX , 0.7, (0, 255, 255), 2)
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture

class FaceCam(Screen):
  def build(self):
      self.capture = cv2.VideoCapture(0)
      self.my_camera = KivyCamera(capture=self.capture, fps=30)
      return self.my_camera

  def on_stop(self):
      #without this, app will not exit even if the window is closed
      self.capture.release()


## Gerenciador e telas
sm = ScreenManager()
sm.add_widget(Main(name='main'))
sm.add_widget(FaceCam(name='facecam'))

class MyApp(App):

    def build(self):
        return sm


if __name__ == '__main__':
    MyApp().run()