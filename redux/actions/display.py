def change_active_frame(frame):
  return{
    'type': 'ui/activeFrameChanged',
    'data': {'activeFrame': frame}
  }
