import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import urllib.request
import json as _json
from typing import List
import time
from datetime import datetime
import logging

# configure logging
os.system("color")
logging.basicConfig(level=logging.INFO, encoding='utf-8', format="[%(asctime)s] [%(levelname)s] %(message)s")
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.addLevelName(logging.DEBUG, "\033[30;20mDBG\033[0m")
logging.addLevelName(logging.INFO, "\033[32;20mINF\033[0m")
logging.addLevelName(logging.WARNING, "\033[33;20mWRN\033[0m")
logging.addLevelName(logging.ERROR, "\033[31;20mERR\033[0m")

# In case you want the low temp screen as well, just uncomment the line below and adjust the screens list above.
# screens = ["temp_high", "temp_low", "power", "flow"]
screens = ["temp_high", "power", "flow"]

try:
    fFixed = ImageFont.truetype("fonts/MatrixLight6.ttf", 6)
    fAwesome = ImageFont.truetype("fonts/Awesome.ttf", 16)
    fm = ImageFont.truetype("fonts/Roboto_Condensed-Medium.ttf", 28)
    fu = ImageFont.truetype("fonts/Roboto_Condensed-Light.ttf", 18)
except:
    logging.error("Error loading fonts. Make sure the .ttf files are in the '.\\fonts' directory relative to this script.")
    sys.exit(1)

def read_aqs_export():
    # You need to configure AQS to export the desired data to 
    # the windows temp directory first.
    try:
        with open('c:\\windows\\temp\\AquaSuiteExport.json') as json_data:
            d = json.load(json_data)
            return d
    except:
        logging.error("Error loading AquaSuite software export. Make sure the file 'AquaSuiteExport.json' is in the 'c:\\windows\\temp' directory.")
        return False

def create_image(percentages, temp_l, temp_h, power, flow, screen=screens[0]):
    height = 40
    width  = 128
    bar_width = 4
    spacing = 3

    img = Image.new('RGB', (width, height), color='black') # White background
    draw = ImageDraw.Draw(img)

    
    # Draw FAN BARGRAPHS
    # Calculate total width needed for bars and spacing
    num_bars = len(percentages)
    total_bar_area_width = num_bars * bar_width + (num_bars - 1) * spacing
    
    # Start X position to center bars on the right side (adjust as needed for padding)
    # Let's put some padding from the right edge, e.g., 5px
    right_padding = 0
    start_x = width - right_padding - total_bar_area_width

    vbar_max_height = 18
    vbar_offset_top = 20
    for i, percentage in enumerate(percentages):
        # Calculate bar height based on percentage (0-100)
        #percentage = {"value":15, "name":"X"}
        vbar_height = int((percentage.get("value", 0) / 100.0) * (vbar_max_height))
        
        # Calculate bar coordinates (x1, y1, x2, y2)
        # y1 is the top, y2 is the bottom (from bottom up)
        x1 = start_x + i * (bar_width + spacing) - 3
        y1 = vbar_max_height - vbar_height + vbar_offset_top # Draw from bottom up
        x2 = x1 + bar_width
        y2 = vbar_max_height + vbar_offset_top # Full height at bottom

        # Draw the bar (filled rectangle)
        draw.rectangle([x1, 19, x2, height-1], outline="white") # Blue filling
        draw.rectangle([x1+1, y1, x2-1, y2], fill='gray') # Blue filling
        draw.text((x1+1, 13), percentage.get("name", "X"), (255,255,255), font=fFixed)

    # Draw COOLEANT  and FAN header
    draw.rectangle([0, -1, 96, 10], fill="white")
    draw.text((2, -2), "CIRCULATION", (0,0,0), font=fAwesome)
    draw.rectangle([97, -1, 127, 10], outline="white")
    draw.text((99, -2), "FANS", (255,255,255), font=fAwesome)
    try:
        power = float(power)
    except:
        power = -1
    try:
        temp_h = float(temp_h)
    except:
        temp_h = -1
    try:
        temp_l = float(temp_l)
    except:
        temp_l = -1
    try:
        flow = float(flow)
    except:
        flow = -1

    # Draw COOLEANT Numbers
    if screen == "temp_high":
        try:
            draw.text((28, 10), "{:2.1f}".format(temp_h).replace(".", ","), (255,255,255), font=fm)
            draw.text((76, 12), "°", (255,255,255), font=fu)
            draw.text((83, 12), "C", (255,255,255), font=fu)
        except:
            draw.text((28, 10), "N/A", (255,255,255), font=fm)
        img2 = Image.open('icons/cooleant_high.png', 'r')
        img.paste(img2, (0,15))
    if screen == "temp_low":
        try:
            draw.text((28, 10), "{:2.1f}".format(temp_l).replace(".", ","), (255,255,255), font=fm)
            draw.text((76, 12), "°", (255,255,255), font=fu)
            draw.text((83, 12), "C", (255,255,255), font=fu)
        except:
            draw.text((28, 10), "N/A", (255,255,255), font=fm)    
        img2 = Image.open('icons/cooleant_low.png', 'r')
        img.paste(img2, (0,15))
    if screen == "power":
        try:
            draw.text((34, 10), "{:3.0f}".format(power).replace(".", ","), (255,255,255), font=fm)
            draw.text((77, 12), "W", (255,255,255), font=fu)
        except:
            draw.text((34, 10), "N/A", (255,255,255), font=fm)
        img2 = Image.open('icons/power.png', 'r')
        img.paste(img2, (0,15))
    if screen == "flow":
        try:
            draw.text((34, 10), "{:3.0f}".format(flow).replace(".", ","), (255,255,255), font=fm)
            draw.text((76, 13), "l", (255,255,255), font=fu)
            draw.text((79, 19), "/", (255,255,255), font=fu)
            draw.text((85, 24), "h", (255,255,255), font=fu)
        except:
            draw.text((34, 10), "N/A", (255,255,255), font=fm)
        img2 = Image.open('icons/flow.png', 'r')
        img.paste(img2, (0,15))

    if sys.argv[1:] and sys.argv[1] == "--save-output":
        img.save("output.png")
    return img


def find_steelseries_endpoint():
    """Try to find SteelSeries Engine HTTP endpoint from known coreProps locations.

    Returns base URL like 'http://127.0.0.1:41069' or None.
    """
    try:
        text = ""
        with open("C:\\ProgramData\\SteelSeries\\SteelSeries Engine 3\\coreProps.json", 'r', encoding='utf-8') as f:
            text = f.read()
        js = json.loads(text)
        url = js.get('address')
    except Exception:
        logging.error("Could not determine SteelSeries endpoint from file 'c:\\ProgramData\\SteelSeries\\SteelSeries Engine 3\\coreProps.json'.")
        return None
    logging.info("Found SteelSeries endpoint: %s", url)
    return "http://" + url


def register_game_and_event(base_url, game='AQS2SSE', event='FULLSCREEN'):
    """Register a simple game and a fullscreen event that accepts image frames.

    This function attempts to follow the common GameSense JSON API patterns.
    It will silently continue on failures but prints responses for debugging.

    Registering the game and event is required once before sending any images.
    """
    headers = {'Content-Type': 'application/json', 'User-Agent': 'aqs2sse-uploader/1.0'}

    # 1) Register game metadata
    meta = {
        'game': game,
        'game_display_name': "AquaSuite-2-SteelSeries Engine",
        'developer': 'McSeven',
        "deinitialize_timer_length_ms": 10000
    }
    try:
        req = urllib.request.Request(base_url + '/game_metadata', data=_json.dumps(meta).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=3) as resp:
            logging.info("Registered game with following meta: %s", _json.dumps(meta).encode('utf-8'))
    except Exception as e:
        logging.error('Could not register game event. metadata request failed: %s', e)
        return False

    # 2) Bind the event to devices (simple bind payload)
    # Note: this is the variant for an 128x40 OLED screen as on the APEX Pro.
    bind = {
        'game': game,
        'event': event,
        'min_value': 0,
        'max_value': 100,
        "icon_id": 0,        
        'value_optional': True,
        'handlers': [
            {
                'device-type': 'screened-128x40',
                'zone': 'one',
                'mode': 'screen',
                'datas': [
                    {
                        "has_text": False,
                        "image-data": [0] * 640
                    }
                ]
            }
        ]
    }
    try:
        req = urllib.request.Request(base_url + '/bind_game_event', data=_json.dumps(bind).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=3) as resp:
            logging.debug('Registered an OLED screen event to the name \'FULLSCREEN\': %s %s', resp.status, resp.read().decode('utf-8', errors='ignore'))
            return True
    except Exception as e:
        logging.error('Could not register an event named \'FULLSCREEN\' with SteelSeries GG: %s', e)
        return False


def send_fullscreen_image_as_json(base_url, img, game='AQS2SSE', event='FULLSCREEN'):
    """Convert PIL image to base64 PNG and send as JSON payload to /game_event.

    The exact JSON schema for SteelSeries may vary; this function uses a common
    pattern and prints responses for debugging.

    The OLED is black/white only, therefore, all non-black pixels are treated as 'on' and
    are display white.
    """
    def image_to_128x40_byte_array(im: Image.Image) -> List[int]:
        # Ensure correct size and RGB
        im2 = im.convert('RGB').resize((128, 40), Image.NEAREST)
        bytes_out: List[int] = []
        for y in range(40):
            for xb in range(0, 128, 8):
                b = 0
                for bit in range(8):
                    x = xb + bit
                    r, g, bl = im2.getpixel((x, y))
                    # Simple decision if the pixel should be on or off
                    bit_val = 1 if (r != 0 or g != 0 or bl != 0) else 0
                    # MSB is leftmost pixel
                    b = (b << 1) | bit_val
                bytes_out.append(b)
        return bytes_out
    
    # Now, convert the PIL image into a number array with numbers between 0 and 255
    byte_array = image_to_128x40_byte_array(img)

    # Build payload without 'value' (value_optional handled by registration)
    payload = {
        'game': game,
        'event': event,
        'data': 
            {
                'frame': {
                    'image-data-128x40': byte_array
                }
            }
    }

    headers = {'Content-Type': 'application/json', 'User-Agent': 'aqs2sse-uploader/1.0'}
    try:
        req = urllib.request.Request(base_url + '/game_event', data=_json.dumps(payload).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            logging.debug('game_event: %s %s', resp.status, resp.read().decode('utf-8', errors='ignore'))
            return True
        
    except Exception as e:
        logging.error('game_event send failed: %s', e)
        return False

registered = False
screenindex = 0
if __name__ == "__main__":
    while True:
        time.sleep(1)
        # Integrate with SteelSeries GameSense if possible.
        if not registered:
            base = find_steelseries_endpoint()
            if not base:
                logging.warning('SteelSeries endpoint not found; not sending image to GameSense.')
                continue
            # Register and bind a fullscreen event, then send image as JSON
            if not register_game_and_event(base):
                logging.warning('Error registering game or event, continuing...')
                continue
            registered = True
            logging.info('Successfully registered game and event with SteelSeries GameSense. Starting to send screen data...')

        systemData = read_aqs_export()
        if not systemData:
            logging.warning('Error reading AQS export, continuing...')
            continue
        
        # mapping and extracting the data
        percentages = []
        temp_low = 0
        temp_high = 0
        power = 0
        flow = 0
        for value in systemData['Logdata']:
            if value.get("DataSourcePath") == 'quadro:1305159824:data\\temperatures\\3':
                temp_low = value.get("value", 0)
            if value.get("DataSourcePath") == 'highflow_next:1554543936:data\\temperature_water':
                temp_high = value.get("value", 0)
            if value.get("DataSourcePath") == 'quadro:1305159824:data\\fans\\0\\power':
                percentages.append({"name":value.get("name", "X")[0], "value":value.get("value", 0)})
            if value.get("DataSourcePath") == 'quadro:1305159824:data\\fans\\1\\power':
                percentages.append({"name":value.get("name", "X")[0], "value":value.get("value", 0)})
            if value.get("DataSourcePath") == 'quadro:1305159824:data\\fans\\2\\power':
                percentages.append({"name":value.get("name", "X")[0], "value":value.get("value", 0)})
            if value.get("DataSourcePath") == 'quadro:1305159824:data\\fans\\3\\power':
                percentages.append({"name":value.get("name", "X")[0], "value":value.get("value", 0)})
            if value.get("DataSourcePath") == 'service_data:1:data\\sensor\\virtualsensors/9886c2461fd34a72a8cf2636d840e500':
                power = value.get("value", 0)
            if value.get("DataSourcePath") == 'highflow_next:1554543936:data\\flow':
                flow = value.get("value", 0)

        screenindex = (screenindex + 1) % len(screens)
        systemdataimage = create_image(percentages, temp_low, temp_high, power, flow, screen=screens[screenindex])
        
        if not send_fullscreen_image_as_json(base, systemdataimage):
            logging.error('Failed to send fullscreen image to SteelSeries at %s', base)
            registered = False
            continue