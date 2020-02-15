# создаём виртуальную среду для отсекания возможных проблем с зависимостями 
### Redactor Sublime Text 2, Version 2.0.2, Build 2221 # (for encoding)

# *for GNU/Linux* 
## python -m venv KZ # создание виртуальной среды KZ-PANDA
## source KZ/bin/activate # вход в виртуальную среду
# pip install --upgrade pip
# pip install opencv-python
# pip install imutils
# pip install Pillow
# pip install nuitka # don't working
## deactivate # выход из окружения виртуальной среды

#*for pypy* ## нет нужных библиотек для pypy3 :(
## sudo snap install --classic pypy3
# virtualenv -p pypy3 PYPYKZ
# source PYPYKZ/bin/activate 
# pypy3 filename.py

# *for Windows => 7*
## https://conda.io/en/latest/miniconda.html
## conda create -n KZNuitka python=3.7 # создание виртуальной среды с требуемой версией Python
### conda activate KZNuitka # вход в виртуальную среду
# /установка пакетов/
## conda install -c conda-forge opencv ## or ## pip install opencv-python-headless
## conda install -c pjamesjoyce imutils
# conda install -c conda-forge nuitka # don't working
# python -m nuitka --standalone --mingw64 --plugin-enable=tk-inter --plugin-enable=numpy demo_with_nuitka.py
### conda deactivate # выход из окружения виртуальной среды
# where python # путь до папки с Miniconda (и виртуальными средами)

# импортируем необходимые библиотеки
from tkinter import *
from PIL import Image, ImageTk
import cv2
import threading
from tkinter.ttk import Combobox
import numpy as np
import imutils
import datetime
from tkinter import filedialog
from pathlib import Path
from collections import deque 
from tkinter import messagebox


current_dir = Path.cwd() # путь текущей директории

root = Tk() # создаём главное окно для интерфейса
root.title("Camera")
root.filename = filedialog.askopenfilename(initialdir = current_dir, # initialdir = "/run/media/rick/DATA/Kazahi"
 title = "Select videofile", filetypes = (("avi files", "*.avi"),("all files", "*.*")))
print(root.filename) # вывод окна для выбора требуемого видеофайла

print("\nPress 'q' or 'Ctrl+C' for break\n") # сообщение в терминал-консоль для завершения работы

# создаём переменные для всех основных используемых параметров
# и задаём им начальные значения
min_area = 400
min_threshold = 66 #5 # for motion detected

N1 = 190
N2 = 255

threshold_min = 100 # для выделения интересующей области на кадре

time = [] 

time2 = [0]*2 # счётчик минут / или секунд -- по заданному условию см. ниже
time2minute = deque(time2, maxlen=2)
time_parameter = 56

framemes = []
d_maxlen = 15 # кол-во сохраняемых в дек кадров для сравнения крайних и детектирования движения
d = deque(framemes, maxlen=d_maxlen)
movement = False

firstFrame = None

# параметры фильтрации
height=21
width=21
kernel=(height,width)

size_windows = 950 # размер окна

# считываем файл или real-time веб-камеру (параметры: -1 или 0 (или 1))
cap = cv2.VideoCapture(root.filename)#(0)#("pech.avi")

PRC = 0 # parameter of Real Time Camera

text_status = 'error 404: status is not defined'

parameters = [0]*9
parameters[0] = min_area
parameters[1] = threshold_min 
parameters[2] = N1
parameters[3] = N2
parameters[4] = height
parameters[5] = width
parameters[6] = min_threshold
parameters[7] = d_maxlen
parameters[8] = time_parameter

# функция основного рабочего цикла
def videoLoop():
	global root
	global cap
	global firstFrame
	global movement

	vidLabel = Label(root, anchor=NW)
	vidLabel.pack(expand=YES, fill=BOTH)
	while True:
		_, frame = cap.read() # считываем текущий кадр

		lower_white = np.array([N1,N1,N1]) # нижний уровень белого цвета
		upper_white = np.array([N2,N2,N2]) # верхний уровень белого цвета
		mask = cv2.inRange(frame, lower_white, upper_white) # создаём маску для изображения
		res = cv2.bitwise_and(frame,frame, mask= mask)

		text = "Motionless"

		# изменяем размер окна
		frame = imutils.resize(frame, width=size_windows)
		d.append(frame)
		res = imutils.resize(res, width=size_windows)

		# фильтруем
		gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY) #frame
		gray = cv2.GaussianBlur(gray, kernel, 0)

        # if the first frame is None, initialize it
		if firstFrame is None:
			firstFrame = gray
			continue
        # compute the absolute difference between the current frame and
        # first frame
		frameDelta = cv2.absdiff(firstFrame, gray)
		thresh = cv2.threshold(frameDelta, threshold_min, 255, cv2.THRESH_BINARY)[1]
     
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
		thresh = cv2.dilate(thresh, None, iterations=2)
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
		cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M%p"), (frame.shape[0] - 100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

        # условие распознавания движения-остановки и запись времени в файл
		frameDelta2 = cv2.absdiff(d[0], d[-1])
		diff = int(((frameDelta2 ** 2) / (1 * 10 ** 6)).sum())

		if diff > min_threshold:
			if not movement:
				time.append(datetime.datetime.now().strftime("start: %I:%M:%S%p"))
				time2minute.append(datetime.datetime.now().second) #.minute # фиксирует время начала остановки в секундах или минутах соответственно
				movement = not movement
				global text_status
				text_status = 'detected movement'
				#print(text_status) # вывод статуса в терминал-консоль
				#messagebox.showinfo('Status', text_status)
		else:
			if movement:
				time.append(datetime.datetime.now().strftime("end: %I:%M:%S%p"))
				time2minute.append(datetime.datetime.now().second) #.minute # фиксирует время начала нового движения в секундах или минутах соответственно
				movement = not movement
				text_status = 'nothing is moving now'
				#print(text_status)
				#messagebox.showinfo('Status', text_status)

		# всплывающее окно-оповещение о времени простоя в секундах или минутах соответственно см.выше
		if abs(time2minute[0] - time2minute[1]) > time_parameter:
			period = abs(time2minute[0] - time2minute[1])
			messagebox.showinfo('Status', 'Ararm! Timeout Exceeded: {} ({},{})'.format(period,time2minute[0],time2minute[1]))

        # отображение видео в окне tkinter для работы в режиме поддержки интерфейса
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		frame = Image.fromarray(frame)
		frame = ImageTk.PhotoImage(frame)
		vidLabel.configure(image=frame)
		vidLabel.image = frame
        

container = Frame() # создаём контейнер на главном окне для расположения кнопок и полей ввода
container.pack(side='top', fill='both', expand=True)
#container.grid_rowconfigure(0, weight=1)

# создаём необходимые кнопки и поля для ввода параметров
########################################################################
lbl5 = Label(container, text="Min area = ")  
lbl5.grid(column=0, row=0) 

txt5 = Entry(container,width=8)  
txt5.grid(column=1, row=0) 

def clicked5():
    global min_area
    global parameters
    min_area = int(txt5.get())
    parameters[0] = min_area 

btn5 = Button(container, text="Input area", command=clicked5)
#btn.pack(side="left", fill=None, expand=None, padx=10, pady=10)
btn5.grid(column=2, row=0)

########################################################################
lbl = Label(container, text="Lower color (N1) = ")  
lbl.grid(column=0, row=1) 
#lbl.place(x=0, y=0)

txt = Entry(container,width=8)  
txt.grid(column=1, row=1) 
#txt.place(x=10, y=0)

def clicked():
    #print("{} was clicked".format(txt.get()))
    global N1
    global parameters
    N1 = int(txt.get())
    parameters[2] = N1

btn = Button(container, text="Input N1", command=clicked)
#btn.pack(side="left", fill=None, expand=None, padx=10, pady=10)
btn.grid(column=2, row=1) 

########################################################################
lbl2 = Label(container, text="Upper color (N2) = ")  
lbl2.grid(column=3, row=1) 

txt2 = Entry(container,width=8)  
txt2.grid(column=4, row=1) 

def clicked2():
    global N2
    global parameters
    N2 = int(txt2.get())
    parameters[3] = N2

btn2 = Button(container, text="Input N2", command=clicked2)
#btn2.pack(side="left", fill=None, expand=None, padx=10, pady=10)
btn2.grid(column=5, row=1)

########################################################################
lbl1 = Label(container, text="Param 1 = ")  
lbl1.grid(column=0, row=2) 

combo = Combobox(container,width=8)  
combo['values'] = [x for x in range(1, 39, 2)] 
combo.current(11)  # установите вариант по умолчанию  
combo.grid(column=1, row=2)

def clicked3():
    global height
    global parameters
    height = combo.get()
    parameters[4] = height

btn3 = Button(container, text="Input param 1", command=clicked3)
btn3.grid(column=2, row=2)#.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

########################################################################
lbl3 = Label(container, text="Param 2 = ")  
lbl3.grid(column=3, row=2) 

combo2 = Combobox(container,width=8)  
combo2['values'] = [x for x in range(1, 39, 2)] 
combo2.current(10)  # установите вариант по умолчанию  
combo2.grid(column=4, row=2)

def clicked4():
    global width
    global parameters
    width = combo2.get()
    parameters[5] = width

btn4 = Button(container, text="Input param 2", command=clicked4)
btn4.grid(column=5, row=2)#.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

########################################################################
def clicked1():
    global cap
    cap = cv2.VideoCapture(root.filename)

btn1 = Button(root, text="Open videofile", command=clicked1)
btn1.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

########################################################################
# lbl7 = Label(container, text="RealTimeCam = ")  
# lbl7.grid(column=6, row=2) 

# combo7 = Combobox(container,width=8)  
# combo7['values'] = [x for x in range(-1, 2, 1)] 
# combo7.current(1)  # установите вариант по умолчанию  
# combo7.grid(column=7, row=2)

# def clicked7():
#     global PRC
#     PRC = int(combo7.get())
#     #print("{} was clicked".format(combo.get()))

# btn7 = Button(container, text="Input PRC", command=clicked7)
# btn7.grid(column=8, row=2)

lbl7 = Label(container, text="TimeParam = ")  
lbl7.grid(column=6, row=2) 

combo7 = Entry(container,width=8)  
combo7.grid(column=7, row=2)

def clicked7():
    global time_parameter
    global parameters
    time_parameter = int(combo7.get())
    parameters[8] = time_parameter

btn7 = Button(container, text="Input PRC", command=clicked7)
btn7.grid(column=8, row=2)

########################################################################
def clicked0():
    global cap
    cap = cv2.VideoCapture(PRC)

btn0 = Button(root, text="Open realtime camera", command=clicked0)
btn0.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

########################################################################
lbl6 = Label(container, text="Tresh min = ")  
lbl6.grid(column=3, row=0) 

txt6 = Entry(container,width=8)  
txt6.grid(column=4, row=0) 

def clicked6():
    global threshold_min
    global parameters
    threshold_min = int(txt6.get())
    parameters[1] = threshold_min  

btn6 = Button(container, text="Input Tresh", command=clicked6)
#btn.pack(side="left", fill=None, expand=None, padx=10, pady=10)
btn6.grid(column=5, row=0)
########################################################################
lbl8 = Label(container, text="MotionMin = ")  
lbl8.grid(column=6, row=0) 

txt8 = Entry(container,width=8)  
txt8.grid(column=7, row=0) 

def clicked8():
	global min_threshold
	global parameters
	min_threshold = int(txt8.get())
	parameters[6] = min_threshold 

btn8 = Button(container, text="Input MotMin", command=clicked8)
btn8.grid(column=8, row=0)
########################################################################
lbl9 = Label(container, text="Max len = ")  
lbl9.grid(column=6, row=1) 

txt9 = Entry(container,width=8)  
txt9.grid(column=7, row=1) 

def clicked9():
	global d_maxlen
	global parameters
	d_maxlen = int(txt9.get())
	parameters[7] = d_maxlen 

btn9 = Button(container, text="Input MaxLen", command=clicked9)
btn9.grid(column=8, row=1)
######################################################################## 


# запуск рабочего цикла
videoThread = threading.Thread(target=videoLoop, args=())
videoThread.start()
root.mainloop()

# записываем в файл временя остановки выделенного объекта
with open('Time_of_movements_motion.txt', 'w') as f:
	f.write(str(time))

# записываем в файл текущий набор параметров
f = open('Current_parameters.txt', 'w')
f.write('min_area = ')
f.write(str(parameters[0]))
f.write('\n')
f.write('threshold_min = ')
f.write(str(parameters[1]))
f.write('\n')
f.write('Lower color (N1) = ')
f.write(str(parameters[2]))
f.write('\n')
f.write('Upper color (N2) = ')
f.write(str(parameters[3]))
f.write('\n')
f.write('Param 1 = ')
f.write(str(parameters[4]))
f.write('\n')
f.write('Param 2 = ')
f.write(str(parameters[5]))
f.write('\n')
f.write('min_threshold = ')
f.write(str(parameters[6]))
f.write('\n')
f.write('d_maxlen = ')
f.write(str(parameters[7]))
f.write('\n')
f.write('time_parameter = ')
f.write(str(parameters[8]))
f.close()

#print(time2minute)