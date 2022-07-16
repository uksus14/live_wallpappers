from datetime import datetime
from json import load
from ctypes import windll as wll
from PIL import Image, ImageDraw, ImageFont
from time import sleep
from math import sin, cos, pi
import win32api
from random import choice


class Location:
  layout = {}

  def __init__(self, element):
    self.element = element

  def get(self, path=None):
    if not path: path = self.element
    try:
      with open(f"{dir_path}/additional/layout.json", "r") as f: add = load(f)
      with open(f"{dir_path}/additional/screen.json", "r") as f: add.update(load(f))
      Location.layout = add
    except: pass
    return Location.layout[path]

class Label:
  def __init__(self, text, title):
    self.texts = [text]
    self.text = text
    if type(text) == type([]):
      self.texts = text
      self.text = text[0]
    self.title = title
    self.is_visible = True
    self.buffer = datetime.timestamp(datetime.now())

  def update(self): pass

  def get(self):
    button = win32api.GetKeyState(0x04)
    if button >= 0:
      return self.text
    if self.buffer < datetime.timestamp(datetime.now())-0.5:
      one = self.texts
      if len(self.texts)-1: one = [text for text in one if text != self.text]
      self.text = choice(one)
    self.buffer = datetime.timestamp(datetime.now())
    return self.text

  def get_loc(self, path = None): return Location(self.title).get(path)

class WeekDay(Label):
  title = "Week day"
  WEEKDAYS = (" Monday", " Tuesday", " Wednesday", " Thursday", " Friday", " Saturday", " Sunday")

  def __init__(self):
    self.text=self.get()
    super().__init__(self.text, __class__.title)

  def update(self):
    self.text = self.get()

  def get(self):
    return WeekDay.WEEKDAYS[datetime.now().weekday()]

class Date(Label):
  title = "Date"
  def __init__(self):
    self.text=self.get()
    super().__init__(self.text, __class__.title)

  def update(self):
    self.text = self.get()

  def get(self):
    return datetime.now().strftime("%Y %d'th \nof %B ")

class Time(Label):
  title = "Time"
  def __init__(self):
    self.text=self.get()
    super().__init__(self.text, __class__.title)

  def update(self):
    self.text = self.get()

  def get(self):
    time_formating = "%H:%M"
    if self.get_loc("show_seconds"): time_formating += ":%S"
    return datetime.now().strftime(time_formating.center(8+len(time_formating)%2))

class Drawer:
  def __init__(self, bg_color, font, LDM, FPS_mode, hitbox_mode, std_color, elements):
    self.height = wll.user32.GetSystemMetrics(1)
    self.width  = wll.user32.GetSystemMetrics(0)
    self.bg_color = bg_color
    self.font = font
    self.elements = elements
    self.hitbox_mode = hitbox_mode
    self.LDM = LDM
    self.std_color = std_color
    self.FPS_mode = FPS_mode
    self.canvas = Image.new("RGB", (self.width, self.height), self.bg_color)
    sleep(0.1)
    self.canvas.save(f"{dir_path}/additional/wallpaper.png", "PNG")
    self.update([element.title for element in elements])

  def get_font(self, font_size, font = None):
    if font: font_name = font
    else: font_name = Main.legit_fonts[0]
    return ImageFont.truetype(f"{dir_path}/additional/{font_name}.ttf", size=int(font_size), encoding="utf-8")

  def write(self, x, y, text, color, offset, size, point):
    lines = text.split("\n")
    if   point[0] == "bottom": y -= size*len(lines)
    elif point[0] == "middle": y -= size*len(lines)/2
    for line in lines:
      sx = x
      if   point[1] == "middle": sx -= len(line)*offset/2
      elif point[1] == "right":  sx -= len(line)*offset
      for i, char in enumerate(line):
        self.draw.text((sx+offset*i, y), char, color, self.get_font(size))
      y += size

  def update(self, to_update, is_ending=False):
    self.draw_list = []
    if not self.FPS_mode:
      self.canvas = Image.new("RGB", (self.width, self.height), self.bg_color)
    self.draw = ImageDraw.Draw(self.canvas)
    for element in self.elements:
      if element.title not in to_update and self.FPS_mode: continue
      if not element.is_visible: continue

      text = element.text
      el_data = element.get_loc()
      color = self.std_color

      if element.title in glowing_gang:
        now = datetime.now()
        spin = (now.second + now.microsecond/1000000)*pi/60
        color = (127, abs(int(255*sin(spin))), abs(int(255*cos(spin))))
      if element.title in ["Icon border"]:
        for xy1, xy2 in el_data[0]:
          grid, trans = el_data[1][0], el_data[1][1]
          x_trans, y_trans = trans
          x1, y1 = xy1
          x2, y2 = xy2
          if x1 == grid[0]: x1+=1
          if x2 == grid[0]: x2+=1
          self.draw_list.append(("rect", (((x1*x_trans, y1*y_trans), (x2*x_trans, y2*y_trans)), color)))
        continue
      point = el_data["point"]
      x, y = [el_data["pos"][0]*self.width, el_data["pos"][1]*self.height]
      scale = el_data["scale"]
      offset = el_data["char_size"]*scale

      font_size = scale * self.font.size

      lines = text.split("\n")
      lline = len(max(lines, key=len))
      lines = len(lines)
      dx1, dy1 = x, y
      if   point[0] == "bottom": dy1 -= font_size*lines
      elif point[0] == "middle": dy1 -= font_size*lines/2
      dy2 = dy1 + font_size*lines

      if   point[1] == "middle": dx1 -= lline*offset/2
      elif point[1] == "right": dx1 -= lline*offset
      dx2 = dx1 + lline*offset
      if self.hitbox_mode:
        self.draw_list.append(("rect", (((dx1, dy1), (dx2, dy2)), (127, 127, 127))))
      self.write(x, y, text, tuple(color), offset, font_size, point)
    for sprite in self.draw_list:
      if sprite[0] == "rect":
        self.draw.rectangle(*sprite[1])
      elif sprite[0] == "text":
        self.write(*sprite[1])
    if is_ending: sleep(0.5)
    try:
      self.canvas.save(f"{dir_path}/additional/wallpaper.png", "PNG")
    except: pass
    wll.user32.SystemParametersInfoW(0x0014, 0, f"{dir_path}/additional/wallpaper.png", 2)


class Main(Drawer):
  legit_fonts = ["Rubik_Mono_One"]

  def __init__(self, elements):
    with open(f"{dir_path}/additional/layout.json") as f: main_data = load(f)
    font = main_data["font"]
    self.bg_color = tuple(main_data["bg_color"])
    self.delay_mode = main_data["delay_mode"]
    self.font_size = main_data["font_size"]
    self.low_detal_mode = main_data["low_detal_mode"]
    self.debug_mode = main_data["debug_mode"]
    self.hitbox_mode = main_data["hitbox_mode"]
    self.main_color = tuple(main_data["main_color"])
    self.always_update = main_data["always_update"]

    self.mBuffer = wll.user32.GetKeyState(4)
    self.elements = elements
    if font == "default":
      self.font = ImageFont.truetype(f"{dir_path}/additional/{Main.legit_fonts[0]}.ttf", size=self.font_size, encoding="utf-8")
    else:
      self.font = ImageFont.truetype(f"{dir_path}/additional/{font}.ttf", size=self.font_size, encoding="utf-8")

    super().__init__(self.bg_color, self.font, self.low_detal_mode, not self.debug_mode, self.hitbox_mode, self.main_color, elements)

  def start(self):
    to_update = []
    while True:
      if self.delay_mode:
        delay = 60-datetime.now().second
        sleep(delay)
      for element in self.elements:
        if element.get() != element.text:
          to_update.append(element.title)
          element.update()
      sleep(0.05)
      self.update(self.always_update + to_update)
      to_update.clear()

if __name__ == "__main__":
  glowing_gang =  ["Motivation", "Icon border"]
  dir_path = __file__.rpartition("\\")[0].replace("\\", "/")
  while_labels = [Label(["Stay Calm\n& Be Cool", "Stay Turned", "Make It Happen", "Good Vibes Only", "Stop Saying\n\"Tomorrow\"", "Get'em all", "You Can\n&\nYou Will"], "Motivation")]
  main = Main([*while_labels, Date(), Time(), WeekDay(), Label("|\n|", "Border"), Label(None, "Icon border")])
  # main = Main([*while_labels])
  print("Enjoy your new wallpapers\nGood luck!")
  print(main.start())
  end_labels = [Label("The end of Time", "Motivation")]
  main.elements = end_labels + main.elements[len(while_labels):]
  main.update([el.title for el in main.elements], True)