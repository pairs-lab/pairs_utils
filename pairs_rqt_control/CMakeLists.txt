cmake_minimum_required(VERSION 3.5)
project(pairs_rqt_control)

find_package(catkin REQUIRED COMPONENTS
  rqt_gui
  rqt_gui_py
)

catkin_python_setup()

catkin_package()

install(FILES plugin.xml
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

catkin_install_python(PROGRAMS scripts/pairs_rqt_control
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
