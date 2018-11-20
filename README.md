che696_yufei_proj
==============================

Particle image velocimetry for simple shear flows

### Copyright

Copyright (c) 2018, yufeiwei


#### Acknowledgements
 
Project based on the 
[Computational Chemistry Python Cookiecutter](https://github.com/choderalab/cookiecutter-python-comp-chem)

Installation
------------
1. Make sure python is installed. Python >=3.5 is recommended. 

2. From the base folder where you would like the set of files (a new folder will be created, by default called md_utils):
   ~~~
   git clone https://github.com/yufeiwei/che696_proj_piv.git
   ~~~

3. Make sure the following line is in .bashrc or .bashprofile. If not, add it to the file and source the file.
   ~~~
   PATH=$PATH:$HOME/.local/bin
   ~~~

4. To make a tarball to allow installation:

   a. From the main directory of your project, run:
   ~~~
    python setup.py sdist   
   ~~~
   
   b. Run
   ~~~
   pip install dist/che696_proj_yufei-*.tar.gz --user
   ~~~
Introduction
-------------
#### What can you do with this package:

Run particle image velocimetry (PIV) analysis for simple shear flow from command line.

#### Format of input images:

A pair of black-and-white images of equal size. 

Horizontal direction: flow direction

Vertical direction: velocity gradient direction

#### Output of the PIV analysis

* a .csv file containing displacement (column 2) versus position along the gradient direction (column 1)

* a plot showing the displacement profile.

Example
--------
1. To see if the installation worked and gets some brief info about the code, run:
    ~~~
    image_proc -h
    ~~~

2. To perform an particle image analysis on a pair of image, run:
    ~~~
    image_proc -m image_a_path image_b_path
    ~~~

3. To change the value of the stripe height (type=int) (default = 5), run:
    ~~~
    image_proc -m image_a_path image_b_path -d stripe_height
    ~~~
    