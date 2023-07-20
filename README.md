# LatticeGeometryUI

## Kurzbeschreibung

Die LatticeGeometryUI ist das User Interface zur `latticegeometrylib`, welche Funktionen bereitstellt, um aus einer beliebigen Eingangsgeometrie eine Schalengeometrie mit Gitterkern zu erzeugen.
Die grafische Nutzeroberfläche hat hierbei die Aufgabe, diese Funktionen in einen einfach durchführbaren Workflow zu kombinieren.

## Vorraussetzungen 

## Verwendung

### Einladen eines Modells und Erstellen einer Schalengeometrie

Das Einladen der Geometrie, welche mit einem Gitter gefüllt werden soll, geschieht im Punkt "Einladen des Modells". Das Betätigen der Schaltfläche "Datei auswählen" öffnet einen Dialog, mit welchem sich `.step`-Dateien einladen lassen.
Mit der Schaltfläche "Löschen" kann dieser Schritt rückgängig gemacht werden. 
<img src="./src/images/tab1.png " width="400" />
Die Schalengeometrie kann auf zwei Wegen erzeugt/ geladen werden. Der erste Weg ist die Erzeugung aus der Eingangsgeometrie, wobei hier lediglich die Wandstärke der Schalengeometrie angegeben werden muss.
Dies geschieht im Punkt "Erstellung des Schalenmodells aus dem Vollkörper". Das Feld "innen" meint hierbei eine Aufdickung ins Innere des Bauteils von der Oberfläche beginnend. Umgekehrt ist bei einer Aufdickung nach außen 
die Oberfläche des Eingangsmodells nun die Innenfläche. Eine Aufdickung in beide Richtungen ist ebenfalls möglich.
Außerdem ist es möglich, eine Schalengeometrie extern zu erstellen und nachträglich einzuladen. Hierfür muss unter "Einladen des Modells" die Schaltfläche "Vollkörper" auf Schale umgestellt werden.

### Initialisierung des Gitters und der Elementarzelle

Der Anwender hat im Tab "2" die Möglichkeit die Abmessungen der Elementarzelle in x, y und z-Richtung anzugeben. Ein Schalter steuert hierbei, ob diese Abmessungen genau eingehalten werden sollen.
Ist die Option für eine Raumrichtung nicht aktiviert, kommt es zu einer geringfügigen Anpassung der angegeben Maße.
<img src="./src/images/tab2.png " width="400" />
Wird auf "Elementarzelle initialisieren" geklickt, erscheint im Vorschaufenster ein interaktives Abbild des Gitters. Der Anwender hat somit eine Vorstellung, wie viele Elementarzellen erzeugt werden.

### Konfiguration der Elementarzelle

Die Konfiguration der Elementarzelle geschieht über die Angabe einzelner Listen, welche jeweils ein Objekt darstellen, das der Zelle hinzugefügt werden soll. Diese Listen beinhalten hierbei Knotenindizes
die ein solches Objekt definieren. Außerdem können Attribute (wie z.B. der Durchmesser) mit angegeben werden.

Knotendefinition:
````
[ 1, { 'diameter': 1.0 } ]  (genau auf Eckknoten)
[ (1, 2), { 'diameter': 1.0 } ] (mittig von Eckknoten) 
[ (1, 2, 0.7), { 'diameter': 1.0 } ] (relative Position zu beiden Eckknoten)
[ (1, 2, 0.7, 0.7), { 'diameter': 1.0 } ] (relative Position zu beiden Eckknoten)
[ ( (1,2), 3), { 'diameter': 1.0 } ] (Verschachtelung)
```   

Strebendefinition:
```
[ 1, 3, { 'diameter': 1.0 } ]
[ 2, (2,3), { 'diameter': 1.0 } ]
```

Plattendefinition:
```
[ 1, 3, 2, { 'thickness': 1.0 } ]
[ 2, (2,3), 4, { 'thickness': 1.0 } ]
```

Definition einer Verrundung:
```
[ 'fillet' { 'radius': 0.25 } ]
```

Einladen von Vorlagen:
```
[ 'template' { 'filepath': 'C:/ ... /templates/template.txt' } ]
```

Definition viele Variablen:
```
[ 'var' { 'name': 'd', 'value': 2.0 } ]
[ 1, 2, { 'diameter': 'd' } ]
```

Angemerkt sei hierbei, dass in Vorlagen-Dateien die gleiche Notation verwendet wird. Dies ermöglicht ein Abspeichern von Zwischenständen. Die Variablen besitzen den Vorteil, dass somit die Geometrie
mehrerer Einträge gleichzeitig beeinflusst werden kann.
<img src="./src/images/tab3.png " width="400" />

Ist die Konfiguration einer Elementarzelle abgeschlossen, kann die Geometrie der Elementarzelle über "Erstellen" erzeugt werden.

### Erstellung des Gitters und Überschneidung mit dem Eingangsmodells

Das Gitter entsteht über die räumliche Wiederholung der Elementarzelle. Die Abmessungen der Elementarzelle und des Gitters wurden bereits in Tab "2" definiert. Die Gestalt der Elementarzelle ist zudem in Tab "3"
konfiguriert worden. Daher muss in Tab "4" unter "Erstellung des Gitters aus der Elementarzelle" nur die Schaltfläche "Erstellen" betätigt werden.
<img src="./src/images/tab4.png " width="400" />
Ähnliches gilt für die Überschneidung des Gitters mit der Eingangsgeometrie. Da Eingangsgeometrie und Gitter bereits definiert sind, muss lediglich die Schaltfläche "Erstellen" gedrückt werden.

### Verschmelzen von Gitter und Schale

Da das Gitter bereits zurechtgeschnitten und die Schale definiert ist, geschieht die Verschmelzung der beiden über die Schaltfläche "Erstellen"
<img src="./src/images/tab5.png " width="400" />
Die dabei entstehende Geometrie kann schließlich in eine `.step`-Datei oder eine `.stl`-Datei exportiert werden.



