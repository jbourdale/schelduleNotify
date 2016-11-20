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
    import calendar, requests, json, pygame, os
except:
    print "Dependencies error. Please read README"
    exit()


class edt:

    def __init__(self):
        self.date = datetime.now()
        self.day = calendar.weekday(self.date.year, self.date.month, self.date.day)
        self.day = 3
        if self.day < 5:
            self.pdf = None
            self.config = self.getConfig()
            self.checkFiles()
            self.parseConfig(self.config)
        else:
            print "There is no schedule today."

    def checkFiles(self):

        try:
            conf = open("config.py", "r")
            conf.close()
        except:
            print "Error. Try to create manualy config.py in root directory"
            exit()
        try:
            edt = open("edt.pdf", "r")
            edt.close()
        except:
            print "PDF not found. Downloading.."
            self.getPDF(self.date)

    def createImg(self,weekday):
        try:
            with Image.open("edt.png") as img:
                x,y = 145, 19+(227*weekday)
                x2,y2 = 1644, 246+(227*weekday)
                rect = (x,y,x2,y2)
                region = img.crop(rect)
                region.save("tmp.png", "PNG")
        except Exception, e:
            print "Error : %s"%e
            print "Error parsing img. Please try again."



    def pdfToPng(self):
        os.system("pdfimages -png edt.pdf edt")
        os.system("mv edt-000.png edt.png")

    def display(self):

        try:
            img = open("edt.png", "r")
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

        edt = pygame.image.load("tmp.png")
        edt = pygame.transform.smoothscale(edt, screenSize)

        """
        w,h = edt.get_size()
        ratioW = float(w)/screenSize[0]
        ratioH = 227.0/screenSize[1]
        print "ratioW : %s"%ratioW
        print "ratioH : {0} / {1} = {2}".format(227, screenSize[1], ratioH)

        size = width, height = int(w/ratioW), 1000
        print "size : %s"%[str(i) for i in size]
        #image de base => 19
        x = 19*ratioH + (235*ratioH * self.day)
        displayZone = pygame.Rect(60*0.8, x, 1500*0.8, 250*ratioH)
        """

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
                    os.system("rm tmp.png")

    def getWeekFirstDay(self, date):
        weekList = calendar.Calendar().monthdatescalendar(date.year, date.month)
        for week in weekList:
            if week[0].month == date.month and week[0].day > date.day:
                return week[0]
                break
        return week[len(weekList)-1]

    def getConfig(self):
        try:
            config = open("config.py", "r")
            return json.load(config)
            config.close()
        except Exception, e:
            try:
                config = open("config.py", "w+")
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
            })
        except:
            pygame.init()
            content = json.dumps({
                'year' : date.year,
                'month' : date.month,
                'day' : date.day,
                'annee' : '2A',
                'resolution' : ",".join([str(pygame.display.Info().current_w),str(pygame.display.Info().current_h)]),
            })

        config = open("config.py", "w+")
        config.write(content)
        config.close()
        self.config = self.getConfig()

    def savePDF(self, content):
        pdf = open("edt.pdf", "w+")
        pdf.write(content)
        pdf.close()

    def getPDF(self, date):
        date = self.getWeekFirstDay(date)
        url = "http://www.iutc3.unicaen.fr/c3/DépartementInformatique/OrganisationEtEmploisDuTemps20162017?action=AttachFile&do=get&target=edtInfo2A{0}{1}{2}.pdf".format(date.year, date.month, date.day)
        try:
            req = requests.get(url)
            self.savePDF(req.content)
            self.saveConfig(date)
        except Exception, e:
            print "Error (%s). Please check you're internet connection"%e
            exit()


if __name__ == "__main__":
    edt = edt()
