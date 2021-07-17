import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy


wCam, hCam = 640, 480
frameR = 100     #Reducción de fotogramas
smoothening = 7  #valor aleatorio


pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()

# imprimir (wScr, hScr)

while True:
    # Paso 1: encuentra los puntos de referencia
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # Paso 2: obtén la punta del dedo índice y medio
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # Paso 3: comprueba qué dedos están hacia arriba
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)

        # Paso 4: solo dedo índice: modo de movimiento
        if fingers[1] == 1 and fingers[2] == 0:

            # Paso 5: convierte las coordenadas
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            # Paso 6: valores suaves
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Paso 7: mover el mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # Paso 8: Tanto el índice como el medio están arriba: modo de clic
        if fingers[1] == 1 and fingers[2] == 1:

            # Paso 9: Encuentra la distancia entre los dedos
            length, img, lineInfo = detector.findDistance(8, 12, img)

            # Paso 10: haga clic en el mouse si la distancia es corta
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()

    # Paso 11: Velocidad de fotogramas
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)

    # Paso 12: Pantalla
    cv2.imshow("image", img)
    cv2.waitKey(1)