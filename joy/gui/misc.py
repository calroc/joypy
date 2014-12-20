

class FileFaker(object):

  def __init__(self, T):
    self.T = T

  def write(self, text):
    self.T.insert('end', text)

  def flush(self):
    pass


def is_numerical(s):
  try:
    float(s)
  except ValueError:
    return False
  return True
