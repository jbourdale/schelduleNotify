#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    setup.py for edtNotify

    author: jbourdale
    mail: etudiant@jbourdale.fr
"""

import os
try:
    from datetime import datetime
    from PIL import Image
    import calendar, requests, json, pygame
except Exception, e:
    print "Some dependencies are missing: %s"%e
    print "Running : pip2 install pygame pillow requests json datetime"
    os.system("pip2 install pygame pillow requests datetime")


print "Setting up config.py..."
annee = raw_input("School Year? (1A/2A) ")
while annee != "1A" and annee != "2A":
    annee = raw_input("School Year ? (1A/2A) ")

pygame.init()
resolution = ",".join([str(pygame.display.Info().current_w),str(pygame.display.Info().current_h)])
print "Detected screen resolution : %s"%resolution

content = json.dumps({
    'path' : os.getcwd(),
    'annee' : annee,
    'resolution' : resolution,
})

try:
    with open("config.py", "w+") as config:
        config.write(content)
        os.system("chmod a+w config.py")
        config.close()
except:
    print "Can't open config.py. Exiting"
    exit()

print "Creating /usr/bin/edt script"
pwd = os.getcwd()
script = "#!/bin/bash\npython "+pwd+"/main.py "+pwd+"/"
try:
    with open("/usr/bin/edt", "w+") as launcher:
        os.system("chmod +x /usr/bin/edt")
        launcher.write(script)
        launcher.close()
except Exception, e:
    print "Error (%s). Can't right at /usr/bin/. Check if you run setup.py with root privilege."%e
