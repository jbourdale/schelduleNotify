# Schedule Notify

Python script that pops up my school day's schedule on a simple command

# Dependancies

  - Python 2.7
  - pip
  
# Installation
  
  To install scheduleNotify, please copy this repository where you want to store the script (e.g : ~/.edtNotify/)
  
  Then run
  
    sudo apt-get install python-pip
    sudo python setup.py

  This will install for you missing module. 
  
    Pygame and Pillow needed

# Running
 
 Type /usr/bin/edt or just run edt in a command-line prompt

# Usage

 edt [options]

 Options (facultative): 
  -h or --help : Display this page
  -s or --schoolyear : (1A/2A) Schoolyear to display. Will be save in config.py 
  -d or --day : The day (in relative than today) that the scheldule is query
  -r or --resolution : Save and display for this resolution.

 Exemples : 
  edt
    This will display the edt with saved config
  edt -s 1A -d 1 -r 1920,1080
    This will display the 1A's scheldule for tomorrow in a resolution of 1920,1080
 
# Up comming

  Windows support
 
# Contact

  Author : jbourdale
  
  Mail : etudiant@jbourdale.fr
