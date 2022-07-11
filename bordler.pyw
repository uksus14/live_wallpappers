import os
from turtle import down
import pygame as pg
from json import dumps, load
path = __file__.rpartition("\\")[0]
mapp, deform, grid = 0, 0, 0
if not os.path.exists(f"{path}\\additional\\screen.json"):
  with open(f"{path}\\additional\\screen.json", "w+") as f: pass
else:
  with open(f"{path}\\additional\\screen.json", "r") as f:
    data = load(f)
    mapp = data["mapp"]
    grid, deform = data["Icon border"][1]

if not grid:
  grid = [25, 10]
if not mapp:
  mapp = [[0 for _ in range(grid[0])] for _ in range(grid[1])]
if not deform:
  deform = [38, 50.5]
else: deform = [deform[0]/2, deform[1]/2]

fps = 60
stu, ups = 0, 0
# stu = 0.5
ups = 8
if stu:
  fpu = fps*stu
else:
  fpu = fps/ups

pg.init()
window = pg.display.set_mode((grid[0]*deform[0], grid[1]*deform[1]))
pg.display.set_caption("Set engaged")
clock = pg.time.Clock()


window.fill((127, 127, 127))
run = True
click = [False, 1]
tick = 0

while run:
  if click[0]:
    x, y = pg.mouse.get_pos()
    x, y = int(x/deform[0]), int(y/deform[1])
    mapp[y][x] = click[1]
  clock.tick(fps)
  ev = pg.event.get()
  for event in ev:
    if event.type == pg.QUIT:
      pg.quit()
      run = False
    elif event.type == pg.MOUSEBUTTONDOWN:
      x, y = pg.mouse.get_pos()
      x, y = int(x/deform[0]), int(y/deform[1])
      click = [True, abs(mapp[y][x]-1)]
    elif event.type == pg.MOUSEBUTTONUP:
      click[0] = False
  if not run: break
  for y, row in enumerate(mapp):
    for x, cell in enumerate(row):
      pg.draw.rect(window, pg.Color((1-cell)*255, (1-cell)*255, (1-cell)*255), pg.Rect(x*deform[0]+1, y*deform[1]+1, deform[0]-1, deform[1]-1))
  pg.display.flip()
  tick += 1
  if tick <= fpu:
    continue
  tick %= fpu
  jcon = {"mapp": mapp, "Icon border": [[], [grid, [deform[0]*2, deform[1]*2]]]}
  corners = sum([sum([[(x, y), (x+1, y), (x, y+1), (x+1, y+1)] for x, cell in enumerate(row) if cell], []) for y, row in enumerate(mapp)], [])
  borders = []
  for corner in set(corners):
    if ((corner[0] and corner[1] and corners.count(corner) < 4) or (corner[0] ^ corner[1] and corners.count(corner) < 2)) and corner not in borders:
      borders.append(corner)
#   print(borders)
  poly = []
  for x, y in borders:
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
      cx, cy = min(x, x+dx), min(y, y+dy)
      normx = lambda x: max(min(x, grid[0]-1), 0)
      normy = lambda y: max(min(y, grid[1]-1), 0)
      down_border = mapp[normy(y)][normx(cx)]
      if y == grid[1]: down_border = False
      if (x+dx, y+dy) in borders and ((dx and (down_border ^ mapp[normy(y-1)][normx(cx)])) or (dy and (mapp[normy(cy)][normx(x)] ^ mapp[normy(cy)][normx(x-1)]))):
        poly.append(tuple(sorted([(x, y), (x+dx, y+dy)], key=lambda p: 30*p[0]+p[1])))
  poly = list(set(poly))

  jcon["Icon border"][0] = poly
  with open(f"{path}\\additional\\screen.json", "w") as f: f.write(dumps(jcon))