#!/usr/bin/env python
"""rqt control panel for the PAIRS UAV system.

A small window of buttons + fields wired to the standard PAIRS services, so you
can arm, take off, fly (goto), hover, and land from a GUI — similar to the
kr_autonomous_flight rqt panel, adapted to the PAIRS service interface.
"""
import os

import rospy
from rqt_gui_py.plugin import Plugin
from python_qt_binding.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit, QDoubleSpinBox,
)
from python_qt_binding.QtCore import QTimer

from std_srvs.srv import Trigger, SetBool

try:
    from pairs_msgs.srv import Vec4
    from pairs_msgs.msg import ControlManagerDiagnostics, HwApiStatus
    _MSGS = True
except Exception:  # pragma: no cover - depends on a sourced PAIRS workspace
    _MSGS = False


class PairsControlPanel(Plugin):

    def __init__(self, context):
        super(PairsControlPanel, self).__init__(context)
        self.setObjectName('PairsControlPanel')

        self._diag = None
        self._hw = None
        self._sub_diag = None
        self._sub_hw = None

        widget = QWidget()
        widget.setObjectName('PairsControlPanelUi')
        widget.setWindowTitle('PAIRS UAV Control')
        root = QVBoxLayout(widget)

        # --- UAV selector ---
        row = QHBoxLayout()
        row.addWidget(QLabel('UAV:'))
        self._uav_edit = QLineEdit(os.environ.get('UAV_NAME', 'uav1'))
        self._uav_edit.setMaximumWidth(120)
        self._uav_edit.editingFinished.connect(self._resubscribe)
        row.addWidget(self._uav_edit)
        row.addStretch(1)
        root.addLayout(row)

        # --- live status line ---
        self._status = QLabel(u'—')
        self._status.setStyleSheet('font-family: monospace; padding: 2px;')
        root.addWidget(self._status)

        # --- flight buttons ---
        flight = QGroupBox('Flight')
        fg = QGridLayout(flight)
        buttons = [
            ('Arm',       lambda: self._call('hw_api/arming', SetBool, True)),
            ('Disarm',    lambda: self._call('hw_api/arming', SetBool, False)),
            ('Offboard',  lambda: self._call('hw_api/offboard', Trigger)),
            ('Takeoff',   self._takeoff_sequence),
            ('Land',      lambda: self._call('uav_manager/land', Trigger)),
            ('Land Home', lambda: self._call('uav_manager/land_home', Trigger)),
            ('Hover',     lambda: self._call('control_manager/hover', Trigger)),
            ('E-Land',    lambda: self._call('control_manager/eland', Trigger)),
        ]
        for i, (label, cb) in enumerate(buttons):
            b = QPushButton(label)
            b.clicked.connect(cb)
            fg.addWidget(b, i // 4, i % 4)
        root.addWidget(flight)

        # --- goto ---
        goto = QGroupBox('Go to  (x  y  z  heading)')
        gg = QGridLayout(goto)
        self._spin = {}
        for col, (name, default) in enumerate([('x', 0.0), ('y', 0.0), ('z', 3.0), ('heading', 0.0)]):
            sb = QDoubleSpinBox()
            sb.setRange(-1000.0, 1000.0)
            sb.setDecimals(2)
            sb.setSingleStep(0.5)
            sb.setValue(default)
            self._spin[name] = sb
            gg.addWidget(QLabel(name), 0, col)
            gg.addWidget(sb, 1, col)
        b_goto = QPushButton('Go To')
        b_goto.clicked.connect(lambda: self._goto('control_manager/goto'))
        b_rel = QPushButton('Go To (relative)')
        b_rel.clicked.connect(lambda: self._goto('control_manager/goto_relative'))
        gg.addWidget(b_goto, 2, 0, 1, 2)
        gg.addWidget(b_rel, 2, 2, 1, 2)
        root.addWidget(goto)

        # --- last action result ---
        self._result = QLabel('ready')
        self._result.setStyleSheet('font-family: monospace; padding: 2px; color: #666;')
        self._result.setWordWrap(True)
        root.addWidget(self._result)

        root.addStretch(1)
        context.add_widget(widget)
        self._widget = widget

        if not _MSGS:
            self._result.setText('pairs_msgs not found — source the PAIRS workspace before launching')

        self._resubscribe()
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.start(300)

    # ------------------------------------------------------------------ ROS

    def _uav(self):
        return self._uav_edit.text().strip() or 'uav1'

    def _resubscribe(self):
        if not _MSGS:
            return
        for s in (self._sub_diag, self._sub_hw):
            if s is not None:
                s.unregister()
        uav = self._uav()
        self._diag = None
        self._hw = None
        self._sub_diag = rospy.Subscriber('/%s/control_manager/diagnostics' % uav,
                                          ControlManagerDiagnostics, self._on_diag, queue_size=1)
        self._sub_hw = rospy.Subscriber('/%s/hw_api/status' % uav,
                                        HwApiStatus, self._on_hw, queue_size=1)

    def _on_diag(self, msg):
        self._diag = msg

    def _on_hw(self, msg):
        self._hw = msg

    def _call(self, srv, srv_type, *args):
        full = '/%s/%s' % (self._uav(), srv)
        try:
            rospy.wait_for_service(full, timeout=2.0)
            resp = rospy.ServiceProxy(full, srv_type)(*args)
            ok = bool(getattr(resp, 'success', True))
            self._set_result('%s -> %s %s' % (srv, 'OK' if ok else 'FAIL',
                                              getattr(resp, 'message', '')), ok)
            return ok
        except Exception as e:  # rospy.ServiceException, ROSException (timeout), etc.
            self._set_result('%s -> ERROR: %s' % (srv, e), False)
            return False

    def _goto(self, srv):
        goal = [self._spin['x'].value(), self._spin['y'].value(),
                self._spin['z'].value(), self._spin['heading'].value()]
        self._call(srv, Vec4, goal)

    # One-click takeoff: arm -> offboard -> takeoff, chained with non-blocking
    # timers. PX4 SITL often rejects the first arm command(s) (estimator/home
    # still converging), so arming is retried until it sticks; PX4 also drops
    # OFFBOARD on the ground unless takeoff follows within ~1 s, so offboard and
    # takeoff are issued back-to-back and the whole tail retries on failure.
    def _takeoff_sequence(self):
        self._tk_arm_tries = 0
        self._tk_loop_tries = 0
        self._set_result('takeoff: arming...', True)
        self._tk_arm()

    def _tk_arm(self):
        if (self._hw is not None and self._hw.armed) or self._call('hw_api/arming', SetBool, True):
            QTimer.singleShot(1500, self._tk_output)
        elif self._tk_arm_tries < 15:
            self._tk_arm_tries += 1
            self._set_result('takeoff: arming (attempt %d)...' % (self._tk_arm_tries + 1), True)
            QTimer.singleShot(1000, self._tk_arm)
        else:
            self._set_result('takeoff: could not arm after %d attempts' % self._tk_arm_tries, False)

    def _tk_output(self):
        # enable the control_manager output (as automatic_start does) so it starts
        # streaming setpoints; without this PX4 drops OFFBOARD and takeoff fails.
        self._set_result('takeoff: enabling control output...', True)
        self._call('control_manager/toggle_output', SetBool, True)
        QTimer.singleShot(600, self._tk_offboard)

    def _tk_offboard(self):
        self._set_result('takeoff: offboard + takeoff...', True)
        self._call('hw_api/offboard', Trigger)
        QTimer.singleShot(700, self._tk_takeoff)

    def _tk_takeoff(self):
        if self._call('uav_manager/takeoff', Trigger):
            return
        # not armed / not offboard / transient — restart the sequence a few times
        if self._tk_loop_tries < 4:
            self._tk_loop_tries += 1
            QTimer.singleShot(700, self._tk_arm)

    # ------------------------------------------------------------------- UI

    def _set_result(self, text, ok):
        self._result.setText(text)
        self._result.setStyleSheet('font-family: monospace; padding: 2px; color: %s;'
                                   % ('#138a13' if ok else '#c00'))

    def _refresh(self):
        if not _MSGS:
            return
        parts = ['uav=%s' % self._uav()]
        if self._hw is not None:
            parts.append('armed=%s' % ('Y' if self._hw.armed else 'N'))
            parts.append('offboard=%s' % ('Y' if self._hw.offboard else 'N'))
        else:
            parts.append('hw_api: no data')
        if self._diag is not None:
            parts.append('tracker=%s' % self._diag.active_tracker)
            parts.append('flying=%s' % ('Y' if self._diag.flying_normally else 'N'))
        self._status.setText('   '.join(parts))

    def shutdown_plugin(self):
        if getattr(self, '_timer', None) is not None:
            self._timer.stop()
        for s in (self._sub_diag, self._sub_hw):
            if s is not None:
                s.unregister()
