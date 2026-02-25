import os

# Set headless rendering for MuJoCo
os.environ["MUJOCO_GL"] = "egl"

import json
import logging
import sys
from pathlib import Path
from typing import Any, cast

import numpy as np

# Ensure project src is in path
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from PIL import Image
except ImportError:
    Image = None
    print("PIL not found. Please install Pillow to save images.")

from generic_robot_env.generic_robot_env import GenericRobotArmEnv, RobotConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MENAGERIE_PATH = Path("mujoco_menagerie")
THUMBNAILS_DIR = Path("thumbnails")


def generate_thumbnails():
    if not MENAGERIE_PATH.exists():
        logger.error(f"Directory {MENAGERIE_PATH} does not exist.")
        return

    # Create thumbnails directory if not exists
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    # Iterate over subdirectories
    for robot_dir in MENAGERIE_PATH.iterdir():
        if not robot_dir.is_dir():
            continue

        robot_name = robot_dir.name
        scene_xml = robot_dir / "scene.xml"

        # Some robots might have different main xml files, but we only
        # search for scene.xml
        if not scene_xml.exists():
            logger.warning(f"Skipping {robot_name}: scene.xml not found.")
            continue

        logger.info(f"Processing {robot_name}...")

        try:
            # Load configuration (automatically handles includes in XML)
            config = RobotConfig.from_xml(scene_xml, robot_name=robot_name)

            # Check for cameras
            if not config.camera_names:
                logger.warning(
                    f"Skipping {robot_name}: No cameras found (checked all includes)."
                )
                continue

            logger.info(
                f"Found {len(config.camera_names)} cameras for {robot_name}: "
                f"{', '.join(config.camera_names)}"
            )

            # Initialize environment
            try:
                env = GenericRobotArmEnv(
                    robot_config=config, image_obs=True, render_mode="rgb_array"
                )
            except Exception as e:
                logger.error(f"Failed to initialize environment for {robot_name}: {e}")
                continue

            # Run one simulation step
            try:
                env.reset()

                # We need to know the action space size.
                action_space = cast(Any, env.action_space)
                action = np.zeros(action_space.shape, dtype=np.float32)

                obs, _, _, _, _ = env.step(action)

                if "pixels" not in obs or not obs["pixels"]:
                    logger.warning(f"No pixel observations for {robot_name}.")
                    env.close()
                    continue

                # Save images
                for cam_name, img_array in obs["pixels"].items():
                    if Image is None:
                        logger.error("PIL not installed, cannot save image.")
                        break

                    # Convert to image
                    # MuJoCo renders are usually flip_vertical?
                    # mujoco.Renderer returns standard array.
                    # It might be uint8 [H, W, 3].

                    try:
                        img = Image.fromarray(img_array)
                        filename = f"{robot_name}_{cam_name}.png"
                        # Clean filename
                        filename = filename.replace("/", "_").replace("\\", "_")
                        save_path = THUMBNAILS_DIR / filename
                        img.save(save_path)
                        logger.info(f"Saved thumbnail: {save_path}")
                    except Exception as e:
                        logger.error(
                            f"Failed to save image for {robot_name} camera "
                            f"{cam_name}: {e}"
                        )

                # Save config as JSON
                # RobotConfig is a dataclass.
                # However, it contains Path objects and numpy arrays which
                # are not JSON serializable by default.
                # We need a helper.
                config_dict: dict[str, Any] = {
                    "robot_name": config.robot_name,
                    "xml_path": str(config.xml_path),  # Convert Path to string
                    "joint_names": config.joint_names,
                    "actuator_names": config.actuator_names,
                    "end_effector_site_name": config.end_effector_site_name,
                    "gripper_actuator_name": config.gripper_actuator_name,
                    "home_position": config.home_position.tolist()
                    if config.home_position is not None
                    else None,
                    "cartesian_bounds": config.cartesian_bounds.tolist()
                    if config.cartesian_bounds is not None
                    else None,
                    "camera_names": config.camera_names,
                    # Optional runtime detected fields might be None
                    "dof_ids": config.dof_ids.tolist()
                    if config.dof_ids is not None
                    else None,
                    "actuator_ids": config.actuator_ids.tolist()
                    if config.actuator_ids is not None
                    else None,
                    "end_effector_site_id": config.end_effector_site_id,
                    "gripper_actuator_id": config.gripper_actuator_id,
                }

                json_path = THUMBNAILS_DIR / f"{robot_name}.json"
                with open(json_path, "w") as f:
                    json.dump(config_dict, f, indent=4)
                logger.info(f"Saved config: {json_path}")

            except Exception as e:
                logger.error(f"Error running simulation for {robot_name}: {e}")
            finally:
                env.close()

        except Exception as e:
            logger.error(f"Error processing {robot_name}: {e}")


if __name__ == "__main__":
    generate_thumbnails()
