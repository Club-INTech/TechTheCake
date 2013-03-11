
import sys, random, math
from PyQt4 import QtGui, QtCore

class FenetrePrincipale(QtGui.QMainWindow) :
    def __init__(self) :
        QtGui.QMainWindow.__init__(self)
        
        self.canvas, self.boutons, self.regleHorizontale, self.regleVerticale = None, None, None, None
        
        self.sizeX , self.sizeY = 800, 600
        self.resize(self.sizeX, self.sizeY)
        self.frameCanvas = QtGui.QFrame(self)
        self.frameBoutons = QtGui.QFrame(self)
        self.frameRegleVerticale = QtGui.QFrame(self)
        self.frameRegleHorizontale = QtGui.QFrame(self)
        
        self.widthFrameBoutons = 220
        self.widthRegleVerticale = 100
        self.heightRegleHorizontale = 40
      
        self.frameCanvas.setFrameShape(QtGui.QFrame.Box)
        self.frameBoutons.setFrameShape(QtGui.QFrame.Box)
        self.frameRegleHorizontale.setFrameShape(QtGui.QFrame.Box)
        self.frameRegleVerticale.setFrameShape(QtGui.QFrame.Box)
        
        self.frameBoutons.show()
        self.frameCanvas.show()
        self.frameRegleHorizontale.show()
        self.frameRegleVerticale.show()
        
        self.setMinimumSize(500,300)
        self.show()
        
    def addCanvas(self, canvas) :
        self.canvas = canvas
    def addBoutons(self, boutons) :
        self.boutons = boutons
    def addRegleHorizontale(self, regle) :
        self.regleHorizontale = regle
    def addRegleVerticale(self, regle) :
        self.regleVerticale = regle
    def addGraduationH(self, g) :
        self.graduationH = g
    def addGraduationV(self, g) :
        self.graduationV = g
        
    def paintEvent(self, e) :
        self.frameCanvas.resize(self.size().width() - self.widthFrameBoutons - self.widthRegleVerticale, self.size().height() - self.heightRegleHorizontale)
        self.frameCanvas.move(self.widthRegleVerticale, 0)
        self.frameRegleHorizontale.resize(self.size().width() - self.widthFrameBoutons - self.widthRegleVerticale, self.heightRegleHorizontale)
        self.frameRegleHorizontale.move(self.widthRegleVerticale, self.size().height() - self.heightRegleHorizontale)
        self.frameRegleVerticale.resize(self.widthRegleVerticale, self.size().height() - self.heightRegleHorizontale)
        
        self.frameBoutons.resize(self.widthFrameBoutons, self.size().height())
        self.frameBoutons.move(self.size().width()-self.widthFrameBoutons, 0)
        
class GraduationV(QtGui.QWidget) :
    def __init__(self, fenetrePrincipale) :
        self.fenetrePrincipale = fenetrePrincipale
        self.fenetrePrincipale.addGraduationV(self)
        QtGui.QWidget.__init__(self, fenetrePrincipale.frameRegleVerticale)
        self.show()
        
    def paintEvent(self, e) :
        self.resize(self.parent().size())
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawGraduations(qp)
        qp.end()
        
    def drawGraduations(self, qp) :
        hauteur = self.parent().size().height()
        nombreGraduationsMax = hauteur//50
        deltaCoord = self.fenetrePrincipale.canvas.maxCoordY - self.fenetrePrincipale.canvas.minCoordY
        pas = float(deltaCoord)/nombreGraduationsMax
        
        base = _simplify(self.fenetrePrincipale.canvas.minCoordY)
        
        for id_ in range(nombreGraduationsMax) :
            qp.drawText(15, self.fenetrePrincipale.canvas.coordsToPixels(0,_simplify(base+pas*id_))[1] , _intToSc(base+pas*id_))
        
class GraduationH(QtGui.QWidget) :
    def __init__(self, fenetrePrincipale) :
        self.fenetrePrincipale = fenetrePrincipale
        self.fenetrePrincipale.addGraduationH(self)
        QtGui.QWidget.__init__(self, fenetrePrincipale.frameRegleHorizontale)
        self.show()
        
    def paintEvent(self, e) :
        self.resize(self.parent().size())
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawGraduations(qp)
        qp.end()
        
    def drawGraduations(self, qp) :
        largeur = self.parent().size().width()
        nombreGraduationsMax = largeur//100
        deltaCoord = self.fenetrePrincipale.canvas.maxCoordX - self.fenetrePrincipale.canvas.minCoordX
        pas = float(deltaCoord)/nombreGraduationsMax
        base = _simplify(self.fenetrePrincipale.canvas.minCoordX)
        for id_ in range(nombreGraduationsMax) :
            qp.drawText(self.fenetrePrincipale.canvas.coordsToPixels(_simplify(base+pas*id_),0)[0], 14, _intToSc(base+pas*id_))
            
        
class Boutons(QtGui.QWidget) :
    def __init__(self, fenetrePrincipale) :
        self.fenetrePrincipale = fenetrePrincipale
        self.fenetrePrincipale.addBoutons(self)
        QtGui.QWidget.__init__(self, fenetrePrincipale.frameBoutons)
        VLayout = QtGui.QVBoxLayout()
        
        # ---- Réinitialiser la vue ----
        reinitialiserBouton = QtGui.QPushButton("Réinitialiser la vue", self)
        reinitialiserBouton.clicked.connect(self.reinitialiserVue)
        
        
        # ---- Epaisseur des courbes ----
        frameEpaisseur = QtGui.QFrame(self)
        boxEpaisseur = QtGui.QHBoxLayout()
        texteEpaisseur = QtGui.QLabel("Epaisseur des courbes :", frameEpaisseur)
        tailleCourbe = QtGui.QSpinBox(frameEpaisseur)
        tailleCourbe.setRange(1,10)
        tailleCourbe.setValue(5)
        tailleCourbe.valueChanged.connect(self.changerEpaisseurCourbes)
        boxEpaisseur.addWidget(texteEpaisseur)
        boxEpaisseur.addWidget(tailleCourbe)
        frameEpaisseur.setLayout(boxEpaisseur)
        
        # ---- Liste déroulante des courbes ----
        frameListeDeroulanteCourbes = QtGui.QFrame(self)
        boxListeDeroulanteCourbes = QtGui.QHBoxLayout()
        texteListe = QtGui.QLabel("Courbes :", frameListeDeroulanteCourbes)
        listeDeroulanteCourbes = QtGui.QComboBox(frameListeDeroulanteCourbes)
        for courbe in self.fenetrePrincipale.canvas.courbes :
            listeDeroulanteCourbes.addItem(courbe.name)
        boxListeDeroulanteCourbes.addWidget(texteListe)
        boxListeDeroulanteCourbes.addWidget(listeDeroulanteCourbes)
        frameListeDeroulanteCourbes.setLayout(boxListeDeroulanteCourbes)
        
        # ---- Ajout des items dans la VBoxLayout ----
        VLayout.addWidget(reinitialiserBouton)
        VLayout.addWidget(frameEpaisseur)
        VLayout.addWidget(frameListeDeroulanteCourbes)
        
        self.setLayout(VLayout)
        self.show()
        
    def changerEpaisseurCourbes(self, e) :
        sender = self.sender()
        self.fenetrePrincipale.statusBar().showMessage("Modification de la taille des courbes : " + str(sender.value()))
        self.fenetrePrincipale.canvas.changerEpaisseurCourbes(sender.value())
        
    def reinitialiserVue(self, e) :
        self.fenetrePrincipale.statusBar().showMessage("Réinitialisation de la vue")
        self.fenetrePrincipale.canvas.reinitialiserVue()
        
        
        
class Canvas(QtGui.QWidget) :
    def __init__(self, courbes) :
        self.courbes = courbes
        self.marge = 10
        
        
        self.fenetrePrincipale = FenetrePrincipale()
        QtGui.QWidget.__init__(self, self.fenetrePrincipale.frameCanvas)
        self.fenetrePrincipale.addCanvas(self)
        
        Boutons(self.fenetrePrincipale)
        GraduationV(self.fenetrePrincipale)
        GraduationH(self.fenetrePrincipale)
        
        
        self.maxCoordX, self.maxCoordY = self._getMaxCoords()
        self.minCoordX, self.minCoordY = self._getMinCoords()
        
        self.show()

        
    def _getMaxCoords(self) :
        tableauX, tableauY = [], []
        for courbe in self.courbes :
            tableauX.append(max(courbe.valeurs_x))
            tableauY.append(max(courbe.valeurs_y))
        return (max(tableauX), max(tableauY))
        
    def _getMinCoords(self) :
        tableauX, tableauY = [], []
        for courbe in self.courbes :
            tableauX.append(min(courbe.valeurs_x))
            tableauY.append(min(courbe.valeurs_y))
        return (min(tableauX), min(tableauY))
        
    def coordsToPixels(self, coord_x, coord_y) :
        pixel_x = (coord_x - self.minCoordX)/(self.maxCoordX - self.minCoordX) * (self.size().width()-2*self.marge) + self.marge
        pixel_y = (1-(coord_y - self.minCoordY)/(self.maxCoordY - self.minCoordY)) * (self.size().height()-2*self.marge)+self.marge
        
        return (int(pixel_x), int(pixel_y))
        
    def reinitialiserVue(self) :
        self.maxCoordX, self.maxCoordY = self._getMaxCoords()
        self.minCoordX, self.minCoordY = self._getMinCoords()
        self.update()
    
    # Redraw
    def paintEvent(self, e) :
        self.resize(self.parent().size().width(), self.parent().size().height())
        qp = QtGui.QPainter()
        qp.begin(self)
        
        for courbe in self.courbes :
            self.drawCourbe(qp, courbe)
        qp.end()
        
        self.fenetrePrincipale.graduationH.update()
        self.fenetrePrincipale.graduationV.update()
        
        
    # Molette souris
    def wheelEvent(self, e) :
        delta = e.delta()
        message = "Zoom "
        if delta > 0 : message += "in"
        else : message += "out"
        self.fenetrePrincipale.statusBar().showMessage(message)
        
        fac = .001
        
        fac*=delta
        
        maxCoordX = (1-fac)*self.maxCoordX + fac*self.minCoordX
        minCoordX = fac*self.maxCoordX + (1-fac)*self.minCoordX
        maxCoordY = (1-fac)*self.maxCoordY + fac*self.minCoordY
        minCoordY = fac*self.maxCoordY + (1-fac)*self.minCoordY
        
        self.minCoordX, self.maxCoordX = minCoordX, maxCoordX
        self.minCoordY, self.maxCoordY = minCoordY, maxCoordY
            
        self.update()
        
    
    def deplacerFenetre(self, x, y) :
        fac= .002
        deplX = (self.maxCoordX - self.minCoordX)*x*fac
        deplY = (self.maxCoordY - self.minCoordY)*y*fac
        
        self.minCoordX -= deplX
        self.maxCoordX -= deplX
        self.minCoordY -= deplY
        self.maxCoordY -= deplY
        
        self.update()
        
    def mouseMoveEvent(self, e) :
        # Clique gauche
        if int(e.buttons()) == 1 :
            delta = e.pos() - self.cliqueGauchePos
            self.deplacerFenetre(delta.x(), -delta.y())
            self.fenetrePrincipale.statusBar().showMessage("Déplacement de la fenêtre")
            self.cliqueGauchePos = e.pos()
        
    def mousePressEvent(self, e) :
        # Clique gauche
        if e.button() == 1 :
            self.cliqueGauchePos = e.pos()
        
       
        
    def drawCourbe(self, qp, courbe):
        pen = QtGui.QPen()
        pen.setWidth(courbe.width)
        pen.setColor(courbe.color)
        qp.setPen(pen)
        size = self.size()
        
        for id_, val_ in enumerate(courbe.valeurs_x) :
            if id_ > 0 :
                pixels = self.coordsToPixels(val_, courbe.valeurs_y[id_])
                qp.drawLine(pixels_precedent[0], pixels_precedent[1], pixels[0], pixels[1])
                pixels_precedent=pixels
            else :
                pixels_precedent = self.coordsToPixels(val_, courbe.valeurs_y[id_])
                
    def changerEpaisseurCourbes(self, val) :
        for courbe in self.courbes :
            courbe.width = val
        self.update()
        
                  
    
class Courbe :
    def __init__(self, valeurs_x = None, valeurs_y = None, color=None, name=None) :
        if not hasattr(Courbe, "nombreCourbes") :
            Courbe.nombreCourbes = 1
        else :
            Courbe.nombreCourbes += 1
        
        if valeurs_x is None : valeurs_x=[]
        if valeurs_y is None : valeurs_y=[]
        
        self.valeurs_x = valeurs_x
        self.valeurs_y = valeurs_y
        
        self.width = 5
        if name is None : self.name = "Courbe sans nom " + str(Courbe.nombreCourbes)
        else : self.name = name
        
        if color is None : self.color = QtGui.QColor("red")
        else : self.color = QtGui.QColor(color)
        
    def addPoint(self, x, y) :
        self.valeurs_x.append(x)
        self.valeurs_y.append(y)
        
# Retourne un int
def _scToInt(string) :
    i = string.find("e")
    m = float(string[:i])
    e = int(string[i+1:])
    return (m*10**e)
    
# Retourne un str
def _intToSc(int_) :
    if abs(int_) >= 0.1:
        return "%.1f"%int_
    else :
        return "%.1e"%int_
        
def _simplify(int_) :
    return _scToInt('%.1e'%int_)
    
def _getPuissanceDe10LaPlusProche(float_) :
    if float_ != 0 :
        return round(math.log(abs(float_)))
    else :
        return 0
        
def createCourbe(points) :
    c = Courbe()
    for pt in points :
        c.addPoint(pt[0], pt[1])
    return c
    
def createDeltaCourbe(delta, ordonnees) :
    c = Courbe()
    for id_, ordo in enumerate(ordonnees) :
        c.addPoint(id_*delta, ordo)
    return c
        
        
        
if __name__ == "__main__" :
    c1 = Courbe([1,3,6], [2,-1,5])
    c2 = createCourbe([[1,2], [3,5], [4, 6], [7, -1]])
    c3 = createDeltaCourbe(0.5, [1,1.1,1.3,1.5,1.58,1.62,1.63,1.64,1.56,1.40,1.3,1.2,1.15,1.1, 1.08])
    app = QtGui.QApplication(sys.argv)
    
    canvas = Canvas([c3])
    sys.exit(app.exec_())