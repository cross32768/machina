# Copyright 2018 DeepX Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


import numpy as np
import torch

from machina.pds import DeterministicPd
from machina.pols import BasePol
from machina.utils import get_device


class DeterministicActionNoisePol(BasePol):
    def __init__(self, ob_space, ac_space, net, noise=None, rnn=False, normalize_ac=True, data_parallel=False, parallel_dim=0):
        if rnn:
            raise ValueError('rnn with DeterministicActionNoisePol is not supported now')
        BasePol.__init__(self, ob_space, ac_space, net, rnn=rnn, normalize_ac=normalize_ac, data_parallel=data_parallel, parallel_dim=parallel_dim)
        self.noise = noise
        self.pd = DeterministicPd()
        self.to(get_device())

    def reset(self):
        super(DeterministicActionNoisePol, self).reset()
        if self.noise is not None:
            self.noise.reset()

    def forward(self, obs, no_noise=False):
        obs = self._check_obs_shape(obs)

        if self.dp_run:
            mean = self.dp_net(obs)
        else:
            mean = self.net(obs)
        ac = mean

        if self.noise is not None and not no_noise:
            action_noise = self.noise(device=ac.device)
            ac = ac + action_noise

        ac_real = self.convert_ac_for_real(ac.detach().cpu().numpy())
        return ac_real, ac, dict(mean=mean)

    def deterministic_ac_real(self, obs):
        """
        action for deployment
        """
        obs = self._check_obs_shape(obs)

        mean = self.net(obs)
        mean_real = self.convert_ac_for_real(mean.detach().cpu().numpy())
        return mean_real, mean, dict(mean=mean)
