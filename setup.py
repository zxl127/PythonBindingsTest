from setuptools import setup

setup(
    name='pybindings',
    version='0.1.0',
    packages=['pybindings'],
    install_requires=['invoke'],
    entry_points={
        'console_scripts': ['pybindings = pybindings.tasks:program.run']
    }
)
