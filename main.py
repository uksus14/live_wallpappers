import os, winshell
from win32com.client import Dispatch
wdir = __file__.rpartition("\\")[0]

from math import hypot
from PIL import Image, ImageDraw
size = 600
r = 150
glow_level = 1.2

im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(im)

for y in range(size):
  for x in range(size):
    dx, dy = x-size/2, y-size/2
    pr = hypot(dx, dy)
    draw.point((x, y), (255, 255, 255, int(255-abs(pr-r)**glow_level)))

ico_path = os.path.join(wdir, "additional\\Bordler.ico")

im.save(ico_path, "ICO")

desktop = winshell.desktop()
path = os.path.join(desktop, "Bordler.lnk")


shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(path)
shortcut.Targetpath = os.path.join(wdir, "bordler.pyw")
shortcut.WorkingDirectory = wdir
shortcut.IconLocation = ico_path
shortcut.save()