class Point:

   def __init__(self, x=0, y=0):
      self.x = x
      self.y = y

   def translate(self, dx, dy):
      self.x += dx
      self.y += dy

   def move(self, x, y):
      self.x = x
      self.y = y

   def __str__(self):
      return "(" + str(self.x) + ", " + str(self.y) + ")"
