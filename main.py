import cv2
import math
import numpy as np
from math import sqrt, acos
import tkinter as tk
from pynput.keyboard import Controller, Key

#----------------------------------------------------------------------------
# Set "exit_loop" as false for the while loop
#----------------------------------------------------------------------------
exit_loop = False

#----------------------------------------------------------------------------
# Make a circle around the clock
#----------------------------------------------------------------------------
def create_circular_mask(image, center, radius):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    return mask

#----------------------------------------------------------------------------
# Find center coordinates and print (x,y) for the position the user clicked
#----------------------------------------------------------------------------
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global center
        global clicked_x, clicked_y
        clicked_x = x
        clicked_y = y
        center = (x, y)
        cv2.circle(image, center, 1, (0, 0, 0), -1)
        print(f"Clicked at coordinates (x={clicked_x}, y={clicked_y})")
        #----------------------------------------------------------------------------
        #After the coordinates of the mouse click is register,
        #simulate a space bar click for exiting the window which pupped up.
        #----------------------------------------------------------------------------
        keyboard.tap(Key.space)


#----------------------------------------------------------------------------
#When used, an exiting of the loop will commence
#----------------------------------------------------------------------------
def start_exiting_loop():
    global exit_loop
    digital_clock.destroy()
    cv2.destroyAllWindows()
    exit_loop = True

#----------------------------------------------------------------------------
# Define variable
#----------------------------------------------------------------------------
center = []
clicked_x = []
clicked_y = []
h = []

#----------------------------------------------------------------------------
# While loop begins
#----------------------------------------------------------------------------
while exit_loop == False:
    #------------------------------------------------------------------------
    # Reads the image from the users location and shows it to the user
    #------------------------------------------------------------------------
    image = cv2.imread(r'C:\Users\herma\Desktop\Bildebehandling/live.jpg')
    cv2.imshow('Image', image)

    #------------------------------------------------------------------------
    # Register the mouseclick on the image
    #------------------------------------------------------------------------
    cv2.setMouseCallback('Image', mouse_callback)

    #------------------------------------------------------------------------
    # Wait for the user to click the center of the clock
    # and then exits the image
    #------------------------------------------------------------------------
    keyboard = Controller()

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #------------------------------------------------------------------------
    # Register the created circle from the function "create_circular_mask" and crop it a little
    #------------------------------------------------------------------------
    new_circle = create_circular_mask(image, center, 120)
    crop = cv2.bitwise_and(image, image, mask=new_circle)
    height, width, channels = crop.shape

    #------------------------------------------------------------------------
    # Gaussian filter before edge detection
    #------------------------------------------------------------------------
    _, thresh = cv2.threshold(crop, 50, 255, cv2.THRESH_BINARY)
    gaussian = cv2.GaussianBlur(thresh, (9, 9), 0)

    #------------------------------------------------------------------------
    # Edge detection with Canny
    #------------------------------------------------------------------------
    edges = cv2.Canny(gaussian, 100, 200, apertureSize=5, L2gradient=True)

    #------------------------------------------------------------------------
    # Set kernels for Erode and Dilate
    #------------------------------------------------------------------------
    kernel = np.ones((10, 10), np.uint8)  # (11,11)
    kernel2 = np.ones((15, 15), np.uint8)  # (13, 13)

    #------------------------------------------------------------------------
    # Erode and Dilate
    #------------------------------------------------------------------------
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.erode(edges, kernel2, iterations=1)

    #------------------------------------------------------------------------
    # Minimum and maximum length for HoughLinesP
    #------------------------------------------------------------------------
    minLineLength = 1500
    maxLineGap = 10

    #------------------------------------------------------------------------
    # Detect lines with HoughLinesP
    #------------------------------------------------------------------------
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 15, minLineLength, maxLineGap)

    #------------------------------------------------------------------------
    # Define the following names with some values
    #------------------------------------------------------------------------
    xmax1 = 0
    xmax2 = 0
    ymax1 = 0
    ymax2 = 0
    xs1 = 0
    xs2 = 0
    ys1 = 0
    ys2 = 0

    #------------------------------------------------------------------------
    #Find and defines the coordinates of the clock hands.
    #------------------------------------------------------------------------
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        if dx < 0:
            dx = dx * -1
        dy = y2 - y1
        if dy < 0:
            dy = dy * -1

        hypo = sqrt(dx ** 2 + dy ** 2)

        h.append(hypo)

    a = len(h)
    print(f"len(h) = {a}")
    h.sort(reverse=True)
    m = 0
    k = 0

    for f in range(a):
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx = x2 - x1
            if (dx < 0):
                dx = dx * -1
            dy = y2 - y1
            if (dy < 0):
                dy = dy * -1

            hypo2 = sqrt(dx ** 2 + dy ** 2)

            if hypo2 == h[0]:
                m = hypo2
                xmax1 = x1
                xmax2 = x2
                ymax1 = y1
                ymax2 = y2
                cv2.line(crop, (xmax1, ymax1), (xmax2, ymax2), (255, 0, 0), 3)

            if m == h[0]:
                if hypo2 == h[f]:
                    if (sqrt((xmax2 - x2) ** 2 + (ymax2 - y2) ** 2)) > 20:
                        if (sqrt((xmax1 - x1) ** 2 + (ymax1 - y1) ** 2)) > 20:
                            xs1 = x1
                            xs2 = x2
                            ys1 = y1
                            ys2 = y2
                            cv2.line(crop, (xs1, ys1), (xs2, ys2), (0, 255, 0), 3)
                            print("xs1=", xs1, " ys1=", ys1, " xs2=", xs2, " ys2=", ys2)
                            k = 1
                            break
        if (k == 1):
            break

    print(f"xmax1 = {xmax1}, ymax1 = {ymax1}, xmax2 = {xmax2} and ymax2 = {ymax2}")

    #------------------------------------------------------------------------
    # Define the center coordinates
    #------------------------------------------------------------------------
    print(f"center = {center}")
    xcenter = clicked_x
    ycenter = clicked_y
    print(f"xcenter = {xcenter} and ycenter = {ycenter}")

    #------------------------------------------------------------------------
    # Calculate the coordinates of hour hand tip and the minute hand tip
    #------------------------------------------------------------------------
    hassona1 = abs(xcenter - xs1)
    hassona2 = abs(xcenter - xs2)
    abdo1 = abs(xcenter - xmax1)
    abdo2 = abs(xcenter - xmax2)
    if (hassona1 > hassona2):
        xhours = xs1
        yhours = ys1
    else:
        xhours = xs2
        yhours = ys2

    if (abdo1 > abdo2):
        xminutes = xmax1
        yminutes = ymax1
    else:
        xminutes = xmax2
        yminutes = ymax2

    print(f"Tip coordinates for the clock hands (x,y): "
          f"hour = ({xhours}, {yhours}) and minute = ({xminutes}, {yminutes})")
    #------------------------------------------------------------------------
    # Calculation theta of each line using the law of cosines
    # ------------------------------------------------------------------------
    # calculating theta for hours hand
    # and prints it
    #------------------------------------------------------------------------
    l1 = sqrt(((xcenter - xhours) ** 2) + ((ycenter - yhours) ** 2))
    l2 = ycenter
    l3 = sqrt(((xcenter - xhours) ** 2) + ((0 - yhours) ** 2))
    cos_theta_hours = (((l1) ** 2) + ((l2) ** 2) - ((l3) ** 2)) / (2 * (l1) * (l2))

    theta_hours_radian = acos(cos_theta_hours)
    theta_hours = math.degrees(theta_hours_radian)
    print('theta_hours = ', theta_hours)

    #------------------------------------------------------------------------
    # Calculating theta for minutes hand
    #------------------------------------------------------------------------
    len1 = sqrt(((xcenter - xminutes) ** 2) + ((ycenter - yminutes) ** 2))
    len2 = ycenter
    len3 = sqrt(((xcenter - xminutes) ** 2) + ((0 - yminutes) ** 2))
    cos_theta_minutes = (((len1) ** 2) + ((len2) ** 2) - ((len3) ** 2)) / (2 * (len1) * (len2))

    theta_minutes_radian = acos(cos_theta_minutes)
    theta_minutes = math.degrees(theta_minutes_radian)
    print('theta_minutes = ', theta_minutes)

    #------------------------------------------------------------------------
    # Calculation of the hour hand and determine which half side of the clock
    # it points in
    #------------------------------------------------------------------------
    if (xhours > xcenter):
        right = 1
    else:
        right = 0

    if (right == 1):
        hournum = math.floor(theta_hours / 30)
    if (right == 0):
        hournum = math.floor(12 - (theta_hours / 30))

    if (hournum == 0):
        hournum = 12
    print('hours=', hournum)
    #------------------------------------------------------------------------
    # Calculation of the minute hand and determine
    # which half side of the clock it points in
    #------------------------------------------------------------------------
    if (xminutes > xcenter):
        right1 = 1
    else:
        right1 = 0

    if (right1 == 1):
        minutesnum = int(theta_minutes / 6)
    if (right1 == 0):
        minutesnum = math.floor(60 - (theta_minutes / 6))
        if (xminutes == xcenter):
            minutesnum = 30

    print('minutesnum=', minutesnum)

    #------------------------------------------------------------------------
    #Shows image were the detected clock hands is detected.
    #Green symbolise the hour hand.
    #Blue symbolise the minute hand.
    #------------------------------------------------------------------------
    cv2.imshow('Clock hands detected location', crop)

    #------------------------------------------------------------------------
    # Start to register the tkinter and gives it a title
    #------------------------------------------------------------------------
    digital_clock = tk.Tk()
    digital_clock.title("Digital Clock")

    #------------------------------------------------------------------------
    # This if loop prints the digital clock correctly
    #------------------------------------------------------------------------
    if (minutesnum < 10):
        time = f"{hournum}:0{minutesnum}"
    else:
        time = f"{hournum}:{minutesnum}"

    #------------------------------------------------------------------------
    # Sets up the tkinter window
    #------------------------------------------------------------------------
    label = tk.Label(digital_clock, text=time, font=('calibri', 150, 'bold'), background='black', foreground='white')
    label.pack(anchor='center')

    #------------------------------------------------------------------------
    #Creates a button to run the program anew
    #------------------------------------------------------------------------
    again_button = tk.Button(digital_clock, text="Run the program again", command=digital_clock.destroy)
    again_button.pack(side=tk.LEFT, padx=10)

    #------------------------------------------------------------------------
    #Creates a button to exit the program
    #------------------------------------------------------------------------
    close_button = tk.Button(digital_clock, text="Close the program", command=start_exiting_loop)
    close_button.pack(side=tk.RIGHT, padx=10)

    #------------------------------------------------------------------------
    # Run the Tkinter "digital_clock" event loop
    #------------------------------------------------------------------------
    digital_clock.mainloop()
    #------------------------------------------------------------------------
    # Once the user clicks "Run the program again" or "Close the program",
    # the program will start anew
    #------------------------------------------------------------------------
    cv2.destroyAllWindows()
