import numpy as np
from typing import Any, Optional, Union

class MjModel:
    njnt: int
    nu: int
    nsite: int
    nkey: int
    ncam: int
    nv: int
    nbody: int
    jnt_type: np.ndarray
    jnt_qposadr: np.ndarray
    jnt_dofadr: np.ndarray
    key_qpos: np.ndarray
    actuator_ctrlrange: np.ndarray
    nmocap: int
    opt: Any

    @staticmethod
    def from_xml_path(xml_path: str) -> MjModel: ...
    def joint(self, name: str) -> Any: ...
    def actuator(self, name: str) -> Any: ...
    def site(self, name: str) -> Any: ...

class MjData:
    qpos: np.ndarray
    qvel: np.ndarray
    ctrl: np.ndarray
    site_xpos: np.ndarray
    site_xmat: np.ndarray
    mocap_pos: np.ndarray
    mocap_quat: np.ndarray
    def __init__(self, model: MjModel) -> None: ...

class Renderer:
    def __init__(self, model: MjModel, height: int = ..., width: int = ...) -> None: ...
    def update_scene(self, data: MjData, camera: Union[int, str, None] = None) -> None: ...
    def render(self) -> np.ndarray: ...
    def close(self) -> None: ...

def mj_id2name(model: MjModel, obj_type: int, id: int) -> Optional[str]: ...
def mj_forward(model: MjModel, data: MjData) -> None: ...
def mj_step(model: MjModel, data: MjData) -> None: ...
def mj_jacSite(model: MjModel, data: MjData, jac_p: np.ndarray, jac_r: np.ndarray, site_id: int) -> None: ...
def mju_mat2Quat(quat: np.ndarray, mat: np.ndarray) -> None: ...

class mjtObj:
    mjOBJ_ACTUATOR: int
    mjOBJ_SITE: int
    mjOBJ_CAMERA: int
    mjOBJ_JOINT: int
    mjOBJ_KEY: int

def mj_name2id(model: MjModel, obj_type: int, name: str) -> int: ...

class mjtJoint:
    mjJNT_HINGE: int
    mjJNT_SLIDE: int
