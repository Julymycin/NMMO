from collections import defaultdict
from typing import Dict

import numpy as np
import math
from neurips2022nmmo import Metrics

EQUIPMENT = [
    "HatLevel", "BottomLevel", "TopLevel", "HeldLevel", "AmmunitionLevel"
]
PROFESSION = ["MeleeLevel", "RangeLevel", "MageLevel",'MageLevel', 'FishingLevel', 'HerbalismLevel', 'ProspectingLevel', 'CarvingLevel', 'AlchemyLevel']


class RewardParser:
    def __init__(self, phase: str = "phase1"):
        assert phase in ["phase1", "phase2"]
        self.phase = phase
        self.best_ever_equip_level = defaultdict(
            lambda: defaultdict(lambda: 0))

    def reset(self):
        self.best_ever_equip_level.clear()

    def parse(
        self,
        prev_metric: Dict[int, Metrics],
        curr_metric: Dict[int, Metrics],
        obs: Dict[int, Dict[str, np.ndarray]],
        step: int,
        done: int,
    ) -> Dict[int, float]:
        reward = {}
        health, food, water, fog, va_move, population = self.extract_info_from_obs(obs)
        for agent_id in curr_metric:
            curr, prev = curr_metric[agent_id], prev_metric[agent_id]
            # if agent_id==0 and curr['TimeAlive']%200==0:
            #     print('-----------Time:{} Agent: {}\n -----------Previous {} \n ----------- Current {}\n ----------- OBS {} \n'
            #             .format(curr["TimeAlive"],agent_id, prev,curr,obs[agent_id]))

            r = 0.0
            if agent_id in done and done[agent_id]:
                r-=2
                reward[agent_id] = r
                continue
            hp=health[agent_id] if agent_id in health else 0. # range(0,1]
            ugold=curr['Gold']-prev['Gold']
            usells=curr['Sells']-prev['Sells']
            uequip=curr['Equipment']-prev['Equipment']
            ubuys=curr['Buys']-prev['Buys']
            uration=curr['RationConsumed']-prev['RationConsumed']
            upoultice=curr['PoulticeConsumed']-prev['PoulticeConsumed']
            gained=ugold+uequip
            kill_gained=gained-usells


            
            # Alive reward
            # with time going on, r from almost 0 to 5, first slow and last rapid 
            if curr["TimeAlive"]-prev['TimeAlive']>0 and curr["TimeAlive"]>=900:
                r+=(curr['TimeAlive']-prev['TimeAlive'])*math.exp((curr['TimeAlive']-1024)/10.)*1.0
            if curr["TimeAlive"] == 1024:
                r += 5.0
            
            # Obstacle reward
            # if agent_id in va_move and np.sum(va_move[agent_id])>=3:
            #     r+= 2./1000

            # Fog
            if agent_id in fog:
                fog_damage=fog[agent_id][7,7]
                if fog_damage<=0:
                    if curr["TimeAlive"]>900: r+=10./1000
                else:
                    r-=100./1000*math.exp(1.-hp)*(1+10*fog_damage)

            # Team reward
            # if agent_id in population:
            #     allian1=np.sum(population[agent_id][4:11,4:11]==1) # in range 3
            #     enemy1=np.sum(population[agent_id][4:11,4:11]>1)
            #     allian2=np.sum(population[agent_id]==1) # in observation
            #     enemy2=np.sum(population[agent_id]>1)

            #     r+=(allian1-enemy1)*10/1000*(1-abs(allian1-4)/4)
            #     r+=allian2*1/1000*(1-abs(allian1-4)/4)
            
            # Defeats reward, gold and health
            kill=curr["PlayerDefeats"] - prev["PlayerDefeats"]
            
            # r += kill*(1 /(1+math.exp(-hp*5)) -0.5)*2*max(1,kill_gained/10)
            r += kill*(1 /(1+math.exp(-hp*5)) -0.5)*2

            # r+=min(0,np.log(hp+0.6))
            # r+=max(0,gained/10.)


            # Profession reward
            for p in PROFESSION:
                r += (curr[p] - prev[p]) * 0.1 * curr[p]
            # Equipment reward
            for e in EQUIPMENT:
                delta = curr[e] - self.best_ever_equip_level[agent_id][e]
                if delta > 0:
                    r += delta * 0.1 * curr[e]
                    self.best_ever_equip_level[agent_id][e] = curr[e]
            
            # DamageTaken penalty
            if kill==0 and hp<0.8:
                r -= (curr["DamageTaken"] - prev["DamageTaken"]) * 0.1
            
            # Starvation penalty
            if agent_id in food and food[agent_id] <0.5:
                r -= 1.*(1/(1+math.exp(food[agent_id]*10)))
            if agent_id in water and water[agent_id] <0.5:
                r -= 1.*(1/(1+math.exp(water[agent_id]*10)))


            # if agent_id in done and done[agent_id]:
            #         r -= 5.0
            # phase2 only
            if self.phase == "phase2":
                # Death penalty
                if agent_id in done and done[agent_id]:
                    r -= 5.0
                    
            reward[agent_id] = r
        return reward

    def extract_info_from_obs(self, obs: Dict[int, Dict[str, np.ndarray]]):
        # gold = {i: obs[i]["self_entity"][0, 9] for i in obs}
        health = {i: obs[i]["self_entity"][0, 10] for i in obs}
        food = {i: obs[i]["self_entity"][0, 11] for i in obs}
        water = {i: obs[i]["self_entity"][0, 12] for i in obs}
        fog = {i:obs[i]["death_fog_damage"] for i in obs}
        va_move={i:obs[i]["va_move"] for i in obs}
        population={i:obs[i]["entity_population"] for i in obs}
        return health, food, water, fog, va_move, population
