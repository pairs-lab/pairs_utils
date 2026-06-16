# pairs_rqt_control

An **rqt GUI control panel** for the PAIRS UAV system — a window of buttons and
fields to fly a UAV without typing service calls, in the spirit of the
kr_autonomous_flight rqt panel but wired to the PAIRS service interface.

## What it does

- **Flight**: `Arm` · `Disarm` · `Offboard` · `Takeoff` · `Land` · `Land Home` · `Hover` · `E-Land`
  - **`Takeoff` is one click** — it runs the whole `arm → offboard → takeoff`
    sequence with the right timing (see the note below), so you don't have to
    chain the buttons yourself.
- **Go to**: `x y z heading` fields with **Go To** (world frame) and **Go To (relative)**
- **Live status** line: armed / offboard / active tracker / flying
- a **UAV** field at the top so one panel can drive any namespace (`uav1`, `uav2`, …)

It calls the standard services: `hw_api/arming` (`std_srvs/SetBool`),
`hw_api/offboard`, `uav_manager/takeoff|land|land_home`,
`control_manager/hover|eland` (`std_srvs/Trigger`), and
`control_manager/goto|goto_relative` (`pairs_msgs/Vec4`).

## Run

In the Gazebo simulation it already opens automatically in the **`gui`** tmux
window of the single-drone sessions. To open it yourself:
```bash
rosrun pairs_rqt_control pairs_rqt_control
# or
roslaunch pairs_rqt_control control.launch UAV_NAME:=uav1
```
Or load it inside the full rqt: `rqt` → **Plugins ▸ PAIRS ▸ PAIRS UAV Control**.

The panel reads `$UAV_NAME` for its default namespace; change the **UAV** field to
control a different drone.

## How to fly

1. Press **Takeoff** — one click arms, switches to offboard, and takes off.
   Watch the status line until it reads `tracker=MpcTracker` and `flying=Y`.
2. Type a target into `x y z heading` and press **Go To** (world frame) or
   **Go To (relative)**. **Hover** stops and holds.
3. Press **Land** (in place) or **Land Home** (return to the takeoff point).

The bottom line shows the result of the last action (green = OK, red = failed).

### Why a one-click takeoff?

Taking off needs a specific sequence (the same one `automatic_start` runs):
**arm → enable the control output → offboard → takeoff**, back-to-back. The
control-output step makes the controller start streaming setpoints; without it
PX4 immediately drops OFFBOARD and takeoff fails with *"UAV not in offboard
mode"*. PX4 SITL also often rejects the first arm command, so it has to be
retried. The **Takeoff** button does all of this for you (arm-retry, enable
output, offboard, takeoff, and a couple of retries on failure). The individual
**Arm** / **Offboard** buttons are kept for manual/advanced use.

## License
BSD 3-Clause. See the repository [LICENSE](../LICENSE).
