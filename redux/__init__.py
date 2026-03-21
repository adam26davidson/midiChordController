import pydux

from .reducers import controllerCoupler, controllerManager, display, musicEngine

reducer = pydux.combine_reducers({
    'controllerManager': controllerManager.reducer,
    'controllerCoupler': controllerCoupler.reducer,
    'musicEngine': musicEngine.reducer,
    'display': display.reducer
})

store = pydux.create_store(reducer)
