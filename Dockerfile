FROM osrf/ros:humble-desktop

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-numpy \
    python3-yaml \
    python3-scipy \
    && rm -rf /var/lib/apt/lists/*

# Install open3d (Open3D might need some extra libs for headless or UI)
RUN pip3 install open3d

# Set up workspace
WORKDIR /ros2_ws
COPY src /ros2_ws/src

# Source ROS2 and build
RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

# Set up entrypoint
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

CMD ["bash"]
