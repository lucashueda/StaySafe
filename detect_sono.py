import cv2
import dlib
import cv2
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
dlib.DLIB_USE_CUDA = True

EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 20
# initialize the frame counter as well as a boolean used to
# indicate if the alarm is going off
COUNTER = 0
ALARM_ON = False

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

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
ap.add_argument("-a", "--alarm", type=str, default="",
	help="path alarm .WAV file")
ap.add_argument("-w", "--webcam", type=int, default=0,
	help="index of webcam on system")
args = vars(ap.parse_args())

def sound_alarm(path):
	# play an alarm sound
	playsound.playsound(path)


captura = cv2.VideoCapture(0)
 
count = 0

initial_recognition = True
init_frames = 0
p = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(p)

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

print("[INFO] starting video stream thread...")
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)


initial_recognition = True
init_frames = 0

# loop over frames from the video stream
while True:
	# grab the frame from the threaded video file stream, resize
	# it, and convert it to grayscale
	# channels)
	frame = vs.read()
	frame = imutils.resize(frame, width=1000)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# detect faces in the grayscale frame
	rects = detector(gray, 0)

		# loop over the face detections
	for rect in rects:
		# determine the facial landmarks for the face region, then
		# convert the facial landmark (x, y)-coordinates to a NumPy
		# array
		shape = predictor(gray, rect)

		if(initial_recognition):

			(x, y, w, h) = rect_to_bb(rect)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

			for i in range(1,68):
				cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 1, (0,255,255), thickness=-1) #For each point, draw a red circle with thickness2 on the original frame

			# time.sleep(5)

			if(init_frames < 50):
				cv2.putText(frame, "Iniciando monitoramento...", (10, 30),
					cv2.FONT_HERSHEY_TRIPLEX , 0.7, (0, 255, 255), 2)
			elif((init_frames >= 50)&(init_frames <70)):
				cv2.putText(frame, "Face detectada, dirija com cuidado!", (10, 30),
					cv2.FONT_HERSHEY_TRIPLEX , 0.7, (0, 255, 255), 2)
			elif((init_frames >= 70)&(init_frames <80)):
				x = None
			else:
				initial_recognition = False
			init_frames += 1
		else:

			shape = face_utils.shape_to_np(shape)
			# extract the left and right eye coordinates, then use the
			# coordinates to compute the eye aspect ratio for both eyes
			leftEye = shape[lStart:lEnd]
			rightEye = shape[rStart:rEnd]
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
			if ear < EYE_AR_THRESH:
				COUNTER += 1
				# if the eyes were closed for a sufficient number of
				# then sound the alarm
				if COUNTER >= EYE_AR_CONSEC_FRAMES:
					# if the alarm is not on, turn it on
					if not ALARM_ON:
						ALARM_ON = True
						# check to see if an alarm file was supplied,
						# and if so, start a thread to have the alarm
						# sound played in the background
						if args["alarm"] != "":
							t = Thread(target=sound_alarm,
								args=(args["alarm"],))
							t.deamon = True
							t.start()
							# ALARM_ON = False
							# time.sleep(1)

					# draw an alarm on the frame
					cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			# otherwise, the eye aspect ratio is not below the blink
			# threshold, so reset the counter and alarm
			else:
				COUNTER = 0
				ALARM_ON = False
			
			cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
				cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()


# while(1):
#     ret, frame = captura.read()


#     if(count%2==0):
#         rects = detector(frame, 0)

#         #For each detected face  
#         for k,d in enumerate(rects):

#             (x, y, w, h) = rect_to_bb(d)
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#             #Get coordinates
#             shape = predictor(frame, d)
#             #There are 68 landmark points on each face
#             for i in range(1,68):

#                 cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 1, (0,255,0), thickness=-1) #For each point, draw a red circle with thickness2 on the original frame


		
#         cv2.imshow("Video", frame)
			 
#     k = cv2.waitKey(30) & 0xff
#     if k == 27:
#         break
#     count = count+1

# captura.release()
# cv2.destroyAllWindows()

# import cv2
# # Caso você tenha apenas 1 webcam, set device = 0, caso contrario, escolha seu device(webcam) de preferencia, 0, 1, 2 ,3 ...
# cap = cv2.VideoCapture(0)
# while True:
#   # Obtendo nossa imagem através da webCam e transformando-a preto e branco
#     _, image = cap.read()
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
#     # Mostrando a imagem na tela
#     cv2.imshow("Output", image)
		
#     #tecla para para sair do loop
#     k = cv2.waitKey(5) & 0xFF
#     if k == 27:
#         break
# cv2.destroyAllWindows()
# cap.release()