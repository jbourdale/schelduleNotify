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
    import calendar, requests, json, pygame, os, sys
except:
    print "Dependencies error. Please read README, installation notes."
    exit()


class edt:

    def __init__(self, path):
        self.path = path
        print path
        self.date = datetime.now()
        self.day = calendar.weekday(self.date.year, self.date.month, self.date.day)
        if self.day < 5:
            self.pdf = None
            self.config = self.getConfig()
            self.checkFiles()
            self.parseConfig(self.config)
        else:
            print "There is no schedule today."

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

        edt = pygame.image.load(self.path+"tmp.png")
        edt = pygame.transform.smoothscale(edt, screenSize)

        screen = pygame.display.set_mode(screenSize, pygame.NOFRAME)

        #screen.blit(edt, (0,0), displayZone)
        screen.blit(edt, (0,0))
        pygame.display.flip()
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    pygame.quit()
                    run = False
                    os.system("rm "+self.path+"tmp.png")

    def getWeekFirstDay(self, date):
        weekList = calendar.Calendar().monthdatescalendar(date.year, date.month)
        for week in weekList:
            if week[0].month == date.month and week[0].day > date.day:
                return week[0]
                break
        return week[len(weekList)-1]

    def getConfig(self):
        try:
            config = open(self.path+"config.py", "r")
            return json.load(config)
            config.close()
        except Exception, e:
            try:
                config = open(self.path+"config.py", "w+")
                config.close()
                return None
            except:
                print "Error. Couldn't open config.py file"
                exit()

    def parseConfig(self, config):
        day = self.getWeekFirstDay(self.date)
        try:
            if config["year"] != day.year or config["month"] != day.month or config["day"] != day.day:
                print "Saved pdf is outdated. Downloading newest..."
                self.getPDF(self.date)
            else:
                print "Saved pdf is up to date. Display..."
                self.display()

        except Exception, e:
            print "File config.py empty, Downloading new pdf..."
            self.getPDF(self.date)

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

        config = open(self.path+"config.py", "w+")
        config.write(content)
        config.close()
        self.config = self.getConfig()

    def savePDF(self, content):
        pdf = open(self.path+"edt.pdf", "w+")
        pdf.write(content)
        pdf.close()

    def getPDF(self, date):
        print self.config
        date = self.getWeekFirstDay(date)
        url = "http://www.iutc3.unicaen.fr/c3/DépartementInformatique/OrganisationEtEmploisDuTemps20162017?action=AttachFile&do=get&target=edtInfo{0}{1}{2}{3}.pdf".format(self.config["annee"], date.year, date.month, date.day)
        try:
            req = requests.get(url)
            self.savePDF(req.content)
            self.saveConfig(date)
        except Exception, e:
            print "Error (%s). Please check you're internet connection"%e
            exit()


if __name__ == "__main__":
    edt = edt(sys.argv[1])
