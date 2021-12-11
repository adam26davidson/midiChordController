from abc import ABC, abstractmethod, abstractproperty
from typing import Dict
from numpy import * 

class Controller(ABC):

  @abstractmethod
  def checkIfConnected():
    pass

  @abstractmethod
  def getUIMap(self):
    pass

  @abstractmethod
  def getMusicEngineMap(self):
    pass

  def processAnalogValue(self, value, control: Dict, config: Dict, state: Dict):
    range = control['range']

    valueHistory = state["valueHistory"].copy()
    valueHistory.append(value)
    if (len(valueHistory) > config["averageCount"]):
      valueHistory.pop(0)

    # get the average of the past raw values (prevents fluttering)
    sum = 0
    for val in valueHistory:
      sum += val
    avg = sum / len(valueHistory)

    #clamp value to between -0.999 and 0.999
    slope = 2.0 / (range["top"]- range["bottom"])
    intercept = 1 - (slope*range["top"])
    normalized =  (slope*avg) + intercept
    normalized = max(min(normalized, 0.999), -0.999)

    thresholdValue = 0
    #determine threshold value
    if normalized > config["threshold"]:
      thresholdValue = 1
    elif normalized < -1*config["threshold"]:
      thresholdValue = -1

    thresholdValueChanged = thresholdValue != state["thresholdValue"]
    
    return {
      "thresholdValueChanged": thresholdValueChanged,
      "value": normalized,
      "thresholdValue": thresholdValue,
      "state": {
        "valueHistory": valueHistory,
        "thresholdValue": thresholdValue
      }
    }