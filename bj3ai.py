from PIL import Image, ImageGrab, ImageOps
import time, autopy, sys
#366,141,381,160
im_path = 'start.png'
im_lightning_path = 'start_lightning_2.png'
im_snow_path = 'start_snow.png'
str_pos = ()
keep = []
x_pad,y_pad = 82,82

def mouse_move(x,y):
    autopy.mouse.move(x,y)

def mouse_click(x,y):
    mouse_move(x,y)
    autopy.mouse.click()

def find_start_location():
    global im_path, im_lightning_path, im_snow_path
    path = im_path
    img_start = autopy.bitmap.Bitmap.open(im_path)
    pos = None
    while pos == None:
        pos = autopy.bitmap.capture_screen().find_bitmap(img_start)
        if pos != None and path == im_path:
            mouse_click(pos[0],pos[1])
            return (pos[0] + 252 , pos[1] - 439, pos[0] + 262,  pos[1] - 423)
        elif pos != None and path == im_snow_path:
            mouse_click(pos[0],pos[1])
            return (pos[0] + 109 , pos[1] - 398, pos[0] + 129,  pos[1] - 375)
        elif pos != None and path == im_lightning_path:
            mouse_click(pos[0],pos[1])
            return (pos[0] + 84 , pos[1] + 111, pos[0] + 124,  pos[1] + 133)

        if path == im_path:
            path = im_snow_path
            img_start = autopy.bitmap.Bitmap.open(path)
        elif path == im_snow_path:
            path = im_lightning_path
            img_start = autopy.bitmap.Bitmap.open(path)
        elif path == im_lightning_path:
            path = im_path
            img_start = autopy.bitmap.Bitmap.open(path)

def identify_gem(img_gem,row=0,col=0):
    global rmin,gmin,bmin,rmax,gmax,bmax
    img_8bit = img_gem.convert('P', palette=Image.ADAPTIVE, colors=1)
    img_8bit.putalpha(0)
    c = img_8bit.getcolors(256)
    r,g,b = c[0][1][0], c[0][1][1], c[0][1][2]
    gem = None

    # Red, Green, Blue, Orange and Purple arenot be identified exactly by me
    if r >= 160 and r <= 255 and g >= 7 and g  <= 105 and b >= 1 and b <= 99:
        gem = 'R'
    if r >= 240 and r <= 255 and g >= 128 and g  <= 155 and b >= 170 and b <= 200:
        gem = 'R' #RL
    if r >= 1 and r <= 193 and g >= 129 and g  <= 255 and b >= 1 and b <= 210:
        gem = 'G'
    if abs(r-g) >= 90 and abs(r-g) <= 120 and g >= 180 and abs(b-g) >= 90:
        gem = 'G' #GL
    if r >= 90 and r <= 130 and  g >= 220 and g <= 250 and b >= 240:
        gem = 'B' #'BL'
    if r < 190 and abs(r-g) >= 30 and (g >= 120  and g <= 250) and (abs(g-b) >= 30 and abs(g-b) <= 90):
        gem = 'B'
    if abs(r-b) >= 90 and abs(b-g) >= 50 and b >= 145:
        gem = 'B'
    if r >= 170 and (g >= 84 and g <= 160) and (b >= 10 and b <= 100):
        gem = 'O'
    if r  >= 240 and r  <= 255  and g >= 170 and g <= 200 and b >= 150 and b <= 190:
        gem = 'O' #OL
    if (abs(r-b) >= 0 and abs(r-b) <= 30) and g <= 150:
        gem = 'P'
    if  r > 200 and g < 100 and b > 200:
        gem = 'P' #PF
    if r >= 250 and g >= 7 and g >= 160 and g  <= 180 and b >= 250:
        gem = 'P' #PL

    # Yellow and White are unique identify
    if r >= 150 and (g >= 150 and  g <= 236)and (b >= 9 and b <= 170):
        gem = 'Y'
    elif r >= 220 and r < 255 and g >= 170 and b <= 170:
        gem = 'Y' #YL
    elif (r-g) <= 40 and abs(r-b) <= 40 and abs(g-b) <= 40:
        gem = 'W'
    elif (r == g and r == b and g == b):
        gem = 'W'

    if (r <= 100) and (g <= 100) and (b <= 100):
        gem = "C"

    return gem

def click_close_play():
    play_btn = autopy.bitmap.Bitmap.open('play2.png')
    location = autopy.bitmap.capture_screen(((0,0),(1366,768))).find_bitmap(play_btn)
    if location != None:
        mouse_click(location[0],location[1])
        autopy.mouse.click()

    close_btn = autopy.bitmap.Bitmap.open('close3.png')
    location = autopy.bitmap.capture_screen(((0,0),(1366,768))).find_bitmap(close_btn)
    if location != None:
        mouse_click(location[0],location[1])
        autopy.mouse.click()

def build_board():
    global str_pos,keep, cnt
    img = ImageGrab.grab()
    keep = []
    print ''
    x1_start,y1_start = str_pos[0],str_pos[1]
    x2_start,y2_start = str_pos[2],str_pos[3]
    for row in xrange(8):
        x1 = x1_start
        x2 = x2_start
        print row+1,
        if row == 0:
            y1 = y1_start
            y2 = y2_start
        else:
            y1+=y_pad
            y2+=y_pad
        for col in xrange(8):
            box = (x1,y1,x2,y2)
            img_gem = img.crop(box)
            color = identify_gem(img_gem,row,col)
            if color == None:
                color = 'N'

            print "%2s" % (color),
            keep.append([color,x1,y1])
            x1 += x_pad
            x2 += x_pad
        print ''

def find_move():
    global valid_move
    valid_move = []
    for row in xrange(8):
        for col in xrange(8):
            current_col = 8*row+col
            mouse_x1 = keep[current_col][1]
            mouse_y1 = keep[current_col][2]
            mouse_x2 = 100
            mouse_y2 = 150
            if (current_col > 7 and current_col < 56 and not(current_col in [8,16,24,32,40,48,56]) and
                keep[current_col-8][0] == keep[current_col-1][0] == keep[current_col+8][0] and
                keep[current_col-8][0] != "N" and keep[current_col-1][0] != "N" and keep[current_col+8][0] != "N"): # top blank left bot
                print "top blank left bot",
                print current_col, keep[current_col-8][0], keep[current_col][0], keep[current_col-1][0], keep[current_col+8][0]
                mouse_x2 = keep[current_col-1][1]
                mouse_y2 = keep[current_col-1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 7 and current_col < 56 and not(current_col in [15,23,31,39,47,55]) and
                keep[current_col-8][0] == keep[current_col+1][0] == keep[current_col+8][0] and
                keep[current_col-8][0] != "N" and keep[current_col+1][0] != "N" and keep[current_col+8][0] != "N"): # top blank right bot
                print "top blank right bot IN",
                print current_col, keep[current_col-8][0], keep[current_col][0], keep[current_col+1][0], keep[current_col+8][0]
                mouse_x2 = keep[current_col+1][1]
                mouse_y2 = keep[current_col+1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col < 56 and not(current_col in [6,7,14,15,22,23,30,31,38,39,46,47,54,55]) and
                keep[current_col+2][0] == keep[current_col+1][0] == keep[current_col+8][0] and
                keep[current_col+2][0] != "N" and keep[current_col-1][0] != "N" and keep[current_col+8][0] != "N"): # blank right right bot
                print "blank right right bot ",
                print current_col, keep[current_col][0], keep[current_col+1][0], keep[current_col+2][0], keep[current_col+8][0]
                mouse_x2 = keep[current_col+8][1]
                mouse_y2 = keep[current_col+8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 7 and not((current_col) in [14,15,22,23,30,31,38,39,46,47,54,55,62,63]) and
                keep[current_col+2][0] == keep[current_col+1][0] == keep[current_col-8][0] and
                keep[current_col+2][0] != "N" and keep[current_col+1][0] != "N" and keep[current_col-8][0] != "N"): # blank right right top
                print "blank right right top ",
                print current_col, keep[current_col][0], keep[current_col+1][0], keep[current_col+2][0], keep[current_col-8][0]
                mouse_x2 = keep[current_col-8][1]
                mouse_y2 = keep[current_col-8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col < 56 and not(current_col in [0,1,8,9,16,17,24,25,32,33,40,41,48,49]) and
                keep[current_col-2][0] == keep[current_col-1][0] == keep[current_col+8][0] and
                keep[current_col-2][0] != "N" and keep[current_col-1][0] != "N" and keep[current_col+8][0] != "N"): # left left blank bot
                print "left left blank bot ",
                print current_col, keep[current_col-2][0], keep[current_col-1][0], keep[current_col][0], keep[current_col+8][0]
                mouse_x2 = keep[current_col+8][1]
                mouse_y2 = keep[current_col+8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 7 and not((current_col) in [0,1,8,9,16,17,24,25,32,33,40,41,48,49]) and
                keep[current_col-2][0] == keep[current_col-1][0] == keep[current_col-8][0] and
                keep[current_col-2][0] != "N" and keep[current_col-1][0] != "N" and keep[current_col-8][0] != "N"): # left left blank top
                print "left left blank top ",
                print current_col, keep[current_col-2][0], keep[current_col-1][0], keep[current_col][0], keep[current_col-8][0]
                mouse_x2 = keep[current_col-8][1]
                mouse_y2 = keep[current_col-8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (not(current_col in [0,1,8,9,16,17,24,25,32,33,40,41,48,49,56,57,7,15,23,31,39,47,63]) and
                keep[current_col-2][0] == keep[current_col-1][0] == keep[current_col+1][0] and
                keep[current_col-2][0] != "N" and keep[current_col-1][0] != "N" and keep[current_col+1][0] != "N"): # left left blank right
                print "left left blank right ",
                print current_col, keep[current_col-2][0], keep[current_col-1][0], keep[current_col][0], keep[current_col+1][0]
                mouse_x2 = keep[current_col+1][1]
                mouse_y2 = keep[current_col+1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (not(current_col in [0,8,16,24,32,40,48,56,6,7,14,15,22,23,30,31,38,39,46,47,54,55,62,63]) and
                keep[current_col-1][0] == keep[current_col+1][0] == keep[current_col+2][0] and
                keep[current_col-1][0] != "N" and keep[current_col+1][0] != "N" and keep[current_col+2][0] != "N"): # left blank right right
                print "left blank right right ",
                print current_col, keep[current_col-1][0], keep[current_col][0], keep[current_col+1][0], keep[current_col+1][0]
                mouse_x2 = keep[current_col-1][1]
                mouse_y2 = keep[current_col-1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col < 56 and not((current_col) in [0,8,16,24,32,40,48,56,7,15,23,31,39,47,55]) and
                keep[current_col-1][0] == keep[current_col+1][0] == keep[current_col+8][0] and
                keep[current_col-1][0] != "N" and keep[current_col+1][0] != "N" and keep[current_col+8][0] != "N"): # left blank right bot
                print "left blank right bot ",
                print current_col, keep[current_col-1][0], keep[current_col][0], keep[current_col+1][0], keep[current_col+8][0]
                mouse_x2 = keep[current_col+8][1]
                mouse_y2 = keep[current_col+8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 7 and not((current_col) in [8,16,24,32,40,48,56,15,23,31,39,47,55,63]) and
                keep[current_col-1][0] == keep[current_col+1][0] == keep[current_col-8][0] and
                keep[current_col-1][0] != "N" and keep[current_col+1][0] != "N" and keep[current_col-8][0] != "N"): # left blank right top
                print "left blank right top ",
                print current_col, keep[current_col-1][0], keep[current_col][0], keep[current_col+1][0], keep[current_col-8][0]
                mouse_x2 = keep[current_col-8][1]
                mouse_y2 = keep[current_col-8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col < 48 and not(current_col in [0,8,16,15,24,23,32,31,40]) and
                keep[current_col-1][0] == keep[current_col+8][0] == keep[current_col+16][0] and
                keep[current_col-1][0] != "N" and keep[current_col+8][0] != "N" and keep[current_col+16][0] != "N"): # blank left bot bot
                print "blank left bot bot ",
                print current_col+1, keep[current_col][0], keep[current_col-1][0], keep[current_col+8][0], keep[current_col+16][0]
                mouse_x2 = keep[current_col-1][1]
                mouse_y2 = keep[current_col-1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col < 48 and not(current_col in [7,15,23,31,39,47]) and
                keep[current_col+1][0] == keep[current_col+8][0] == keep[current_col+16][0] and
                keep[current_col+1][0] != "N" and keep[current_col+8][0] != "N" and keep[current_col+16][0] != "N"): # blank right bot bot
                print "blank right bot bot ",
                print current_col+1, keep[current_col][0], keep[current_col+1][0], keep[current_col+8][0], keep[current_col+16][0]
                mouse_x2 = keep[current_col+1][1]
                mouse_y2 = keep[current_col+1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 15 and not(current_col in [16,24,32,40,48,56]) and
                keep[current_col-1][0] == keep[current_col-8][0] == keep[current_col-16][0] and
                keep[current_col-1][0] != "N" and keep[current_col-8][0] != "N" and keep[current_col-16][0] != "N"): # top top blank left
                print "top top blank left ",
                print current_col+1, keep[current_col-8][0], keep[current_col-16][0], keep[current_col][0], keep[current_col-1][0]
                mouse_x2 = keep[current_col-1][1]
                mouse_y2 = keep[current_col-1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 7 and current_col < 40 and
                keep[current_col-8][0] == keep[current_col+8][0] == keep[current_col+16][0] and
                keep[current_col-8][0] != "N" and keep[current_col+8][0] != "N" and keep[current_col+16][0] != "N"): # top blank bot bot
                print "top blank bot bot "
                print current_col+1, keep[current_col-8][0], keep[current_col][0], keep[current_col+8][0], keep[current_col+16][0]
                mouse_x2 = keep[current_col-8][1]
                mouse_y2 = keep[current_col-8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 15 and not(current_col in [7,15,23,31,39,47,55,63]) and
                keep[current_col+1][0] == keep[current_col-8][0] == keep[current_col-16][0] and
                keep[current_col+1][0] != "N" and keep[current_col-8][0] != "N" and keep[current_col-16][0] != "N"): # top top blank right
                print "top top blank right ",
                print current_col+1, keep[current_col-8][0], keep[current_col-16][0], keep[current_col][0], keep[current_col+1][0]
                mouse_x2 = keep[current_col+1][1]
                mouse_y2 = keep[current_col+1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 15 and current_col < 56 and
                keep[current_col-16][0] == keep[current_col-8][0] == keep[current_col+8][0] and
                keep[current_col-16][0] != "N" and keep[current_col+8][0] != "N" and keep[current_col-8][0] != "N"): # top top blank bot
                print "top top blank bot "
                print current_col+1, keep[current_col-16][0], keep[current_col-8][0], keep[current_col][0], keep[current_col+8][0]
                mouse_x2 = keep[current_col+8][1]
                mouse_y2 = keep[current_col+8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col > 7 and current_col < 48 and
                keep[current_col+16][0] == keep[current_col+8][0] == keep[current_col-8][0] and
                keep[current_col+16][0] != "N" and keep[current_col+8][0] != "N" and keep[current_col-8][0] != "N"): # bot bot blank top
                print "bot bot blank top "
                print current_col+1, keep[current_col+16][0], keep[current_col+8][0], keep[current_col][0], keep[current_col-8][0]
                mouse_x2 = keep[current_col-8][1]
                mouse_y2 = keep[current_col-8][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col < 48 and not(current_col in [7,15,23,31,39,47,55,63]) and
                keep[current_col+1][0] == keep[current_col+8][0] == keep[current_col+16][0] and
                keep[current_col+1][0] != "N" and keep[current_col+8][0] != "N" and keep[current_col+16][0] != "N"): # right blank bot bot
                print "right blank bot bot "
                print current_col+1, keep[current_col+1][0], keep[current_col][0], keep[current_col+8][0], keep[current_col+16][0]
                mouse_x2 = keep[current_col+1][1]
                mouse_y2 = keep[current_col+1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (current_col < 48 and not(current_col in [0,8,16,24,32,40]) and
                keep[current_col-1][0] == keep[current_col+8][0] == keep[current_col+16][0] and
                keep[current_col-1][0] != "N" and keep[current_col+8][0] != "N" and keep[current_col+16][0] != "N"): # left blank bot bot
                print "left blank bot bot "
                print current_col+1, keep[current_col-1][0], keep[current_col][0], keep[current_col+8][0], keep[current_col+16][0]
                mouse_x2 = keep[current_col-1][1]
                mouse_y2 = keep[current_col-1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (keep[current_col][0] == "C" and not(current_col in [0,8,16,24,32,40,48,56]) ):
                print "left cube "
                print current_col+1, keep[current_col][0], keep[current_col-1][0]
                mouse_x2 = keep[current_col-1][1]
                mouse_y2 = keep[current_col-1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

            if (keep[current_col][0] == "C" and not(current_col in [7,15,23,31,39,47,55,63]) ):
                print "cube right "
                print current_col+1, keep[current_col][0], keep[current_col+1][0]
                mouse_x2 = keep[current_col+1][1]
                mouse_y2 = keep[current_col+1][2]
                swap(mouse_x1,mouse_y1,mouse_x2,mouse_y2)

def swap(x1,y1,x2,y2):
    mouse_click(x1, y1)
    mouse_click(x2, y2)
    time.sleep(0.001)
    build_board()

def run(minutes=1):
    try:
        t_end = time.time() + 60 * minutes
        while time.time() < t_end:
            build_board()
            find_move()
            click_close_play()
    except (KeyboardInterrupt, SystemExit):
        print '\n! Received keyboard interrupt, quitting app.\n'
        exit()

def main(args):
    global str_pos
    click_close_play()
    str_pos = find_start_location()
    if len(args) > 1:
        run(int(args[1]))
    else:
        run()

if __name__ == '__main__':
    main(sys.argv)
