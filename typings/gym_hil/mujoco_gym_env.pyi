import mujoco

from typing import Any, Literal, Optional, TypeVar, Generic
from pathlib import Path
import gymnasium as gym

ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

class GymRenderingSpec:
    height: int
    width: int
    camera_id: str | int
    mode: Literal["rgb_array", "human"]
    def __init__(self, height: int = 128, width: int = 128, camera_id: str | int = -1, mode: Literal["rgb_array", "human"] = "rgb_array") -> None: ...

class MujocoGymEnv(gym.Env[ObsType, ActType], Generic[ObsType, ActType]):
    metadata: dict[str, Any]
    render_mode: str | None
    _model: mujoco.MjModel
    _data: mujoco.MjData
    _n_substeps: int
    def __init__(self, xml_path: Path, seed: int = 0, control_dt: float = 0.02, physics_dt: float = 0.002, render_spec: GymRenderingSpec = ...) -> None: ...
    def step(self, action: ActType) -> tuple[ObsType, float, bool, bool, dict[str, Any]]: ...
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None) -> tuple[ObsType, dict[str, Any]]: ...
    def render(self) -> Any: ...
    def close(self) -> None: ...
    @property
    def model(self) -> mujoco.MjModel: ...
    @property
    def data(self) -> mujoco.MjData: ...
