from typing import Callable, Protocol

from pyrsistent.typing import PMap

from redux.types import ReduxAction

_Reducer = Callable[[PMap[str, object] | None, ReduxAction], PMap[str, object]]


class Store(Protocol):
    def get_state(self) -> PMap[str, PMap[str, object]]: ...
    def dispatch(self, action: ReduxAction) -> ReduxAction: ...
    def subscribe(self, listener: Callable[[], None]) -> Callable[[], None]: ...


def create_store(reducer: _Reducer) -> Store: ...


def combine_reducers(
    reducers: dict[str, _Reducer],
) -> _Reducer: ...
