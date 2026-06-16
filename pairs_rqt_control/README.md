# pairs_rqt_control

An **rqt GUI control panel** for the PAIRS UAV system — a window of buttons and
fields to fly a UAV without typing service calls, in the spirit of the
kr_autonomous_flight rqt panel but wired to the PAIRS service interface.

## What it does

- **Flight**: `Arm` · `Disarm` · `Offboard` · `Takeoff` · `Land` · `Land Home` · `Hover` · `E-Land`
- **Go to**: `x y z heading` fields with **Go To** (world frame) and **Go To (relative)**
- **Live status** line: armed / offboard / active tracker / flying
- a **UAV** field at the top so one panel can drive any namespace (`uav1`, `uav2`, …)

It calls the standard services: `hw_api/arming` (`std_srvs/SetBool`),
`hw_api/offboard`, `uav_manager/takeoff|land|land_home`,
`control_manager/hover|eland` (`std_srvs/Trigger`), and
`control_manager/goto|goto_relative` (`pairs_msgs/Vec4`).

## Run

Standalone window:
```bash
rosrun pairs_rqt_control pairs_rqt_control
# or
roslaunch pairs_rqt_control control.launch UAV_NAME:=uav1
```
Or load it inside the full rqt: `rqt` → **Plugins ▸ PAIRS ▸ PAIRS UAV Control**.

The panel reads `$UAV_NAME` for its default namespace; change the **UAV** field to
control a different drone.

## Typical flow
`Arm` → `Offboard` → `Takeoff`, wait until the status shows `tracker=MpcTracker`
and `flying=Y`, then set `x y z heading` and press **Go To**, or `Hover` / `Land`.

## License
BSD 3-Clause. See the repository [LICENSE](../LICENSE).
