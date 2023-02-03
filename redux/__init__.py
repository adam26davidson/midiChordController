import pydux
from .reducers import controllerManager, musicEngine, display

reducer = pydux.combine_reducers({
  'controllerManager': controllerManager.reducer,
  'musicEngine': musicEngine.reducer,
  'display': display.reducer
})

store = pydux.create_store(reducer)