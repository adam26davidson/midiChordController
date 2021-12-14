import pydux
from .reducers import controllerManager, musicEngine

reducer = pydux.combine_reducers({
  'controllerManager': controllerManager.reducer,
  'musicEngine': musicEngine.reducer
})

store = pydux.create_store(reducer)