from cmu_112_graphics import *
from tkinter import *
from PIL import ImageDraw
import random, math, string, pygame
pygame.mixer.init()

## Citation: Superclass 'Mode' has been inherited from cmu_112_graphics

#PIL (Python Image Library) import imagedraw

# Make explanation mode for both combustion and titration
class StartMode(Mode):
    def appStarted(mode):
        mode.background = mode.loadImage('images/background.jpg')
        mode.background = mode.scaleImage(mode.background,0.5)
        mode.buttons = []
        mode.buttons.append(Button('Combustion',mode.width/4,mode.height/2,mode.width/5,mode.height/5))
        mode.buttons.append(Button('Titration',mode.width*3/4,mode.height/2,mode.width/5,mode.height/5))
        mode.music = pygame.mixer.Sound('sounds/start.ogg')
        mode.select = pygame.mixer.Sound('sounds/select.ogg')

    def mousePressed(mode,event):
        for button in mode.buttons:
            if (button.x-button.width/2 <= event.x <= button.x+button.width/2) and \
            (button.y-button.height/2 <= event.y <= button.y+button.height/2):
                if button.name == 'Combustion':
                    mode.music.stop()
                    mode.select.play()
                    mode.app.setActiveMode(mode.app.combustionMode)
                if button.name == 'Titration':
                    mode.music.stop()
                    mode.select.play()
                    mode.app.setActiveMode(mode.app.acidBaseMode)

    def keyPressed(mode,event):
        if event.key == 'h':
            mode.app.setActiveMode(mode.app.helpMode)

    def redrawAll(mode,canvas):
        mode.music.play()
        canvas.create_image(mode.width/2,mode.height/2,image = ImageTk.PhotoImage(mode.background))
        canvas.create_text(mode.width/2,mode.height*0.2,text = 'Welcome to Virtual Lab 42',font = ('verdana','24','bold'),fill = 'white')
        canvas.create_text(mode.width/2,mode.height*0.25,text = 'Select a mode below to begin',fill='white',font = ('verdana','12','bold'))
        for button in mode.buttons:
            button.drawButton(canvas)

class Button(StartMode):
    def __init__(self,name,x,y,width,height):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def drawButton(self,canvas):
        canvas.create_rectangle(self.x-self.width/2,self.y-self.height/2,self.x+self.width/2,self.y+self.height/2,fill='black',outline = 'white')
        canvas.create_text(self.x,self.y,text = self.name,fill='white',font = ('verdana','14','bold'))




class State(object):
    def __eq__(self, other):
        return (other != None) and self.__dict__ == other.__dict__
    def __hash__(self): return hash(str(self.__dict__))
    def __repr__(self): return str(self.__dict__)


class Rxnstate(State):
    def __init__(self,coefficientList):
        self.coefficientList = coefficientList


class BacktrackingPuzzleSolver(object):
    def solve(self, checkConstraints=True):
        self.moves = [ ]
        self.states = set()
        self.checkConstraints = checkConstraints
        self.solutionState = self.solveFromState(self.startState)
        return (self.moves, self.solutionState)

    def solveFromState(self, state):
        if state in self.states:
            return None
        self.states.add(state)
        if self.isSolutionState(state):
            return state
        else:
            for move in self.getLegalMoves(state):
                childState = self.doMove(state, move)
                if ((self.stateSatisfiesConstraints(childState)) or
                    (not self.checkConstraints)):
                    self.moves.append(move)
                    result = self.solveFromState(childState)
                    if result != None:
                        return result
                    self.moves.pop()
            return None



class Rxnsolver(BacktrackingPuzzleSolver):
    def __init__(self,hydrocarbon):
        self.hydrocarbon = hydrocarbon
        self.c = self.findCoefficient(self.hydrocarbon,'C')
        self.h = self.findCoefficient(self.hydrocarbon,'H')
        self.o = self.findCoefficient(self.hydrocarbon,'O')
        self.startState = Rxnstate([])


    def findCoefficient(self,chemical,element):
        if element not in chemical:
            return 0
        startIndex = chemical.index(element)+1
        coefficient = 0
        for x in chemical[startIndex:]:
            if x.isdigit():
                coefficient = coefficient*10 + int(x)
            elif x.isalpha():
                break
        if coefficient == 0:
            coefficient = 1
        return coefficient

    def stateSatisfiesConstraints(self, state):
        lastIndex = len(state.coefficientList)-1
        if lastIndex < 4:
            return True
        else:
            return False


    def isSolutionState(self,state):
        if len(state.coefficientList) !=  4:
            return False
        hydrocarbonCount,O2Count,CO2Count,H2OCount = state.coefficientList
        cBalance = hydrocarbonCount*self.c - CO2Count
        hBalance = hydrocarbonCount*self.h - 2*H2OCount
        oBalance = hydrocarbonCount*self.o + 2*O2Count - 2*CO2Count - H2OCount
        if cBalance != 0 or hBalance != 0 or oBalance != 0:
            return False
        return True

    def getLegalMoves(self,state):
        moves = []
        for i in range(1,15):
            moves.append(i)
        return moves


    def doMove(self,state,move):
        newCoefficientList = state.coefficientList + [move]
        return Rxnstate(newCoefficientList)




class CombustionMode(Mode):
    def appStarted(mode):
        mode.chemicalsList = [Chemical('CH4','CH4'),Chemical('C2H6','CH3CH3'),
        Chemical('C3H8','CH3CH2CH3'),Chemical('C4H10','CH3CH2CH2CH3'),Chemical('CH4O','CH3OH1')]
        mode.chemButtons = []
        mode.rxnList = []
        mode.chemBoxWidth = mode.width/10
        mode.chemBoxHeight = mode.height/(len(mode.chemicalsList)*2)
        for i in range(len(mode.chemicalsList)):
            mode.chemButtons.append(Button(mode.chemicalsList[i].name,mode.width*0.3+mode.chemBoxWidth*i,
            mode.height/6,mode.chemBoxWidth,mode.chemBoxHeight))
        mode.buttons = []
        mode.buttons.append(Button('Molecular View',mode.width/2,mode.height*0.8,mode.width/10,mode.height/10))
        mode.buttons.append(Button('Back',mode.width*0.9,mode.height*0.9,mode.width/10,mode.height/10))
        mode.buttons.append(Button('What is Combustion?',mode.width/10,mode.height*0.9,mode.width/8,mode.height/10))
        mode.countError = False
        mode.background = mode.loadImage('images/grey.jpg')
        mode.select = pygame.mixer.Sound('sounds/select.ogg')
        mode.back = pygame.mixer.Sound('sounds/back.ogg')
        mode.click = pygame.mixer.Sound('sounds/click.ogg')



    def mousePressed(mode,event):
        mode.countError = False
        for button in mode.buttons:
            if (button.x-button.width/2 <= event.x <= button.x+button.width/2) and \
            (button.y-button.height/2 <= event.y <= button.y+button.height/2):
                if button.name == 'Molecular View':
                    if mode.app.chemicals == []:
                        mode.countError = True
                    else:
                        for chemical in mode.app.chemicals:
                            mode.app.HCDraw[chemical.name] = []
                            for i in range(24//len(mode.app.chemicals)):
                                x0 = random.randint(mode.width/6,mode.width-mode.width/5)
                                y0 = random.randint(mode.width/6,mode.height-mode.width/5)
                                dirx = random.randint(0,100)/100
                                diry = (1 - dirx**2)**0.5
                                if random.randint(0,1) == 0:
                                    dirx = -dirx
                                if random.randint(0,1) == 0:
                                    diry = -diry
                                mode.app.HCDraw[chemical.name].append(Hydrocarbon(chemical.name,chemical.codename,x0,y0,(dirx,diry)))
                        mode.app.setActiveMode(mode.app.cMoleculeMode)
                        mode.app.previousMode = mode.app.combustionMode
                        mode.select.play()
                if button.name == 'Back':
                    mode.app.chemicals = []
                    mode.app.setActiveMode(mode.app.startMode)
                    mode.app.previousMode = mode.app.combustionMode
                    mode.back.play()
                if '?' in button.name:
                    mode.app.setActiveMode(mode.app.cExplainMode)
                    mode.click.play()
        for button in mode.chemButtons:
            if (button.x-button.width/2 <= event.x <= button.x+button.width/2) and \
            (button.y-button.height/2 <= event.y <= button.y+button.height/2):
                chemicals = []
                for chemical in mode.app.chemicals:
                    chemicals.append(chemical.name)
                if button.name in chemicals:
                    for chemical in mode.chemicalsList:
                        if chemical.name == button.name:
                            mode.app.chemicals.remove(chemical)
                else:
                    for chemical in mode.chemicalsList:
                        if chemical.name == button.name:
                            if len(mode.app.chemicals) < 3:
                                mode.app.chemicals.append(chemical)
                            else:
                                mode.countError = True
                mode.click.play()

    def redrawAll(mode,canvas):
        canvas.create_image(mode.width/2,mode.height/2,image = ImageTk.PhotoImage(mode.background))
        if mode.countError == True:
            canvas.create_text(mode.width/2,mode.height*0.3,fill='white',text='Please select up to 3 hydrocarbons!',font = ('verdana','12','bold'))
        canvas.create_text(mode.width/6,mode.height/6,text='Hydrocarbons:',font = ('verdana','15','bold'))
        for button in mode.buttons:
            button.drawButton(canvas)
        for button in mode.chemButtons:
            button.drawButton(canvas)
        canvas.create_text(mode.width/2,mode.height/2,
        text=f'Hydrocarbons Selected: {mode.app.chemicals}',fill='white',font = ('verdana','20','bold'))

class Chemical(CombustionMode):
    def __init__(self,name,codename):
        self.name = name
        self.codename = codename

    def __repr__(self):
        return self.name




class CMoleculeMode(Mode):
    def appStarted(mode):
        mode.background = mode.loadImage('images/grey.jpg')
        mode.chemicals = mode.app.chemicals
        mode.elementDict = {'O':[7.3,'white'],'H':[3.7,'sky blue'],
        'C':[7.7,'black']}
        mode.margin = mode.width/6
        mode.O2 = []
        mode.products = []
        mode.addO2 = False
        mode.react = False
        mode.buttons = []
        mode.buttons.append(Button('React!',mode.width/2,mode.height/10,mode.width/10,mode.height/10))
        mode.buttons.append(Button('Back',mode.width*0.9,mode.height*0.9,mode.width/10,mode.height/10))
        mode.buttons.append(Button('Press to add O2',mode.width*0.65,mode.height/10,mode.width/10,mode.height/10))
        mode.buttons.append(Button('Freeze Screen',mode.width*0.8,mode.height/10,mode.width/10,mode.height/10))
        mode.concentrations = {}
        mode.reactionRange = mode.width/10
        mode.clickAdd = False
        mode.clickAddPoint = None
        mode.freeze = False
        mode.back = pygame.mixer.Sound('sounds/back.ogg')
        mode.click = pygame.mixer.Sound('sounds/click.ogg')
        mode.success = pygame.mixer.Sound('sounds/success.ogg')
        mode.played = 0


    def mousePressed(mode,event):
        for button in mode.buttons:
            if (button.x-button.width/2 <= event.x <= button.x+button.width/2) and \
            (button.y-button.height/2 <= event.y <= button.y+button.height/2):
                if 'reeze' in button.name:
                    if mode.freeze == False:
                        mode.freeze = True
                        button.name = 'Unfreeze'
                    else:
                        mode.freeze = False
                        button.name = 'Freeze Screen'
                    mode.click.play()
                if 'React' in button.name:
                    if mode.react == False:
                        mode.react = True
                        button.name = 'Stop Reacting'
                    else:
                        mode.react = False
                        button.name = 'React!'
                    mode.click.play()
                if 'add' in button.name:
                    if mode.addO2 == False:
                        button.name = 'Stop adding O2'
                        mode.addO2 = True
                    else:
                        button.name = 'Press to add O2'
                        mode.addO2 = False
                    mode.click.play()
                if button.name == 'Back':
                    mode.app.chemicals = []
                    mode.app.HCDraw = dict()
                    mode.O2 = []
                    mode.products = []
                    mode.played = 0
                    for button in mode.buttons:
                        if 'React' in button.name:
                            button.name = 'React!'
                        if 'O2' in button.name:
                            button.name = 'Press to add O2'
                    mode.react = False
                    mode.addO2 = False
                    mode.freeze = False
                    mode.app.setActiveMode(mode.app.previousMode)
                    mode.back.play()
        if mode.addO2 and (mode.margin <= event.x <= mode.width-mode.margin) and \
        (mode.margin <= event.y <= mode.height-mode.margin):
            mode.clickAdd = True
            mode.clickAddPoint = (event.x,event.y)
        else:
            mode.clickAdd = False
            mode.clickAddPoint = None

    def mouseDragged(mode,event):
        if mode.clickAdd == True:
            if (mode.margin <= event.x <= mode.width-mode.margin) and \
            (mode.margin <= event.y <= mode.height-mode.margin):
                mode.clickAddPoint = (event.x,event.y)
            else:
                mode.clickAdd = False
                mode.clickAddPoint = None

    def mouseReleased(mode,event):
        mode.clickAdd = False
        mode.clickAddPoint = None


    def getCombustionReaction(mode,hydrocarbon):
        (moves,solution) = Rxnsolver(hydrocarbon).solve()
        if solution == None:
            return None
        else:
            return solution.coefficientList


    def checkReaction1(mode,hcname,size,reaction):
        hclist = mode.app.HCDraw[hcname]
        O2React, CO2Produce, H2OProduce = reaction
        rRange = size*3
        reactingHC = []
        for hc in hclist:
            O2inRange = []
            for O2 in mode.O2:
                dist = ((hc.cx-O2.cx)**2+(hc.cy-O2.cy)**2)**0.5
                if dist <= rRange:
                    O2inRange.append(O2)
            if O2React <= len(O2inRange):
                for i in range(O2React):
                    mode.O2.remove(O2inRange[i])
                for j in range(CO2Produce):
                    x0,y0 = hc.cx,hc.cy
                    dirx = random.randint(0,100)/100
                    diry = (1 - dirx**2)**0.5
                    if random.randint(0,1) == 0:
                        dirx = -dirx
                    if random.randint(0,1) == 0:
                        diry = -diry
                    mode.products.append(Product('CO2','CO2',x0,y0,(dirx,diry)))
                for k in range(H2OProduce):
                    x0,y0 = hc.cx,hc.cy
                    dirx = random.randint(0,100)/100
                    diry = (1 - dirx**2)**0.5
                    if random.randint(0,1) == 0:
                        dirx = -dirx
                    if random.randint(0,1) == 0:
                        diry = -diry
                    mode.products.append(Product('H2O','OH2',x0,y0,(dirx,diry)))
                reactingHC.append(hc)
        for hc in reactingHC:
            hclist.remove(hc)


    def checkReaction2(mode,hcname,size,reaction):
        hclist = mode.app.HCDraw[hcname]
        O2React, CO2Produce, H2OProduce = reaction
        rRange = size*3
        reactingHC = []
        if len(hclist) == 2:
            hc1,hc2 = hclist[0], hclist[1]
            xDist = hc2.cx-hc1.cx
            yDist = hc2.cy-hc1.cy
            xyRatio = abs(yDist/xDist)
            hc1.dirx = (1/((xyRatio**2)+1))**0.5
            hc1.diry = hc1.dirx*xyRatio
            if xDist < 0:
                hc1.dirx *= -1
            if yDist < 0:
                hc1.diry *= -1
            hc2.dirx, hc2.diry = -hc1.dirx, -hc1.diry
        for i in range(len(hclist)):
            hc1 = hclist[i]
            HCinRange = []
            O2inRange = []
            if hc1 not in reactingHC:
                for j in range(i+1,len(hclist)):
                    hc2 = hclist[j]
                    if hc2 not in reactingHC:
                        HCdist = ((hc1.cx-hc2.cx)**2+(hc1.cy-hc2.cy)**2)**0.5
                        if HCdist <= rRange:
                            HCinRange.append(hc2)
                if len(HCinRange) > 0:
                    for O2 in mode.O2:
                        dist = ((hc1.cx-O2.cx)**2+(hc1.cy-O2.cy)**2)**0.5
                        if dist <= rRange:
                            O2inRange.append(O2)
                if O2React <= len(O2inRange) and len(HCinRange) > 0:
                    hc2 = HCinRange[0]
                    centerx,centery = (hc1.cx+hc2.cx)/2,(hc1.cy+hc2.cy)/2
                    for i in range(O2React):
                        mode.O2.remove(O2inRange[i])
                    for j in range(CO2Produce):
                        x0,y0 = centerx,centery
                        dirx = random.randint(0,100)/100
                        diry = (1 - dirx**2)**0.5
                        if random.randint(0,1) == 0:
                            dirx = -dirx
                        if random.randint(0,1) == 0:
                            diry = -diry
                        mode.products.append(Product('CO2','CO2',x0,y0,(dirx,diry)))
                    for k in range(H2OProduce):
                        x0,y0 = centerx,centery
                        dirx = random.randint(0,100)/100
                        diry = (1 - dirx**2)**0.5
                        if random.randint(0,1) == 0:
                            dirx = -dirx
                        if random.randint(0,1) == 0:
                            diry = -diry
                        mode.products.append(Product('H2O','OH2',x0,y0,(dirx,diry)))
                    reactingHC.append(hc1)
                    reactingHC.append(hc2)
        for hc in reactingHC:
            hclist.remove(hc)



    def checkWallCollision(mode):
        total = mode.O2 + mode.products
        for key in mode.app.HCDraw:
            total.extend(mode.app.HCDraw[key])
        for chemical in total:
            if chemical.cx < mode.margin or chemical.cx > mode.width-mode.margin:
                chemical.dirx *= -1
            if chemical.cy < mode.margin or chemical.cy > mode.height-mode.margin:
                chemical.diry *= -1


    def getConcentrations(mode):
        concentrations = dict()
        for chemical in mode.app.chemicals:
            concentrations[chemical.name] = 0
        total = mode.O2 + mode.products
        for key in mode.app.HCDraw:
            total.extend(mode.app.HCDraw[key])
        for chemical in total:
            concentrations[chemical.name] = concentrations.get(chemical.name,0) + 1/len(total)
        for chemical in concentrations:
            concentrations[chemical] = (concentrations[chemical]//0.001)/1000
        return concentrations

    def getMoleculeSize(mode,composition):
        if composition == []:
            return 0
        else:
            if type(composition[0]) == str:
                atomSize = mode.elementDict[composition[0]][0]
                return atomSize + mode.getMoleculeSize(composition[1:])
            if type(composition[0]) == list:
                return mode.getMoleculeSize(composition[0])

    def checkReactionComplete(mode,chemical):
        concentrations = mode.getConcentrations()
        concentration = concentrations[chemical.name]
        if concentration == 0:
            return True
        else:
            return False

    def checkAllReactionsComplete(mode):
        hydrocarbons = []
        for chemical in mode.app.chemicals:
            if 'C' in chemical.name:
                hydrocarbons.append(chemical)
        for hydrocarbon in hydrocarbons:
            if not mode.checkReactionComplete(hydrocarbon):
                return False
        return True

    def timerFired(mode):
        if not mode.freeze and not mode.checkAllReactionsComplete():
            if mode.addO2 == True:
                if mode.clickAdd == True:
                    x0,y0 = mode.clickAddPoint
                else:
                    x0 = random.randint(mode.margin,mode.width-mode.margin)
                    y0 = random.randint(mode.margin,mode.height-mode.margin)
                dirx = random.randint(0,100)/100
                diry = (1 - dirx**2)**0.5
                if random.randint(0,1) == 0:
                    dirx = -dirx
                if random.randint(0,1) == 0:
                    diry = -diry
                mode.O2.append(O2(x0,y0,(dirx,diry)))
            mode.checkWallCollision()
            total = mode.O2 + mode.products
            for key in mode.app.HCDraw:
                total.extend(mode.app.HCDraw[key])
            for molecule in total:
                composition = mode.getMolecularCompositionByList(molecule.codename)
                size = mode.getMoleculeSize(composition)
                molecule.cx += molecule.dirx*(100/size)
                molecule.cy += molecule.diry*(100/size)
            if mode.react == True:
                for chemical in mode.app.chemicals:
                    HCReact, O2React, CO2Produce, H2OProduce = mode.getCombustionReaction(chemical.name)
                    composition = mode.getMolecularCompositionByList(chemical.codename)
                    size = mode.getMoleculeSize(composition)
                    if HCReact == 1:
                        mode.checkReaction1(chemical.name,size,(O2React,CO2Produce,H2OProduce))
                    else:
                        mode.checkReaction2(chemical.name,size,(O2React,CO2Produce,H2OProduce))
            mode.concentrations = mode.getConcentrations()




    def getMolecularCompositionByList(mode,codename):
        if codename == '':
            return []
        if len(codename) == 1:
            return [codename]
        else:
            result = []
            if codename[1] in string.ascii_lowercase:
                result.append(codename[0:2])
                result.extend(mode.getMolecularCompositionByList(codename[2:]))
            elif codename[1] in string.ascii_uppercase:
                result.append(codename[0])
                result.extend(mode.getMolecularCompositionByList(codename[1:]))
            else:
                current = [codename[0]]*int(codename[1])
                current.extend(mode.getMolecularCompositionByList(codename[2:]))
                result.append(current)
            return result


    def drawMoleculeByName(mode,canvas,molecule,x,y,lastRadius = 0,\
    firstAtom = True):
        atomCount = 0
        for atom in molecule:
            if type(atom) == str:
                atomCount += 1
        for i in range(len(molecule)):
            if type(molecule[i]) == str:
                angle = 2*math.pi*(i/atomCount)
                r,color = mode.elementDict[molecule[i]]
                if firstAtom == True:
                    canvas.create_oval(x-r,y-r,x+r,y+r,fill=color)
                else:
                    dx = (lastRadius + r)*math.cos(angle)
                    dy = (lastRadius + r)*math.sin(angle)
                    canvas.create_oval(x+dx-r,y+dy-r,x+dx+r,y+dy+r,fill=color)
            elif type(molecule[i]) == list:
                angle = 2*math.pi*(i-1/atomCount)
                r = mode.elementDict[molecule[i-1]][0]
                dx = (lastRadius + r)*math.cos(angle)
                dy = (lastRadius + r)*math.sin(angle)
                if firstAtom == True:
                    mode.drawMoleculeByName(canvas,molecule[i],x,y,r,False)
                else:
                    mode.drawMoleculeByName(canvas,molecule[i],x+dx,y+dy,r,False)

    def drawEquation(mode,canvas):
        chemicals = mode.app.chemicals
        i = 0
        canvas.create_text(mode.width/8,mode.height*0.85,text = 'Reactions:',font = ('verdana','16','bold'))
        for chemical in chemicals:
            HCReact, O2React, CO2Produce, H2OProduce = mode.getCombustionReaction(chemical.name)
            if not mode.checkReactionComplete(chemical):
                canvas.create_text(mode.width*0.27,mode.height*0.85+mode.height/30*i,text = \
                f'{HCReact}{chemical.name} + {O2React}O2 → {CO2Produce}CO2 + {H2OProduce}H2O',font = ('verdana','12','bold'))
            else:
                canvas.create_text(mode.width*0.27,mode.height*0.85+mode.height/30*i,text = \
                f'{HCReact}{chemical.name} + {O2React}O2 → {CO2Produce}CO2 + {H2OProduce}H2O (Complete)',font = ('verdana','12','bold'))
            i += 1

    def redrawAll(mode,canvas):
        canvas.create_image(mode.width/2,mode.height/2,image = ImageTk.PhotoImage(mode.background))
        total = []
        for key in mode.app.HCDraw:
            total.extend(mode.app.HCDraw[key])
        for molecule in mode.products:
            composition = mode.getMolecularCompositionByList(molecule.codename)
            mode.drawMoleculeByName(canvas,composition,molecule.cx,molecule.cy)
        for molecule in mode.O2:
            composition = mode.getMolecularCompositionByList(molecule.codename)
            mode.drawMoleculeByName(canvas,composition,molecule.cx,molecule.cy)
        for molecule in total:
            composition = mode.getMolecularCompositionByList(molecule.codename)
            mode.drawMoleculeByName(canvas,composition,molecule.cx,molecule.cy)
        for button in mode.buttons:
            button.drawButton(canvas)
        i = 0
        canvas.create_text(mode.width*0.13,mode.height*0.06 + mode.height/30*i,text = 'Concentrations:',font = ('verdana','16','bold'))
        for chemical in mode.concentrations:
            concentration = mode.concentrations[chemical]
            canvas.create_text(mode.width/4,mode.height*0.06 + mode.height/30*i,text = f'{chemical}: {concentration}',font = ('verdana','12','bold'))
            i += 1
        mode.drawEquation(canvas)
        if mode.checkAllReactionsComplete():
            if mode.played == 0:
                mode.success.play()
                mode.played += 1
            canvas.create_rectangle(mode.width*0.4,mode.height*0.4,mode.width*0.6,mode.height*0.6,fill = 'springgreen')
            canvas.create_text(mode.width/2,mode.height/2,text = 'All Reactions Complete',font = ('verdana','14','bold'))



class Hydrocarbon(CMoleculeMode):
    def __init__(self,name,codename,x,y,movementDirection):
        self.name = name
        self.codename = codename
        self.cx = x
        self.cy = y
        self.dirx, self.diry = movementDirection
        self.O2inRange = []


class O2(CMoleculeMode):
    def __init__(self,x,y,movementDirection):
        self.name = 'O2'
        self.codename = 'OO1'
        self.cx = x
        self.cy = y
        self.dirx, self.diry = movementDirection

class Product(CMoleculeMode):
    def __init__(self,name,codename,x,y,movementDirection):
        self.name = name
        self.codename = codename
        self.cx = x
        self.cy = y
        self.dirx, self.diry = movementDirection


class CExplainMode(Mode):
    def appStarted(mode):
        mode.background = mode.loadImage('images/grey.jpg')
        mode.overview = 'Combustion is a chemical process in which a hydrogen-carbon-based substance (called hydrocarbons) reacts \n\nrapidly with oxygen to produce carbon dioxide(CO2) and water vapor(H2O). In this virtual lab, you can simulate\n\nsuch reactions interactively.'
        mode.guide = 'Here are some features of Combustion Mode.\n\n- Select at least one and up to three hydrocarbons and press the *Molecular View* button to begin the simulator.\n\n- In the simulator, press the *Press to Add O2* button to add O2 molecules.\n\n- While O2 is being added, you can press on the screen to place O2 molecules in the desired location.\n\n- Press the *React* button to see the combustion reactions occur!\n\n- You can also press the *Freeze Screen* button to freeze the screen during the simulation.'
        mode.back = pygame.mixer.Sound('sounds/back.ogg')


    def keyPressed(mode,event):
        mode.app.setActiveMode(mode.app.combustionMode)
        mode.back.play()

    def redrawAll(mode,canvas):
        canvas.create_image(mode.width/2,mode.height/2,image = ImageTk.PhotoImage(mode.background))
        canvas.create_text(mode.width/2,mode.height*0.1,text = 'What is Combustion?',font = 'verdana 24 bold italic')
        canvas.create_text(mode.width/2,mode.height*0.23,text = 'Overview', font = 'verdana 16 bold underline')
        canvas.create_text(mode.width/2,mode.height*0.33,text = f'{mode.overview}', font = 'verdana 14 bold')
        canvas.create_text(mode.width/2,mode.height*0.48,text = 'Virtual Lab Guide', font = 'verdana 16 bold underline')
        canvas.create_text(mode.width/2,mode.height*0.65,text = f'{mode.guide}', font = 'verdana 14 bold')
        canvas.create_text(mode.width/2,mode.height*0.9,text = '*Press any key to return*', font = 'verdana 12 bold')


class AcidBaseMode(Mode):
    def appStarted(mode):
        mode.background = mode.loadImage('images/grey.jpg')
        mode.acidtitButton = TitrationButton('Weak Acid - Strong Base',mode.width*0.3,mode.height/4-mode.height/20,mode.width/5,mode.height/8)
        mode.basetitButton = TitrationButton('Weak Base - Strong Acid',mode.width*0.7,mode.height/4-mode.height/20,mode.width/5,mode.height/8)
        mode.conButton = ConButton('Enter Titrant Concentration',mode.width*0.3,mode.height/2,mode.width/5,mode.height/8)
        mode.volButton = VolButton('Enter Unknown Solution Volume',mode.width*0.7,mode.height/2,mode.width/5,mode.height/8)
        mode.titrationModeButton = Button('Titrate!',mode.width/2,mode.height*0.8,mode.width/10,mode.height/10)
        mode.backButton = Button('Back',mode.width*0.9,mode.height*0.9,mode.width/10,mode.height/10)
        mode.guideButton = Button('What is Titration?',mode.width/10,mode.height*0.9,mode.width/8,mode.height/10)
        mode.buttons = [mode.acidtitButton,mode.basetitButton,mode.conButton,mode.volButton,mode.titrationModeButton,mode.backButton,mode.guideButton]
        mode.inputError = False
        mode.blankError = False
        mode.selectError = False
        mode.zeroError = False
        mode.select = pygame.mixer.Sound('sounds/select.ogg')
        mode.back = pygame.mixer.Sound('sounds/back.ogg')
        mode.click = pygame.mixer.Sound('sounds/click.ogg')


    def keyPressed(mode,event):
        if mode.inputError == True:
            mode.inputError = False
        if mode.conButton.enter == True:
            if event.key.isdigit():
                if mode.conButton.con == '':
                    mode.conButton.con = event.key
                elif len(mode.conButton.con) < 5:
                    mode.conButton.con += event.key
            elif event.key == 'Enter':
                mode.conButton.enter = False
            elif event.key == 'Delete':
                mode.conButton.con = mode.conButton.con[:-1]
            elif event.key == '.':
                if '.' not in mode.conButton.con and not mode.conButton.con == '':
                    if mode.conButton.con[-1].isdigit():
                        mode.conButton.con += event.key
            else:
                mode.inputError = True
        if mode.volButton.enter == True:
            if event.key.isdigit():
                if mode.volButton.vol == '':
                    mode.volButton.vol = event.key
                elif len(mode.volButton.vol) < 5:
                    mode.volButton.vol += event.key
            elif event.key == 'Enter':
                mode.volButton.enter = False
            elif event.key == 'Delete':
                mode.volButton.vol = mode.volButton.vol[:-1]
            elif event.key == '.':
                if '.' not in mode.volButton.vol and not mode.volButton.vol == '':
                    if mode.volButton.vol[-1].isdigit():
                        mode.volButton.vol += event.key
            else:
                mode.inputError = True


    def mousePressed(mode,event):
        if mode.blankError == True:
            mode.blankError = False
        if mode.inputError == True:
            mode.inputError = False
        if mode.selectError == True:
            mode.selectError = False
        if mode.zeroError == True:
            mode.zeroError = False
        conB = mode.conButton
        volB = mode.volButton
        acid = mode.acidtitButton
        base = mode.basetitButton
        TMB = mode.titrationModeButton
        back = mode.backButton
        guide = mode.guideButton
        if (acid.x-acid.width/2 <= event.x <= acid.x+acid.width/2) and \
        (acid.y-acid.height/2 <= event.y <= acid.y+acid.height/2):
            acid.select = True
            base.select = False
            mode.conButton.name = 'Enter Titrant(Base) Concentration'
            mode.volButton.name = 'Enter Unknown Solution(Acid) Volume'
            mode.click.play()
        if (base.x-base.width/2 <= event.x <= base.x+base.width/2) and \
        (base.y-base.height/2 <= event.y <= base.y+base.height/2):
            base.select = True
            acid.select = False
            mode.conButton.name = 'Enter Titrant(Acid) Concentration'
            mode.volButton.name = 'Enter Unknown Solution(Base) Volume'
            mode.click.play()
        if (conB.x-conB.width/2 <= event.x <= conB.x+conB.width/2) and \
        (conB.y-conB.height/2 <= event.y <= conB.y+conB.height/2):
            if acid.select == False and base.select == False:
                mode.selectError = True
            else:
                conB.con = ''
                conB.enter = True
            mode.click.play()
        else:
            conB.enter = False
        if (volB.x-volB.width/2 <= event.x <= volB.x+volB.width/2) and \
        (volB.y-volB.height/2 <= event.y <= volB.y+volB.height/2):
            if acid.select == False and base.select == False:
                mode.selectError = True
            else:
                volB.vol = ''
                volB.enter = True
            mode.click.play()
        else:
            volB.enter = False
        if (TMB.x-TMB.width/2 <= event.x <= TMB.x+TMB.width/2) and \
        (TMB.y-TMB.height/2 <= event.y <= TMB.y+TMB.height/2):
            mode.blank = []
            mode.zero = []
            if acid.select == False and base.select == False:
                mode.blank.append('Titration Type')
            if conB.con == '':
                mode.blank.append('Titrant Concentration')
            elif float(conB.con) == 0:
                mode.zero.append('Titrant Concentration')
            if volB.vol == '':
                mode.blank.append('Unknown Solution Volume')
            elif float(volB.vol) == 0:
                mode.zero.append('Unknown Solution Volume')
            if mode.blank == [] and mode.zero == []:
                mode.app.previousMode = mode.app.acidBaseMode
                unknownM = random.randint(100,1200)/1000
                titrantM = float(conB.con)
                unknownVol = float(volB.vol)
                target = unknownVol*unknownM/titrantM
                pinkRange = target/20
                answerMin = unknownM - 0.025
                answerMax = unknownM + 0.025
                conB.con = ''
                volB.vol = ''
                if acid.select == True:
                    acid.select = False
                    mode.app.titrationModeInit =\
                    ['acid',titrantM,unknownVol,unknownM,target,pinkRange,'azure',answerMin,answerMax]
                    mode.app.setActiveMode(mode.app.titrationMode)
                elif base.select == True:
                    base.select = False
                    mode.app.titrationModeInit =\
                    ['base',titrantM,unknownVol,unknownM,target,pinkRange,'maroon1',answerMin,answerMax]
                    mode.app.setActiveMode(mode.app.titrationMode)
                mode.select.play()
            elif mode.blank != []:
                mode.blankError = True
            else:
                mode.zeroError = True
        if (back.x-back.width/2 <= event.x <= back.x+back.width/2) and \
        (back.y-back.height/2 <= event.y <= back.y+back.height/2):
            conB.con = ''
            volB.vol = ''
            acid.select = False
            base.select = False
            mode.app.setActiveMode(mode.app.startMode)
            mode.app.previousMode = mode.app.acidBaseMode
            mode.back.play()
        if (guide.x-guide.width/2 <= event.x <= guide.x+guide.width/2) and \
        (guide.y-guide.height/2 <= event.y <= guide.y+guide.height/2):
            mode.app.setActiveMode(mode.app.tExplainMode)
            mode.click.play()



    def redrawAll(mode,canvas):
        canvas.create_image(mode.width/2,mode.height/2,image = ImageTk.PhotoImage(mode.background))
        if mode.zeroError == True:
            canvas.create_text(mode.width/2,mode.height*0.9,text = f'*Error* {mode.zero} cannot be zero!',font = 'verdana 12 bold')
        if mode.selectError == True:
            canvas.create_text(mode.width/2,mode.height*0.9,text = f'*Error* Please select a Titration Type!',font = 'verdana 12 bold')
        if mode.blankError == True:
            canvas.create_text(mode.width/2,mode.height*0.9,text = f'*Error* Please initialize {mode.blank}!',font = 'verdana 12 bold')
        if mode.inputError == True:
            canvas.create_text(mode.width/2,mode.height*0.7,text = '*Error* Please enter a number!')
        canvas.create_text(mode.width/2,mode.height/10,text = 'Select Titration Type',font = ('verdana','16','bold'))
        canvas.create_text(mode.width/2,mode.height*0.4,text = 'Initialize Variables',font = ('verdana','16','bold'))
        for button in mode.buttons:
            button.drawButton(canvas)




class ConButton(AcidBaseMode):
    def __init__(self,name,x,y,width,height):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.con = ''
        self.enter = False
        self.color = 'springgreen'


    def drawButton(self,canvas):
        if self.enter == False:
            canvas.create_rectangle(self.x-self.width/2,self.y-self.height/2,self.x+self.width/2,self.y+self.height/2,fill='black',outline = 'white')
            canvas.create_text(self.x,self.y,text = self.name,fill='white',font = ('verdana','12','bold'))

        else:
            canvas.create_rectangle(self.x-self.width/2,self.y-self.height/2,self.x+self.width/2,self.y+self.height/2,fill=self.color)
            canvas.create_text(self.x,self.y,text = self.name,fill='black',font = ('verdana','12','bold'))
        canvas.create_text(self.x,self.y+self.height,text = f'Titrant Concentration: {self.con}(M)',font = ('verdana','14','bold'))


class VolButton(AcidBaseMode):
    def __init__(self,name,x,y,width,height):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vol = ''
        self.enter = False
        self.color = 'springgreen'

    def drawButton(self,canvas):
        if self.enter == False:
            canvas.create_rectangle(self.x-self.width/2,self.y-self.height/2,self.x+self.width/2,self.y+self.height/2,fill='black',outline = 'white')
            canvas.create_text(self.x,self.y,text = self.name,fill='white',font = ('verdana','12','bold'))

        else:
            canvas.create_rectangle(self.x-self.width/2,self.y-self.height/2,self.x+self.width/2,self.y+self.height/2,fill=self.color)
            canvas.create_text(self.x,self.y,text = self.name,fill='black',font = ('verdana','12','bold'))
        canvas.create_text(self.x,self.y+self.height,text = f'Unknown Solution Volume: {self.vol}(L)',font = ('verdana','14','bold'))

class TitrationButton(AcidBaseMode):
    def __init__(self,name,x,y,width,height):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.select = False
        self.color = 'springgreen'


    def drawButton(self,canvas):
        if self.select == False:
            canvas.create_rectangle(self.x-self.width/2,self.y-self.height/2,self.x+self.width/2,self.y+self.height/2,fill='black',outline = 'white')
            canvas.create_text(self.x,self.y,text = self.name,fill='white',font = ('verdana','14','bold'))
        else:
            canvas.create_rectangle(self.x-self.width/2,self.y-self.height/2,self.x+self.width/2,self.y+self.height/2,fill=self.color)
            canvas.create_text(self.x,self.y,text = self.name,fill='black',font = ('verdana','14','bold'))



class TitrationMode(Mode):
    def appStarted(mode):
        mode.background = mode.loadImage('images/grey.jpg')
        mode.type,mode.titrantM,mode.unknownVol,mode.unknownM,mode.target,mode.pinkRange,\
        mode.color,mode.answerMin,mode.answerMax=mode.app.titrationModeInit
        mode.go = False
        mode.drop = False
        mode.dropAdded = False
        mode.tempPink = False
        mode.titrantH = mode.height/8
        mode.added = 0.000
        mode.epsilon = 0.005
        mode.pinkCount = 0
        mode.drops = []
        mode.flask = mode.loadImage('images/flask.png')
        mode.flask = mode.scaleImage(mode.flask,0.4)
        mode.burette = mode.loadImage('images/burette.png')
        mode.burette = mode.scaleImage(mode.burette,0.5)
        mode.dropButton = DropButton('Drop',mode.width*0.4,mode.height/2,mode.width/30)
        mode.goButton = DropButton('Open Valve',mode.width*0.4,mode.height/3,mode.width/30)
        mode.reset = ResetButton('Reset',mode.width*0.65,mode.height*0.8,mode.width/50)
        mode.ansButton = AnswerButton(mode.width*0.857,mode.height/2,mode.width/15,mode.height/30)
        mode.backButton = Button('Back',mode.width*0.9,mode.height*0.9,mode.width/10,mode.height/10)
        mode.hintButton = Button('Hint',mode.width*0.1,mode.height/10,mode.width/10,mode.height/10)
        mode.inputError = False
        mode.wrong = False
        mode.correct = False
        mode.hint = False
        mode.noneError = False
        mode.dropSound = pygame.mixer.Sound('sounds/drop.ogg')
        mode.flowSound = pygame.mixer.Sound('sounds/open valve.ogg')
        mode.back = pygame.mixer.Sound('sounds/back.ogg')
        mode.click = pygame.mixer.Sound('sounds/click.ogg')
        mode.success = pygame.mixer.Sound('sounds/success.ogg')
        mode.played = 0



    def timerFired(mode):
        if mode.added == 0:
            if mode.type == 'acid':
                mode.color = 'azure'
            else:
                mode.color = 'maroon1'
            mode.type,mode.titrantM,mode.unknownVol,mode.unknownM,mode.target,mode.pinkRange,\
            mode.color,mode.answerMin,mode.answerMax=mode.app.titrationModeInit
        if mode.dropAdded == True:
            mode.dropAdded = False
        if mode.tempPink == True:
            if mode.pinkCount > 8:
                mode.pinkCount = 0
                if mode.type == 'acid':
                    mode.color = 'azure'
                else:
                    mode.color = 'maroon1'
                mode.tempPink = False
            else:
                mode.color = 'orchid1'
                mode.pinkCount += 1
        if mode.titrantH >= mode.height*0.4:
            mode.titrantH = mode.height/8
        if mode.go and mode.titrantH < mode.height*0.4:
            mode.titrantH += 1
            mode.added += 0.005
        for drop in mode.drops:
            drop.y += 20
            if drop.y >= mode.height*0.8:
                mode.drops.remove(drop)
                mode.added += 0.001
                mode.dropSound.play()
                mode.dropAdded = True

    def evaluateAns(mode,answer):
        if mode.answerMin <= answer <= mode.answerMax:
            mode.correct = True
        else:
            mode.wrong = True


    def keyPressed(mode,event):
        if mode.inputError == True:
            mode.inputError = False
        ans = mode.ansButton
        if ans.enter == True:
            if event.key.isdigit():
                if ans.name == '':
                    ans.name = event.key
                elif len(ans.name) < 5:
                    ans.name += event.key
            elif event.key == 'Enter':
                ans.enter = False
                if ans.name == '':
                    mode.noneError = True
                else:
                    mode.evaluateAns(float(ans.name))
            elif event.key == 'Delete':
                ans.name = ans.name[:-1]
            elif event.key == '.':
                if '.' not in ans.name and not ans.name == '':
                    if ans.name[-1].isdigit():
                        ans.name += event.key
            else:
                mode.inputError = True

    def reInitialize(mode):
        mode.go = False
        mode.drop = False
        mode.dropAdded = False
        mode.tempPink = False
        mode.wrong = False
        mode.correct = False
        mode.titrantH = mode.height/8
        mode.added = 0
        mode.pinkCount = 0
        mode.drops = []
        mode.inputError = False
        mode.ansButton.name = ''
        mode.played = 0

    def mousePressed(mode,event):
        go = mode.goButton
        drop = mode.dropButton
        ans = mode.ansButton
        back = mode.backButton
        reset = mode.reset
        hint = mode.hintButton
        if mode.correct == False:
            if mode.wrong == True:
                mode.wrong = False
            if mode.inputError == True:
                mode.inputError = False
            if mode.noneError == True:
                mode.noneError = False
            goDist = ((go.x-event.x)**2+(go.y-event.y)**2)**0.5
            dropDist = ((drop.x-event.x)**2+(drop.y-event.y)**2)**0.5
            resetDist = ((reset.x-event.x)**2+(reset.y-event.y)**2)**0.5
            if goDist <= go.r:
                if mode.go == False:
                    mode.go = True
                    go.name = 'Close Valve'
                else:
                    mode.go = False
                    go.name = 'Open Valve'
                mode.click.play()
            if dropDist <= drop.r and mode.go == False:
                mode.titrantH += 0.2
                mode.drops.append(Drop(mode.width*0.5005,mode.height/2,mode.width/300))
                mode.click.play()
            if resetDist <= reset.r:
                mode.reInitialize()
                mode.click.play()
            if (ans.x-ans.width/2 <= event.x <= ans.x+ans.width/2) and \
            (ans.y-ans.height/2 <= event.y <= ans.y+ans.height/2):
                ans.name = ''
                ans.enter = True
                mode.click.play()
            else:
                ans.enter = False
            if (hint.x-hint.width/2 <= event.x <= hint.x+hint.width/2) and \
            (hint.y-hint.height/2 <= event.y <= hint.y+hint.height/2):
                if mode.hint == False:
                    hint.name = 'Close Hint'
                    mode.hint =  True
                else:
                    hint.name = 'Hint'
                    mode.hint = False
                mode.click.play()
        if (back.x-back.width/2 <= event.x <= back.x+back.width/2) and \
        (back.y-back.height/2 <= event.y <= back.y+back.height/2):
            mode.reInitialize()
            mode.back.play()
            mode.app.setActiveMode(mode.app.previousMode)


    def drawHint(mode,canvas):
        hintText = 'At the Equivalence Point (when the\n\nsolution became completely light pink),\n\nthe number of moles of the acid and\n\nthe base are equal. To get the number\n\nof moles of each reactant, you have to\n\nmultiply the volume(L) and concen-\n\ntration(M) of each solution added into\n\nthe mixture. '
        canvas.create_rectangle(mode.width*0.05,mode.height/5,mode.width*0.3,mode.height*0.7,fill='black',outline='white')
        canvas.create_polygon(mode.width*0.1,mode.height*0.15,mode.width*0.08,mode.height*0.2,mode.width*0.12,mode.height*0.2,fill='black',outline='white')
        canvas.create_line(mode.width*0.08,mode.height*0.2,mode.width*0.12,mode.height*0.2,fill='black')
        canvas.create_text(mode.width*0.175,mode.height*0.27,text = 'Calculating the Concentration',font = 'verdana 18  bold italic', fill='white')
        canvas.create_text(mode.width*0.175,mode.height*0.48,text = hintText,font = 'verdana 13  bold', fill='white')


    def drawSolution(mode,canvas):
        if mode.go or mode.dropAdded:
            if mode.added < mode.target-mode.pinkRange:
                if mode.type == 'acid':
                    mode.color = 'azure'
                else:
                    mode.color = 'maroon1'
            elif mode.target-mode.pinkRange <= mode.added < mode.target-mode.epsilon:
                mode.tempPink = True
            elif mode.target-mode.epsilon <= mode.added <= mode.target+mode.epsilon:
                mode.color = 'orchid1'
            else:
                if mode.type == 'acid':
                    mode.color = 'maroon1'
                else:
                    mode.color = 'azure'
        color = mode.color
        canvas.create_polygon(mode.width*0.45,mode.height*0.75,mode.width*0.55,mode.height*0.75,\
        mode.width*0.56,mode.height*0.78,mode.width*0.44,mode.height*0.78,fill = color)
        canvas.create_rectangle(mode.width*0.45,mode.height*0.75,mode.width*0.55,mode.height*0.845,fill = color,width=0)
        r = mode.width/50
        canvas.create_oval(mode.width*0.45-r,mode.height*0.81-r,mode.width*0.45+r,mode.height*0.81+r,fill = color,width=0)
        canvas.create_oval(mode.width*0.55-r,mode.height*0.81-r,mode.width*0.55+r,mode.height*0.81+r,fill = color,width=0)



    def drawTitrant(mode,canvas):
        color = 'skyblue'
        if mode.go and mode.titrantH < mode.height*0.4:
            mode.flowSound.play()
            canvas.create_rectangle(mode.width*0.499,mode.height*0.48,mode.width*0.5025,mode.height*0.8,fill=color,width=0)
        else:
            mode.flowSound.stop()
        canvas.create_rectangle(mode.width*0.499,mode.height*0.45,mode.width*0.5035,mode.height*0.46,fill=color,width=0)
        canvas.create_oval(mode.width*0.49,mode.height*0.42,mode.width*0.512,mode.height*0.445,fill=color,width=0)
        canvas.create_rectangle(mode.width*0.49,mode.titrantH,mode.width*0.512,mode.height*0.43,fill=color,width = 0)


    def redrawAll(mode,canvas):
        canvas.create_image(mode.width/2,mode.height/2,image = ImageTk.PhotoImage(mode.background))
        for drop in mode.drops:
            drop.drawDrop(canvas)
        mode.drawTitrant(canvas)
        mode.drawSolution(canvas)
        canvas.create_image(mode.width/2,mode.height*0.7,image = ImageTk.PhotoImage(mode.flask))
        canvas.create_image(mode.width/2,mode.height*0.15,image = ImageTk.PhotoImage(mode.burette))
        mode.dropButton.drawButton(canvas)
        mode.goButton.drawButton(canvas)
        mode.reset.drawButton(canvas)
        mode.hintButton.drawButton(canvas)
        canvas.create_text(mode.width/2,mode.height*0.9,text=f'Titrant Added: {mode.added:6.3f}L',font = ('verdana','14','bold'))
        canvas.create_text(mode.width*0.75,mode.height/5,text='Initial Variables',font = ('verdana 18  bold'))
        canvas.create_text(mode.width*0.75,mode.height/4,text=f'Initial Volume of Unknown Solution: {mode.unknownVol}L',font = ('verdana','14','bold'))
        canvas.create_text(mode.width*0.75,mode.height*0.3,text=f'Concentration of Titrant: {mode.titrantM}M',font = ('verdana','14','bold'))
        if mode.inputError == True:
            canvas.create_text(mode.width*0.857,mode.height*0.54,text = '*Error* Please enter a number!',font = 'verdana 12 bold')
        if mode.noneError == True:
            canvas.create_text(mode.width*0.857,mode.height*0.54,text = '*Error* Please submit a value!',font = 'verdana 12 bold')
        if mode.wrong == False:
            if mode.ansButton.enter == True:
                mode.ansButton.drawButton(canvas,'springgreen')
            else:
                mode.ansButton.drawButton(canvas,'white')
        else:
            canvas.create_text(mode.width*0.857,mode.height*0.46,text='Not Quite...',font = 'verdana 12 bold')
            mode.ansButton.drawButton(canvas,'red')
        mode.backButton.drawButton(canvas)
        if mode.hint == True:
            mode.drawHint(canvas)
        if mode.correct == True:
            if mode.played == 0:
                mode.success.play()
                mode.played += 1
            mode.ansButton.drawButton(canvas,'springgreen')
            canvas.create_rectangle(mode.width*0.4,mode.height*0.4,mode.width*0.6,mode.height*0.6,fill = 'springgreen')
            canvas.create_text(mode.width/2,mode.height*0.5,text = 'Titration Complete',font = ('verdana','14','bold'))
            canvas.create_text(mode.width*0.857,mode.height*0.46,text='Correct!',font = 'verdana 12 bold')


class ResetButton(TitrationMode):
    def __init__(self,name,x,y,r,color = 'red'):
        self.name = name
        self.x = x
        self.y = y
        self.r = r
        self.color = color

    def drawButton(self,canvas):
        canvas.create_oval(self.x-self.r,self.y-self.r,self.x+self.r,self.y+self.r,fill=self.color)
        canvas.create_text(self.x,self.y,text = self.name,font = ('verdana','12','bold'))

class DropButton(TitrationMode):
    def __init__(self,name,x,y,r):
        self.name = name
        self.x = x
        self.y = y
        self.r = r

    def drawButton(self,canvas):
        canvas.create_oval(self.x-self.r,self.y-self.r,self.x+self.r,self.y+self.r,fill='black',outline = 'white')
        canvas.create_text(self.x,self.y,text = self.name,fill='white',font = ('verdana','12','bold'))

class Drop(TitrationMode):
    def __init__(self,x,y,r):
        self.x = x
        self.y = y
        self.r = r
        self.color = 'skyblue'

    def drawDrop(self,canvas):
        canvas.create_oval(self.x-self.r,self.y-self.r,self.x+self.r,self.y+self.r,fill=self.color,width=0)
        canvas.create_polygon(self.x,self.y-2*self.r,self.x-self.r,self.y,self.x+self.r,self.y,fill=self.color)


class AnswerButton(TitrationMode):
    def __init__(self,x,y,width,height):
        self.name = ''
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.enter = False

    def drawButton(self,canvas,color):
        canvas.create_text(self.x-self.width*2.25,self.y,text = 'Concentration of the Unknown Solution:',font = ('verdana','14','bold'))
        canvas.create_text(self.x+self.width*0.7,self.y,text = '(M)',font = ('verdana','14','bold'))
        canvas.create_rectangle(self.x-self.width/2,self.y-self.height/2,self.x+self.width/2,self.y+self.height/2,fill=color)
        canvas.create_text(self.x,self.y,text = self.name,font = ('verdana','14','bold'))


class TExplainMode(Mode):
    def appStarted(mode):
        mode.background = mode.loadImage('images/grey.jpg')
        mode.overview = 'Titration is a lab procedure that allows us to determine the concentration of an unknown solution by mixing \n\nit with a solution of known concentration. In this virtual lab, your objective is to perform this procedure and \n\nenter the correct concentration of the unknown solution.'
        mode.guide = 'Here are some features of Titration Mode.\n\n- Select a titration type and initialize variables, then press the *Titrate* button to enter the lab.\n\n- Click the *Open Valve* button to add the titrant into the flask.\n\n- Click the *Drop* button to add a drop of titrant into the flask.\n\n- Add titrant until the solution completely turns light pink.\n\n- Calculate the concentration of the unknown solution using the initial variables and the experimental results.\n\n- You can press the *Hint* button to get hints for the calculation.\n\n- Enter the correct calculated value into the given slot to complete this mode.'
        mode.back = pygame.mixer.Sound('sounds/back.ogg')


    def keyPressed(mode,event):
        mode.app.setActiveMode(mode.app.acidBaseMode)
        mode.back.play()

    def redrawAll(mode,canvas):
        canvas.create_image(mode.width/2,mode.height/2,image = ImageTk.PhotoImage(mode.background))
        canvas.create_text(mode.width/2,mode.height*0.1,text = 'What is Titration?',font = 'verdana 24 bold italic')
        canvas.create_text(mode.width/2,mode.height*0.20,text = 'Overview', font = 'verdana 16 bold underline')
        canvas.create_text(mode.width/2,mode.height*0.30,text = f'{mode.overview}', font = 'verdana 14 bold')
        canvas.create_text(mode.width/2,mode.height*0.45,text = 'Virtual Lab Guide', font = 'verdana 16 bold underline')
        canvas.create_text(mode.width/2,mode.height*0.65,text = f'{mode.guide}', font = 'verdana 14 bold')
        canvas.create_text(mode.width/2,mode.height*0.9,text = '*Press any key to return*', font = 'verdana 12 bold')





## Citation: Superclass 'ModalApp' has been inherited from cmu_112_graphics
class MyModalApp(ModalApp):
    def appStarted(app):
        app.titrationModeInit = []
        app.chemicals = []
        app.HCDraw = dict()
        app.startMode = StartMode()
        app.combustionMode = CombustionMode()
        app.acidBaseMode = AcidBaseMode()
        app.cMoleculeMode = CMoleculeMode()
        app.titrationMode = TitrationMode()
        app.cExplainMode = CExplainMode()
        app.tExplainMode = TExplainMode()
        app.setActiveMode(StartMode())
        app.previousMode = None
        app.timerDelay = 10




app = MyModalApp(width=1450, height = 1000)