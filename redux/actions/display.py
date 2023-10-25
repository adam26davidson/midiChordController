def changeActiveFrame(frame):
  return{
    'type': 'ui/activeFrameChanged',
    'data': {'activeFrame': frame}
  }