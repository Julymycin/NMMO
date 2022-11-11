import nmmo
from nmmo import config
import argparse
import logging
import pprint
import threading
import time
import timeit
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Callable

import numpy as np
import torch
from gym import spaces
from neurips2022nmmo import TeamBasedEnv
from torch import Tensor
from torch import multiprocessing as mp
from torch import nn

from core import file_writer, loss, prof, advantage
from neural_mmo import MonobeastEnv as Environment
from neural_mmo import NMMONet, TrainConfig, TrainEnv

class TestConfig(config.Medium, config.AllGameSystems):
    pass

conf = TrainConfig()
ienv = TeamBasedEnv( conf )
genv=TrainEnv(
        ienv,
        num_selfplay_team=1,
        reward_setting='phase1',
    )
env=Environment(genv)

obs = genv.reset()

# print(obs[1]['Entity'].items())
print(type(obs))
for k,v in obs[1].items():
    print(k,v)
    break

# model=NMMONet()
# print(model)