# Introduction

The software presents a cutting-edge implementation of a highly customizable model, designed specifically to address and explore the intricate aspects associated with automation and ethical considerations within the realm of computer science. By leveraging its sophisticated framework, this software enables in-depth analysis and management of the complex interplay between automated systems and ethical dimensions.

To ensure the utmost integrity and reliability, the software offers two meticulously crafted XSD schemas that serve as robust tools for validating the intricate configurations of both the robot and the individual patient. These schemas act as invaluable resources, ensuring that the specified parameters adhere to predefined standards, thus guaranteeing a coherent and compliant setup.

Significantly, this software can be envisaged as the foundational architectural prototype, establishing a solid groundwork upon which further advancements, configurations, and refinements can be built. By providing a flexible and adaptable framework, it allows for seamless evolution and intricacy within the proposed scenario, accommodating diverse requirements and fostering innovation in the field.

With its capabilities, the model holds immense potential for facilitating comprehensive simulations and meticulous verification of the robot's programming. This empowers researchers and practitioners to scrutinize and fine-tune the intricacies of the robot's behavior, meticulously aligning it with ethical, privacy, and patient dignity principles. By striving to ensure that these essential values are upheld, the software actively contributes to creating a responsible and humane technological ecosystem.

# Authors

* Andrea de Ruvo, andrea.deruvo@gssi.it
* Alberto Petrucci, alberto.petrucci@gssi.it

# Professors

* Martina De Sanctis <martina.desanctis@gssi.it>,
* Paola Inverardi <paola.inverardi@gssi.it>,
* Ludovico Iovino <ludovico.iovino@gssi.it>,
* Patrizio Pelliccione <patrizio.pelliccione@gssi.it>

# Installation
On Windows:

```
pip install -r requirements_windows.txt
```

On MacOS

```
pip install -r requirements_macos.txt
```

# Launching

To launch the software and ensure UTF-8 encoding is used for both input and output, you can run the following command:

```bash
python -X utf8 game.py
```

# Update configuration.py and patient.py

`patient.py` and  `robot.py` are auto-generated with generateDS: https://github.com/ricksladkey/generateDS .

To re-generate them after a change of `schema_configuration.xsd`:

```bash
python $PATH$/generateDS.py -o robot.py schemas/robot.xsd
```

```bash
python $PATH$/generateDS.py -o patient.py schemas/patient.xsd
```

## ToDo List

- [x] Implement a basic simulator of the scenario
- [x] Implement robot daily job using behavioural trees
- [x] Implement User-Robot interaction throught keyboard
- [x] Implement PathPlanner, Verificator and Conditioner
- [x] Load user from XML
- [x] Automatically generate map from XML
- [x] Configure robot daily plan according patients XML (use patientConfiguration attribute)

## Exam Solution
This software simulate in a 3D environment three human profiles (Bob, Alice and Nurse) and a robot that interacts with these characters and move inside the clinic. 
In particular we implemented the following profiles for Bob and Alice.
- Bob profile: If I will refuse the medications or to take pills, it is fine that the robot insists a few times. However, after a few attempts it should call the nurse. I accept that the robot uses cameras and microphones, however all my data cannot be distributed to third parties. Moreover, the robot can only store and/or distribute to the nurse videos and audios that are strictly necessary for my health, and in any case videos cannot be recorded in the toilet.
- Alice profile: I accept having assistive robots checking my health status and supporting me, however, when I show signals of distress, the robot should put me in contact with my daughter by making a video call; if she does not answer the robot should ask the intervention of a nurse and leave my room if I will be in my room of move away from me.

In order to simulate human emotions we simply press a specific key on the keyboard.

### Robot daily job
PyTrees is a Python library for working with tree-based data structures. It provides powerful functionalities for creating, manipulating, and analyzing trees. With support for tree traversal algorithms and customizable behaviors, PyTrees enables efficient management of hierarchical data representations.

The image below summarize all the tasks that the robot will daily execute in a behavioural tree implemented in PyTrees.
![Robot daily job](./images/daily_jobs.png)

## Useful references
- [Ursina](https://www.ursinaengine.org/)
- [Robotics Toolbox Python](https://petercorke.github.io/robotics-toolbox-python)
- [Bug2 Planner](https://automaticaddison.com/the-bug2-algorithm-for-robot-motion-planning/)
- [Distance transform: Base](https://robotics102.github.io/lectures/rob102_07_distance_transform.pdf)
- [Distance transform: Potential fields](https://robotics102.github.io/lectures/rob102_08_potential_field.pdf)
- [Behavioural Tree](https://roboticseabass.com/2021/05/08/introduction-to-behavior-trees/)