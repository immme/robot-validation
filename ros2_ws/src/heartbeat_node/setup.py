from setuptools import find_packages, setup

package_name = "heartbeat_node"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="immme",
    maintainer_email="immme@users.noreply.github.com",
    description="Publishes a counter on /heartbeat every 0.5 seconds (test target node).",
    license="TODO",
    entry_points={
        "console_scripts": [
            "heartbeat_publisher = heartbeat_node.heartbeat_publisher:main",
        ],
    },
)
