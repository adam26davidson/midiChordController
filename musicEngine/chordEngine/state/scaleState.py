from typing import Dict, List


class ScaleState():

    keyAgnostic: List[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    noteClassMap: Dict[int, List[int]] = {}
    allNotesMap: Dict[int, List[int]] = {}