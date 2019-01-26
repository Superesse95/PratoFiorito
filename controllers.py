import sys
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.Qt import QIcon

from model import *

# CLASSE RESPONSABILE DELLA GESTIONE DELLA SINGOLA CASELLA DI GIOCO
class MinesweeperButton(QPushButton):
    update_button = pyqtSignal(bool) # Segnale aggiornamento casella/bottone
    win_signal = pyqtSignal() # Segnale di vittoria
    defeat_signal = pyqtSignal() # Segnale di sconfitta

    def __init__(self, row, col, bombs, diff, matrix, m_sum, path_matrix, bomb_label, img):
        super().__init__()
        self.image_path = sys.path[0]
        self.row = row
        self.col = col
        self.bombs = bombs
        self.diff = diff
        self.matrix = matrix
        self.m_sum = m_sum
        self.path_matrix = path_matrix
        self.bomb_label = bomb_label
        self.img = img
        self.setStyleSheet("border: 0px solid")
        self.setIcon(QIcon(sys.path[0] + '/Images/facingDown.png'))
        self.setIconSize(QSize(32, 32))
        self.setFixedSize(QSize(30, 30))

    def update(self, game_over = False): # Viene aggiornata l'immagine del bottone visibile all'utente in relazione al corrispodente valore nella matrice path_matrix
        if(game_over == False):
            if(self.path_matrix[self.row][self.col] != ' ' and  self.path_matrix[self.row][self.col] != 'p'):
                self.setIcon(QIcon(sys.path[0] + '/Images/' + self.path_matrix[self.row][self.col] +'.png'))
                self.setDisabled(True)
            elif(self.path_matrix[self.row][self.col] == 'p'):
                self.setIcon(QIcon(sys.path[0] + '/Images/flagged.png'))
        else:
            if(self.path_matrix[self.row][self.col] == '*'):
                self.setIcon(QIcon(sys.path[0] + '/Images/bomb.png'))
            self.setDisabled(True)

        #print(self.path_matrix)
        #print()

    def mousePressEvent(self, event): # Gestione evento 'Pressione del mouse'
        if(event.button() != Qt.RightButton):
            self.img.setIcon(QIcon(sys.path[0] + '/Images/attesa.png'))

    def mouseReleaseEvent(self, event): # Gestione evento 'Rilasciamento del mouse'
        if(event.button() == Qt.RightButton and self.path_matrix[self.row][self.col] != 'p'): # Posizionamento bandierina 'p'
            actual_bombs = int(self.bomb_label.text())
            if(actual_bombs > 0):
                actual_bombs -= 1
                self.bomb_label.setText(str(actual_bombs))
                self.path_matrix[self.row][self.col] = 'p'
                self.setIcon(QIcon(sys.path[0] + '/Images/flagged.png'))

        elif(event.button() == Qt.RightButton and self.path_matrix[self.row][self.col] == 'p'): # Rimozione bandierina 'p'
            actual_bombs = int(self.bomb_label.text())
            if(actual_bombs < self.bombs):
                actual_bombs += 1
                self.bomb_label.setText(str(actual_bombs))
                self.path_matrix[self.row][self.col] = ' '
                self.setIcon(QIcon(sys.path[0] + '/Images/facingDown.png'))

        elif (self.path_matrix[self.row][self.col] != 'p'): # Verifica attorno a punto cliccato
            state = click_on_card(matrix=self.matrix, m_sum=self.m_sum, path_matrix=self.path_matrix, row=self.row, col=self.col, n_bombs=self.bombs)
            if(state == 0): # Sconfitta
                self.setIcon(QIcon(sys.path[0] + '/Images/boom.png'))
                self.img.setIcon(QIcon(sys.path[0] + '/Images/sun-sad.png'))
                self.update_button.emit(True)
                self.defeat_signal.emit() # Emissione segnale sconfitta
            if(state == 1): # Gioco
                self.img.setIcon(QIcon(sys.path[0] + '/Images/sun-smile.png'))
                self.update_button.emit(False)
            if(state == 2): #Vittoria
                self.img.setIcon(QIcon(sys.path[0] + '/Images/sun-glasses.png'))
                self.update_button.emit(False)
                self.win_signal.emit() # Emissione segnale vittoria