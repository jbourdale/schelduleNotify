#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    edtNotify is able to dl and display my school time schedule on a simple command

    Author : jBourdale
    mail : etudiant@jbourdale.fr
"""
try:
    from datetime import datetime
    from PIL import Image
    from time import sleep
    import calendar, requests, json, pygame, os, sys, getopt
except:
    print "Dependencies error. Please read README, installation notes."
    exit()


class edt:

    def __init__(self, args):
        self.opt = False
        self.date = datetime.now()
        self.day = calendar.weekday(self.date.year, self.date.month, self.date.day)
        if self.day < 5:
            self.args = args
            self.pdf = None
            self.path = args[2]
            self.config = self.getConfig()
            self.parseOpt(args[1:])

            self.checkFiles()
            self.parseConfig(self.config)
        else:
            print "There is no schedule today."

    def usage(self):
        print "============= Schedule Notify ==============\n"
        print "Usage : edt [options]"
        print "\nOptions (facultative): "
        print "\t-h or --help : Display this page"
        print "\t-s or --schoolyear : (1A/2A) Schoolyear to display. Will be save in config.py "
        print "\t-d or --day : The day (in relative than today) that the scheldule is query"
        print "\t-r or --resolution : Save and display for this resolution."
        print "\nExemples : "
        print "\tedt"
        print "\t\tThis will display the edt with saved config"
        print "\tedt -s 1A -d 1 -r 1920,1080"
        print "\t\tThis will display the 1A's scheldule for tomorrow in a resolution of 1920,1080\n\n"
        exit()


    def parseOpt(self, argv):

        try:
            options, remainder = getopt.getopt(argv, "p:s:d:r:h", [
                "path=",
                "schoolyear=",
                "day=",
                "resolution=",
                "help",
            ])
        except Exception, e:
            print "Error (%s)"%e
            self.usage()

        #print "OPTIONS : %s"%options
        #print "REMAINDER : %s"%remainder

        if remainder:
            self.usage()
        for opt, arg in options:
            if opt in ("-p", "--path"):
                if arg:
                    self.path = arg
                else:
                    self.usage()
            elif opt in ("-s", "--schoolyear"):
                self.opt = True
                if arg:
                    if arg == "1A" or arg == "2A":
                        self.config["annee"] = arg
                    else:
                        self.usage()
                else:
                    self.usage()
            elif opt in ("-d", "--day"):
                self.opt = True
                if arg:
                    ok = False
                    year = self.date.year
                    month = self.date.month
                    try:
                        jour = self.date.day + int(arg)
                    except:
                        self.usage()
                    while(not ok):
                        try:
                            self.date = datetime(year, month, jour)
                            self.day = (self.day+int(arg))%7
                            ok = True
                        except Exception, e:
                            print "Error (%s) "%e
                            month +=1
                            if month > 12:
                                year += 1
                                month -= 12
                            jour -= int(calendar.monthrange(year, month)[1])
                else:
                    self.usage()

                if self.day >= 5:
                    print "There is no schedule today."
                    exit()
            elif opt in ("-r", "--resolution"):
                self.opt = True
                if arg:
                    try:
                        w,h = arg.split(",")
                        w = int(w)
                        h = int(h)
                        if w > 800 and h > 600:
                            self.config["resolution"] = ",".join([str(w),str(h)])
                        else:
                            raise Exception("Resolution not valid")
                    except Exception, e:
                        print "Error(%s)"%e
                        self.usage()
                else:
                    self.usage()
            elif opt in ("-h", "--help"):
                self.usage()

    def checkFiles(self):

        try:
            conf = open(self.path+"config.py", "r")
            conf.close()
        except:
            print "Error. Try to create manualy config.py in root directory"
            exit()

        try:
            edt = open(self.path+"edt.pdf", "r")
            edt.close()
        except:
            print "PDF not found. Downloading.."
            self.getPDF(self.date)


    def createImg(self,weekday):
        try:
            with Image.open(self.path+"edt.png") as img:
                x,y = 145, 19+(227*weekday)
                x2,y2 = 1644, 246+(227*weekday)
                rect = (x,y,x2,y2)
                region = img.crop(rect)
                region.save(self.path+"tmp.png", "PNG")
        except Exception, e:
            print "Error : %s"%e
            print "Error parsing img. Please try again."



    def pdfToPng(self):
        os.system("pdfimages -png "+self.path+"edt.pdf "+self.path+"edt")
        os.system("mv "+self.path+"edt-000.png "+self.path+"edt.png")

    def display(self):

        try:
            img = open(self.path+"edt.png", "r")
            img.close()
        except:
            print "Png not found. Generating..."
            self.pdfToPng()


        resolution = [int(i) for i in self.config["resolution"].split(",")]
        screenSize = int(resolution[0]*0.8), int(resolution[1]*0.2)
        windowPos = int((resolution[0]-screenSize[0])/2),int((resolution[1]-screenSize[1])*0.05)
        self.createImg(self.day)

        os.environ['SDL_VIDEO_WINDOW_POS'] = ",".join([str(i) for i in windowPos])
        pygame.init()

        pygame.event.set_blocked(pygame.MOUSEMOTION)
        pygame.event.set_blocked(pygame.ACTIVEEVENT)

        edt = pygame.image.load(self.path+"tmp.png")
        initImgSize = edt.get_width(), edt.get_height()
        edt = pygame.transform.smoothscale(edt, screenSize)
        imgSize = edt.get_width(), edt.get_height()

        screen = pygame.display.set_mode(screenSize, pygame.NOFRAME)
        screen.blit(edt, (0,0))

        minutes = self.date.hour * 60 + self.date.minute
        if minutes > 480 and minutes < 1080:
            x = 188 + (118.0/60.0 * (minutes-480))
            x /= float(initImgSize[0])/imgSize[0]
            pygame.draw.line(screen, (255,0,0), (x,0),(x,edt.get_height()), 2)

        pygame.display.flip()
        run = True
        while run:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                pygame.quit()
                run = False
                os.system("rm "+self.path+"tmp.png")

    def getWeekFirstDay(self, date):
        weekList = calendar.Calendar().monthdatescalendar(date.year, date.month)
        for week in weekList:
            if week[0].month == date.month and week[0].day > date.day - 7:
                return week[0]
        return weekList[-1][0]

    def getConfig(self):
        try:
            config = open(self.path+"config.py", "r")
            js = json.load(config)
            config.close()
            return js
        except Exception, e:
            try:
                pygame.init()
                content = json.dumps({
                    'year' : self.date.year,
                    'month' : self.date.month,
                    'day' : str(self.getWeekFirstDay(self.date).day),
                    'annee' : '2A',
                    'resolution' : ",".join([str(pygame.display.Info().current_w),str(pygame.display.Info().current_h)]),
                    'path' : os.getcwd()
                })
                pygame.quit()

                config = open(self.path+"config.py", "w+")
                config.write(content)
                config.close()
                sleep(1)

                config = open(self.path+"config.py", "r")
                js = json.load(config)
                config.close()
                return js

            except Exception, e:
                print "Error( %s ). Couldn't open config.py file"%e
                exit()

    def parseConfig(self, config):
        day = self.getWeekFirstDay(self.date)
        try:
            if self.opt:
                print "Option have been set, reloading configuration.."
                os.system("rm "+self.path+"edt.pdf "+self.path+"edt.png")
                self.getPDF(self.date)
                self.display()
            elif config["year"] != day.year or config["month"] != day.month or config["day"] != day.day or config["annee"]:
                print "Saved pdf is outdated. Downloading newest..."
                self.getPDF(self.date)
                self.display()
            else:
                print "Saved pdf is up to date. Display..."
                self.display()
        except Exception, e:
            print "File config.py empty, Downloading new pdf..."
            self.getPDF(self.date)
            self.display()

    def saveConfig(self, date):
        try:
            content = json.dumps({
                'year' : date.year,
                'month' : date.month,
                'day' : date.day,
                'annee' : self.config['annee'],
                'resolution' : self.config['resolution'],
                'path' : self.config['path'],
            })
        except:
            pygame.init()
            content = json.dumps({
                'year' : date.year,
                'month' : date.month,
                'day' : date.day,
                'annee' : '2A',
                'resolution' : ",".join([str(pygame.display.Info().current_w),str(pygame.display.Info().current_h)]),
                'path' : '/opt/edt/'
            })
            pygame.quit()
        config = open(self.path+"config.py", "w+")
        config.write(content)
        config.close()
        self.config = self.getConfig()

    def savePDF(self, content):
        pdf = open(self.path+"edt.pdf", "w+")
        pdf.write(content)
        pdf.close()

    def getPDF(self, date):
        date = self.getWeekFirstDay(date)
        url = "http://www.iutc3.unicaen.fr/c3/DépartementInformatique/OrganisationEtEmploisDuTemps20162017?action=AttachFile&do=get&target=edtInfo{0}{1}{2}{3}.pdf".format(self.config["annee"], date.year, date.month, date.day)
        try:
            req = requests.get(url)
            if "<!DOCTYPE " in req.content:
                print "Error, scheldule not online"
                exit()
            self.savePDF(req.content)
            self.saveConfig(date)
        except Exception, e:
            print "Error (%s). Please check you're internet connection"%e
            exit()


if __name__ == "__main__":
    edt = edt(sys.argv)
