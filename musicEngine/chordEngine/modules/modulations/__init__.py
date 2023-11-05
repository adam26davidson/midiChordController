from musicEngine.chordEngine.modules.modulations.modulationsState import ModulationSide
from ...chordEngineState import state
from redux import store
from redux.actions import musicEngine as actions

class Modulations():

    def __init__(self, setting):
        

    def set(self, side: ModulationSide):
        if state.modulation.side != side:
            scale = state.scale.keyAgnostic
            if side != ModulationSide.NONE:
                scale = self.modulations[side].applyToScale()
            store.dispatch(actions.changeModulation({
                'scale': scale,
                'side': side
            }))
            self.state['modulation'] = side
            self.updateChordType()