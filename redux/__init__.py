import pydux
from .reducers import controllers, musicEngine

reducer = pydux.combine_reducers({
  'controllerManager': controllers.reducer,
  'musicEngine': musicEngine.reducer
})

store = pydux.create_store(reducer)