import pydux

from .reducers import controller_coupler, controller_manager, display, music_engine

reducer = pydux.combine_reducers({
    'controllerManager': controller_manager.reducer,
    'controllerCoupler': controller_coupler.reducer,
    'musicEngine': music_engine.reducer,
    'display': display.reducer
})

store = pydux.create_store(reducer)
