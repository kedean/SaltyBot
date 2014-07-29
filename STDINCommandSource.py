from CommandSourceInterface import CommandSourceInterface
import sys

class STDINCommandSource(CommandSourceInterface):
  messagingFunc = print

  def __init__(self):
    pass
  def __init__(self, messagingFunc):
    self.messagingFunc = messagingFunc

  def commands():
    comm = None
    while comm != self.QUIT_COMMAND:
      comm_string = raw_input()
