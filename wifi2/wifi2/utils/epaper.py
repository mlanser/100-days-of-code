#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
imgdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import epd2in7b
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("ML ePaper Test")
    epd = epd2in7b.EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    #time.sleep(1)
    
    logging.info("Define fonts")
    font24 = ImageFont.truetype(os.path.join(fontdir, 'Ubuntu-Regular.ttf'), 24)
    font18 = ImageFont.truetype(os.path.join(fontdir, 'Ubuntu-Bold.ttf'), 18)
    
    # Drawing on the image
    #logging.info("Drawing")
    #blackimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    #redimage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    
    

    # Drawing on the Horizontal image
    #logging.info("1.Drawing on the Horizontal image...")
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    HRedimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126    

    HBlackimage.paste(Image.open(os.path.join(imgdir, '2in7b-b.bmp')), (5,5))
    #HRedimage.paste(Image.open(os.path.join(imgdir, 'learning-logo.png')), (5,5))

    drawblack = ImageDraw.Draw(HBlackimage)
    drawred = ImageDraw.Draw(HRedimage)
    drawblack.text((5, 0), 'Hello world! :-)', font = font24, fill = 0)
    drawred.text((5, 26), '2.7inch e-Paper demo', font = font18, fill = 0)
    drawblack.line((20, 50, 70, 100), fill = 0)
    drawblack.line((70, 50, 20, 100), fill = 0)
    drawblack.rectangle((20, 50, 70, 100), outline = 0)
    drawred.line((165, 50, 165, 100), fill = 0)
    drawred.line((140, 75, 190, 75), fill = 0)
    drawred.arc((140, 50, 190, 100), 0, 360, fill = 0)
    drawred.rectangle((80, 50, 130, 100), fill = 0)
    drawred.chord((200, 50, 250, 100), 0, 360, fill = 0)
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
    time.sleep(2)
    
    # Drawing on the Vertical image
    #logging.info("2.Drawing on the Vertical image...")
    #LBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
    #LRedimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
    #drawblack = ImageDraw.Draw(LBlackimage)
    #drawred = ImageDraw.Draw(LRedimage)
    
    #drawblack.text((2, 0), 'hello world', font = font18, fill = 0)
    #drawblack.text((2, 20), '2.9inch epd', font = font18, fill = 0)
    #drawblack.text((20, 50), u'微雪电子', font = font18, fill = 0)
    #drawblack.line((10, 90, 60, 140), fill = 0)
    #drawblack.line((60, 90, 10, 140), fill = 0)
    #drawblack.rectangle((10, 90, 60, 140), outline = 0)
    #drawred.line((95, 90, 95, 140), fill = 0)
    #drawred.line((70, 115, 120, 115), fill = 0)
    #drawred.arc((70, 90, 120, 140), 0, 360, fill = 0)
    #drawred.rectangle((10, 150, 60, 200), fill = 0)
    #drawred.chord((70, 150, 120, 200), 0, 360, fill = 0)
    #epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRedimage))
    #time.sleep(2)
    
    #logging.info("3.read bmp file")
    #HBlackimage = Image.open(os.path.join(imgdir, '2in7b-b.bmp'))
    #HRedimage = Image.open(os.path.join(imgdir, '2in7b-r.bmp'))
    #epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
    #time.sleep(2)
    
    #logging.info("4.read bmp file on window")
    #blackimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    #redimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126    
    #newimage = Image.open(os.path.join(imgdir, '100x100.bmp'))
    #blackimage1.paste(newimage, (50,10))    
    #epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))
    
    #logging.info("Clear...")
    #epd.init()
    #epd.Clear()
    
    #logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in7b.epdconfig.module_exit()
    exit()


    
    
    
    
    
    
    
    
    
#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
imgdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import epd2in7b
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("ML ePaper Test")
    epd = epd2in7b.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    # Drawing on the Horizontal image
    logging.info("Drawing on the then screen ...")
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    HRedimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
    time.sleep(2)

    #logging.info("Clear...")
    epd.init()
    epd.Clear()

    #logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in7b.epdconfig.module_exit()
    exit()

    