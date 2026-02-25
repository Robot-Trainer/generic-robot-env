# generic_robot_env

A generic MuJoCo-based robot environment generator for LeRobot or Gymnasium-style experiments.

This library is heavily inspired by and depends on the [gym_hil](https://github.com/huggingface/gym-hil) project which implemented the first variant of these configurations.

This package provides

- `RobotConfig`: A version of the gym_hil MujocoGymEnv that can extract its configuration from a well-formed mujoco scene.xml file.
- `GenericRobotArmEnv`, a configurable robot-control base environment around a MuJoCo XML model, with reusable robot methods (`apply_action`, `get_robot_state`, `reset_robot`, `render`, `get_gripper_pose`).
- `GenericTaskEnv`, a task-oriented layer on top of `GenericRobotArmEnv` that adds Panda-pick-style task behavior (task reset, environment state observation, reward, success/termination).

## Features

- Auto-detects joints, actuators, end-effector site, cameras and (optionally) a `home` keyframe from a MuJoCo XML file.
- Two control modes: `osc` (end-effector operational-space control) and `joint` (direct actuator control).
- Separation of concerns: robot-control APIs in `GenericRobotArmEnv`, task APIs in `GenericTaskEnv`.
- Optional image observations from model cameras.
- Returns structured observations compatible with Gymnasium `spaces.Dict`.

## Installation

This project depends on MuJoCo and Gymnasium. Install prerequisites in your Python environment (example using pip):

```bash
pip install generic_robot_env
```

Note: The repository includes typed stubs under `typings/` for local development and the project expects a working MuJoCo installation accessible to the `mujoco` Python package.

## Usage examples

- **Simple loop:** Create a configuration from a scene XML and run a quick random-action loop. [mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie) is a good repository of scenes.

```python
from pathlib import Path
import numpy as np
from generic_robot_env.generic_robot_env import RobotConfig, GenericTaskEnv

xml = Path("mujoco_menagerie/aloha/scene.xml")  # point to a model in the repo
config = RobotConfig.from_xml(xml, robot_name="aloha")
env = GenericTaskEnv(config, control_mode="osc", image_obs=False)

obs, _ = env.reset()
for _ in range(200):
	action = env.action_space.sample()
	obs, reward, terminated, truncated, info = env.step(action)
	if terminated:
		break
env.close()
```

- **Image observations:** Enable `image_obs=True` to receive pixel arrays under `obs['pixels']` keyed by camera name (when cameras exist in the MJCF).

```python
config = RobotConfig.from_xml(Path("mujoco_menagerie/aloha/aloha.xml"), robot_name="aloha")
env = GenericTaskEnv(config, control_mode="osc", image_obs=True)
obs, _ = env.reset()
# obs['pixels'] -> dict(camera_name -> HxWx3 uint8 array)
```

Notes:

- If the MuJoCo model contains a keyframe named `home`, the environment will try to use that as the default joint pose.
- If cameras are present and `image_obs=True`, pixel observations are returned under `obs['pixels']` keyed by camera name.

## Files

- `src/generic_robot_env/generic_robot_env.py` — main environment implementation (this module).

See [src/generic_robot_env/generic_robot_env.py](src/generic_robot_env/generic_robot_env.py) for the full implementation.

## Observation and action spaces

`GenericRobotArmEnv` observations are returned as a Gymnasium `spaces.Dict` with primary keys under `agent_pos`:

- `joint_pos`: Joint positions for the detected robot joints (array)
- `joint_vel`: Joint velocities (array)
- `tcp_pose`: End-effector pose as [x, y, z, qx, qy, qz, qw]
- `tcp_vel`: End-effector linear and angular velocity (6D)
- `gripper_pose` (optional): Single-value gripper state when a gripper actuator is detected

When `image_obs=True`, `pixels` is included and contains a `spaces.Dict` of camera-name -> RGB image arrays.

`GenericTaskEnv` uses Panda-pick-style observations:

- State mode: `{"agent_pos": <vector>, "environment_state": <object position>}`
- Image mode: `{"pixels": <camera dict>, "agent_pos": <vector>}`

Action spaces depend on `control_mode`:

- `osc`: Continuous Box controlling end-effector delta in position (x,y,z) and rotation (rx,ry,rz). If a gripper is available, an extra dimension for gripper command is appended.
- `joint`: Continuous Box mapped directly to actuator control values. When a gripper actuator exists, it is appended to the action vector.

## Implementation notes

- The environment auto-resolves joint and actuator ids using the MuJoCo model and maps qpos/qvel indices for direct data access.
- For OSC control, a simple opspace solver (from `gym_hil.controllers.opspace`) is used each simulation substep to compute actuator torques that track a desired end-effector target.
- Gripper mapping tries to respect actuator control ranges defined in the model (`actuator_ctrlrange`) when present.

## Running tests

Run the test suite with pytest from the repository root:

```bash
pytest tests
```

## Local presubmit hooks

Install local git hooks so linting/formatting runs before commit and tests run before push:

```bash
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
```

Run hooks manually (optional):

```bash
uv run pre-commit run --all-files
uv run pre-commit run --hook-stage pre-push
```

- **Faster experiments:** Many models include camera/site names that the environment will auto-detect (end-effector sites, cameras, and optional `home` keyframes). If your chosen model provides a `home` keyframe the environment will attempt to use it as the default reset pose.

- **Example with a bundled task:** Some pre-made gym-style wrappers (for example in `gym_hil`) subclass the same base utilities; you can switch between `GenericRobotArmEnv` and those wrappers by pointing both at the same XML and configuration.

## **Tips and troubleshooting**

- **Missing end-effector/site detection:** If the end-effector isn't found automatically, open the XML and add a site with a common name like `ee`, `end_effector`, `tcp` or `attachment_site` so auto-detection can find it.
- **Gripper mapping:** If the model exposes a gripper actuator with a control range, the environment will append a gripper command dimension to the action space and will respect `actuator_ctrlrange` when possible.

## Contributing

Contributions, bug reports and improvements are welcome. When adding new robots or tasks, prefer adding descriptive camera and site names in the MJCF so the auto-detection heuristics can find the end-effector and camera frames.

## License

This project inherits the license of the repository. Ensure you follow the licensing terms of MuJoCo and any third-party dependencies.
