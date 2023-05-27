## Installation
On Windows:

```
pip install -r requirements_windows.txt
```

On MacOS

```
pip install -r requirements_macos.txt
```

## Generate configuration.py

`configuration.py` is auto-generated with generateDS: https://github.com/ricksladkey/generateDS .

To re-generate `configuration.py` after a change of `schema_configuration.xsd`:

```python
python $PATH$/generateDS.py -o configuration.py configuration/schema_configuration.xsd
```

## ToDo List

- [x] Implement a basic simulator of the scenario
- [x] Implement robot daily job using behavioural trees
- [x] Implement User-Robot interaction throught keyboard
- [x] Implement PathPlanner, Verificator and Conditioner
- [ ] Load user from XML
- [ ] ??Automatically generate map from XML??

## Robot daily job
![Robot daily job](./images/daily_jobs.png)

## Useful links:
- [Ursina](https://www.ursinaengine.org/)
- [Robotics Toolbox Python](https://petercorke.github.io/robotics-toolbox-python)
- [Bug2 Planner](https://automaticaddison.com/the-bug2-algorithm-for-robot-motion-planning/)
- [Distance transform: Base](https://robotics102.github.io/lectures/rob102_07_distance_transform.pdf)
- [Distance transform: Potential fields](https://robotics102.github.io/lectures/rob102_08_potential_field.pdf)