# pairs_utils

A metapackage that bundles the small helper utilities of the PAIRS UAV stack. Installing it pulls in a collection of support nodes for transform-tree plumbing, sensor/camera republishing, dynamic reconfiguration, and example/demo flights — none of which are core flight components, but all of which are handy when building and debugging a system. Each tool is a standalone package; this metapackage just groups them.

## Contents

This branch (ROS 1 Noetic) aggregates:

- `pairs_camera_republisher` — republishes camera streams with frame-ID rewriting and throttling.
- `pairs_circle_flier` — flies the UAV in a circle (useful for tuning and demos).
- `pairs_euler_counter_example` — a worked counter-example illustrating Euler-angle pitfalls.
- `pairs_multireconfigure` — dynamically reconfigures parameters of several nodes at once.
- `pairs_sensor_info` — reports sensor status/metadata.
- `pairs_tf_connector` — joins two transform trees through their root frames, keeping selected frames coincident.
- `pairs_tf_estimator` — estimates a static transform between two frames from observed data.
- `pairs_tf_mirror` — mirrors a transform tree into another namespace.
- `pairs_tf_reconfigure` — interactively adjusts a transform at runtime.
- `pairs_throw_activation` — detects a hand-throw to arm/launch the UAV.

## Branches

- `ros1` — ROS 1 Noetic (catkin)
- `ros2` — ROS 2 Jazzy (ament_cmake)

The set of bundled packages differs between branches.

## Install (ROS 1 Noetic)

```bash
sudo apt install ros-noetic-pairs-utils
```

## License
BSD 3-Clause. Derived from the CTU-MRS `pairs_utils` package; the original
copyright is retained in [LICENSE](LICENSE).
