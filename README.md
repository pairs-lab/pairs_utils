# pairs_utils

A metapackage that bundles the small helper utilities of the PAIRS UAV stack. Installing it pulls in a collection of support nodes for transform-tree plumbing and odometry republishing — none of which are core flight components, but all of which are handy when building and debugging a system. Each tool is a standalone package; this metapackage just groups them.

## Contents

This branch (ROS 2 Jazzy) aggregates:

- `pairs_odometry_republisher` — republishes odometry messages (e.g. reframed or relayed) for downstream consumers.
- `pairs_tf_connector` — joins two transform trees through their root frames, keeping selected frames coincident.
- `pairs_tf_mirror` — mirrors a transform tree into another namespace.
- `pairs_tf_reconfigure` — interactively adjusts a transform at runtime.

## Branches

- `ros1` — ROS 1 Noetic (catkin)
- `ros2` — ROS 2 Jazzy (ament_cmake)

The set of bundled packages differs between branches.

## Install (ROS 2 Jazzy)

```bash
sudo apt install ros-jazzy-pairs-utils
```

## License
BSD 3-Clause. Derived from the CTU-MRS `pairs_utils` package; the original
copyright is retained in [LICENSE](LICENSE).
