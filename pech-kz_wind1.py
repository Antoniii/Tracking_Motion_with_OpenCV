# source KZ-PANDA/bin/activate ##too
# import the necessary packages

## conda activate KZ37

from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np 
#import pandas
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",  help="path to the video file") # default="pech1.avi",
#ap.add_argument("-a", "--min-area", type=int, default=400, help="minimum area size")
args = vars(ap.parse_args())
 
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)
 
# otherwise, we are reading from a video file
else:
	vs = cv2.VideoCapture(args["video"])
 
# initialize the first frame in the video stream
firstFrame = None

print("Press 'q' or 'Ctrl+C' for break")

min_area = int(input("Input min area (for example, 400): "))

height=int(input("Input 1 parameter like a odd number (for example, 21): "))
width=int(input("Input 2 parameter like a odd number (for example, 21): "))
kernel=(height,width)
#kernel=(21, 21)

N1 = int(input("Input lower color (for example, 240): "))
N2 = int(input("Input upper color (for example, 255): "))

time = [] 
#df = []
#df = pandas.DataFrame(columns = ["Start", "End"])

# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	text = "Motionless"
 
	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if frame is None:
		break

	lower_white = np.array([N1,N1,N1])
	upper_white = np.array([N2,N2,N2])
	mask = cv2.inRange(frame, lower_white, upper_white)
	res = cv2.bitwise_and(frame,frame, mask= mask)
	#cv2.imshow('res',res)
 
	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	res = imutils.resize(res, width=500)
	gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY) #frame
	gray = cv2.GaussianBlur(gray, kernel, 0) #defalt kernel=(21,21)
 
	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue
	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
 
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < min_area:#args["min_area"]:
			continue
 
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Motion"

	# draw the text and timestamp on the frame
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	
	if text == "Motionless": # WTF?
		time.append(datetime.datetime.now().strftime("%I:%M:%S%p"))
	else:
		time.append(datetime.datetime.now().strftime("%I:%M:%S%p"))
	# show the frame and record if the user presses a key
	#cv2.imshow("Thresh", thresh)
	cv2.imshow('Result from filter',res)
	cv2.imshow("Frame", frame)
	#cv2.imshow("Frame Delta", frameDelta)
	
	'''
	for i in range(len(time)):
		print(time[i])
	'''
	key = cv2.waitKey(1) & 0xFF
	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break
'''
for i in range(0, len(time), 2): 
	df = df.append({"Start":time[i], "End":time[i + 1]}, ignore_index = True) 

# Creating a csv file in which time of movements will be saved 
df.to_csv("Time_of_movements_motion.txt")
#df.to_csv("Time_of_movements_motion.csv")
'''

f = open('Time_of_movements_motion.txt', 'w')
f.write(str(time))
f.close()


# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()

# python pech-kz_wind.py --video pech1.avi