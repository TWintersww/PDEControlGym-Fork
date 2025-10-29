from pde_control_gym.src.rewards.base_reward import BaseReward
import numpy as np
from typing import Optional

class BrainTumorReward(BaseReward):
    """
    BrainTumorReward

    This is a custom reward class designed for the Brain Tumor 1D PDE simulation. A per-timestep step reward (only during treatment steps) and episodic reward given at the episode end are implemented
    """
    
    def reward(self, uVec: np.ndarray =None, time_index: int = None, terminate: Optional[bool] =None, truncate: Optional[bool] =None, action: Optional[float] =None, verbose = True, **kwargs):
        """
        reward

        Note: takes other params as kwargs depending on if we calculate episodic or step reward:
        For episodic reward: pass in t_benchmark
        For step reward: pass in treatment_radius, applied_dosage, and total_dosage

        :param uVec: (required) This is the solution vector of the PDE of which to compute the reward on.
        :param time_index: (required) This is the time at which to compute the reward. (Given in terms of index of uVec).
        :param terminate: States whether the episode is the terminal episode.
        :param truncate: States whether the epsiode is truncated, or ending early.
        :param action: Ignored in this reward - needed to inherit from base reward class.
        """
        # Episodic reward
        t_benchmark = kwargs["t_benchmark"]
        if t_benchmark is None:
            if verbose:
                print(f"Warning: t_benchmark is not yet set -> returned reward of 0\n")
            return 0

        if (terminate or truncate):
            if verbose:
                print(f"Reward Class: time_index - t_benchmark = {time_index} - {t_benchmark}")
            return time_index - t_benchmark
          
        # Step reward (only during treatment steps)
        treatment_radius = kwargs["treatment_radius"]
        applied_dosage = kwargs["applied_dosage"]
        total_dosage = kwargs["total_dosage"]

        # Max safe dosage given treatment radius
        def dmaxsafe(treatment_radius: int):
            return 116 * (treatment_radius ** -0.685)
        
        lambda_toxic = 50
        
        maxsafe = dmaxsafe(treatment_radius)
        if applied_dosage <= maxsafe:
            r_toxic = 0.0
        elif applied_dosage >= total_dosage:
            r_toxic = 1.0
        else:
            r_toxic = ((applied_dosage - maxsafe) / (total_dosage - maxsafe)) ** (1/3)

        if verbose:
            print(f"Reward Class: - l_t*r_toxic = {- lambda_toxic * r_toxic}")
            print(f"\tParams: treatment_radius={treatment_radius} applied_dosage={applied_dosage} dmaxsafe(treatment_radius)={dmaxsafe(treatment_radius)}")
        return - lambda_toxic * r_toxic

