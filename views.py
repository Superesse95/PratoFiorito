import os, pickle
from PyQt5.QtWidgets import QPushButton, QMainWindow, QApplication, QAction, QWidget, QGridLayout, QLineEdit, QLabel, QTabWidget, QRadioButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QSize, Qt, QTimer, QTime, pyqtSignal
from PyQt5.QtGui import QIcon, QPalette

from controllers import MinesweeperButton

from model import *

from dark_fusion import QDarkPalette

from ranking import *


# °°°°°°°° START CLASSE NECESSARIA ALLA PERSONALIZZAZIONE DELLA GRIGLIA DI GIOCO °°°°°°°°

class ConfigPane(QWidget):
    def __init__(self, parameters, on_configure, **kwargs):
        '''The constructor takes a list of integer params of the form (NAME, [VALUES]).'''
        super().__init__(**kwargs)
        self.setStyleSheet("font: 16px Andale Mono")

        layout = QGridLayout(self)

        self._textinputs = []
        self._configbutton = QPushButton(text='New Game')
        self._configbutton.clicked.connect(on_configure)

        layout.addWidget(self._configbutton, 0, 0)
        layout.addWidget(QLabel(text='Width'), 0, 1)
        layout.addWidget(QLabel(text='Height'), 0, 2)
        layout.addWidget(QLabel(text='Mines'), 0, 3)

        for (i, (p, values)) in enumerate(parameters): # Iterate over all config parameters.
            radio_button = QRadioButton(text=p)
            layout.addWidget(radio_button, i+1, 0)
            values_list = []
            for j, value in enumerate(values):
                if (i < 3):
                    line_edit = QLineEdit(text=str(value))
                    line_edit.setReadOnly(True)
                    values_list.append(line_edit)
                    layout.addWidget(values_list[j], i+1, j+1)
                else:
                    values_list.append(QLineEdit(text=str(value)))
                    layout.addWidget(values_list[j], i+1, j+1)
            self._textinputs.append({'radio_btn': radio_button, 'values': values_list})
        self._textinputs[0]['radio_btn'].click()

    def get_param(self): # Ritorna i parametri (width, height, bombs) selezionati dall'utente
        current_param = []
        for elem in self._textinputs:
            if(elem['radio_btn'].isChecked()):
                current_param.append({'difficulties': elem['radio_btn'].text(), 'values': elem['values']})
        return current_param

# °°°°°°°° END CLASSE NECESSARIA ALLA PERSONALIZZAZIONE DELLA GRIGLIA DI GIOCO °°°°°°°°



# °°°°°°°° START CLASSE NECESSARIA ALLA GENERAZIONE DELLA GRIGLIA DI GIOCO °°°°°°°°

# Class to create layout of game application.
class ButtonPane(QWidget):

    manage_ranking = pyqtSignal(str)

    def __init__(self, width, height, bombs, diff, matrix, m_sum, path_matrix, saving, restoring, on_configure):
        super().__init__()

        self.diff = diff # Difficoltà
        self.saving = saving
        self.restoring = restoring

        self.setStyleSheet("font: 16px Andale Mono")

        QVLayout = QVBoxLayout(self)

        area_info = QWidget()
        area_info.setStyleSheet("background-color: gray; border: 1px solid black")
        QHLayout = QHBoxLayout(area_info)

        self.label_1 = QLabel(str(bombs))
        self.label_1.setFixedSize(QSize(80, 30))
        self.label_1.setAlignment(Qt.AlignCenter)
        self.label_1.setStyleSheet("background-color: black; color: red; border-radius: 5px; border: 1px solid black")

        label_2 = QPushButton()
        label_2.setFixedSize(QSize(60, 60))
        label_2.setIcon(QIcon(sys.path[0] + '/Images/sun-smile.png'))
        label_2.setIconSize(QSize(60,60))
        label_2.clicked.connect(on_configure)

        self.label_3 = QLabel('Tempo')
        self.label_3.setFixedSize(QSize(80, 30))
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label_3.setStyleSheet("background-color: black; color: red; border-radius: 5px; border: 1px solid black")

        self.curr_time = QTime(00,00,00)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerEvent)

        area_game = QWidget()
        area_game.setStyleSheet("border: 1px solid black")
        buttons_layout = QGridLayout(area_game)
        buttons_layout.setSpacing(0)
        self.btn_matrix = [[0 for _ in range(height)] for _ in range(width)]
        # Generazione della griglia di gioco
        for i in range(width):
            for j in range(height):
                btn = MinesweeperButton(row=i, col=j, bombs=bombs, diff=diff, matrix=matrix, m_sum=m_sum, path_matrix=path_matrix, bomb_label=self.label_1, img=label_2)
                buttons_layout.addWidget(btn, i, j)
                btn.update_button.connect(self.update_game)
                btn.defeat_signal.connect(self.manage_defeat)
                btn.win_signal.connect(self.manage_win)
                self.btn_matrix[i][j] = btn

        QHLayout.addWidget(self.label_1)
        QHLayout.addWidget(label_2)
        QHLayout.addWidget(self.label_3)

        self.name_zone = QWidget()
        horizontal_layout = QHBoxLayout(self.name_zone)
        label_name = QLabel('Nome:')
        self.name = QLineEdit()
        self.submit_btn = QPushButton('Go!')

        horizontal_layout.addWidget(label_name)
        horizontal_layout.addWidget(self.name)
        horizontal_layout.addWidget(self.submit_btn)
        self.name_zone.hide()


        QVLayout.addWidget(area_info)
        QVLayout.addWidget(area_game)

        QVLayout.addWidget(self.name_zone)

    def update_game(self, game_over): # Aggiornamento dello stato delle caselle componenti la griglia
        for index_row, row in enumerate(self.btn_matrix):
            for index_col, col in enumerate(row):
                self.btn_matrix[index_row][index_col].update(game_over)

    def timerEvent(self): # Aggiormamento del timer
        self.curr_time = self.curr_time.addSecs(1)
        self.label_3.setText(self.curr_time.toString("hh:mm:ss"))

    def manage_win(self): # Gestione del segnale indicante la vittoria
        self.timer.stop()
        self.saving.setDisabled(True)
        self.restoring.setDisabled(True)
        self.manage_ranking.emit(self.curr_time.toString("hh:mm:ss"))
        if(os.path.isfile(sys.path[0] + '/Temp/objs.pkl')):
            os.remove(sys.path[0] + '/Temp/objs.pkl')

    def manage_defeat(self): # Gestione del segnale indicante la sconfitta
        self.timer.stop()
        self.saving.setDisabled(True)
        self.restoring.setDisabled(True)
        if(os.path.isfile(sys.path[0] + '/Temp/objs.pkl')):
            os.remove(sys.path[0] + '/Temp/objs.pkl')

# °°°°°°°° END CLASSE NECESSARIA ALLA GENERAZIONE DELLA GRIGLIA DI GIOCO °°°°°°°°


# °°°°°°°° START CLASSE RESPONSABILE DELLA VISUALIZZAZIONE DELLA CLASSIFICA °°°°°°°°

class ShowRanking(QWidget):
    def __init__(self, **kwargs):
        '''The constructor takes a list of integer params of the form (NAME, [VALUES]).'''
        super().__init__(**kwargs)
        self.setStyleSheet("font: 14px Andale Mono")
        layout = QVBoxLayout(self)

        rankings = QWidget()
        layout.addWidget(rankings)

        grid_layout = QGridLayout(rankings)
        grid_layout.addWidget(QLabel(text='Beginner'), 0, 0, 1, 2)
        grid_layout.addWidget(QLabel(text='Intermediate'), 0, 4, 1, 2)
        grid_layout.addWidget(QLabel(text='Expert'), 0, 8, 1, 2)

        class_types = ['Beginner', 'Intermediate', 'Expert']

        for c, class_type in enumerate(class_types): # Iterate over all config parameters.
            c = c * 4
            ranking_class = Ranking(class_type)
            ranking = ranking_class.ranking
            for r, line in enumerate(ranking):
                if(r <= 9):
                    grid_layout.addWidget(QLabel(line[0]), r + 1, c)
                    grid_layout.addWidget(QLabel(line[1]), r + 1, c + 1)
                    grid_layout.addWidget(QLabel(line[2].rjust(len(line[2])+4, ' ')), r + 1, c + 2)
                    if(c < 8):
                        grid_layout.addWidget(QLabel('     '), r + 1, c + 3)

# °°°°°°°° START CLASSE RESPONSABILE DELLA VISUALIZZAZIONE DELLA CLASSIFICA °°°°°°°°


# °°°°°°°° START CLASSE RESPONSABILE DELLA CREAZIONE DELL'INTERA APPLICAZIONE °°°°°°°°

class CreateApp(QMainWindow):
    '''The main application. The on_configure() method is called when the 'Reconfigure' button pressed on config pane.'''

    def __init__(self):
        super().__init__()

        self.setGeometry(10, 10, 0, 0)
        self.setWindowTitle('Prato Fiorito')

        # °°°°° START MENU BAR °°°°°
        menubar = self.menuBar() # Barra dei Menu
        # FILE
        fileMenu = menubar.addMenu('File')
        self.saving = QAction('Save', self, triggered=self.save, shortcut='Ctrl+S')
        self.restoring = QAction('Load', self, triggered=self.restore, shortcut='Ctrl+L')
        fileMenu.addAction(self.saving)
        fileMenu.addAction(self.restoring)
        exists = os.path.isfile(sys.path[0] + '/Temp/objs.pkl')
        if(exists == False):
            self.restoring.setDisabled(True)
        # VISTA
        viewMenu = menubar.addMenu('Vista')
        self.day_action = QAction('Day Mode', self, checkable=True, triggered=self.setDayMode, shortcut='Ctrl+D')
        self.day_action.setChecked(True)
        self.night_action = QAction('Night Mode', self, checkable=True, triggered=self.setNightMode, shortcut='Ctrl+N')
        self.day_action.setDisabled(True)
        viewMenu.addAction(self.day_action)
        viewMenu.addAction(self.night_action)
        # REGOLE
        rulesMenu = menubar.addMenu('Regole')
        rulesMenu.addAction(QAction('Open Rules', self, triggered=self.openRuleFile, shortcut='Ctrl+R'))
        # °°°°° END MENU BAR °°°°°

        # °°°°° START TAB WIDGET °°°°°
        self._root = QTabWidget()
        self._root.setCornerWidget(self._root.tabBar(), Qt.TopLeftCorner)
        self.setCentralWidget(self._root)

        # CONFIGURAZIONE
        self._config = ConfigPane(parameters=[('Beginner', [9, 9, 10]), ('Intermediate', [16, 16, 40]), ('Expert', [16, 30, 99]), ('Custom', [20, 30, 145])], on_configure=self.on_configure)

        exists = os.path.isfile(sys.path[0] + '/Temp/objs.pkl')
        if(exists):
            self.restore() # Recupero variabili salvate
            diff = ['Beginner', 'Intermediate', 'Expert', 'Custom']
            self._config._textinputs[diff.index(self.difficulties)]['radio_btn'].setChecked(True)
        else:
            self._config._configbutton.click() # Inizializzazione del gioco

        # RANKING
        self._ranking = ShowRanking()

        self._root.addTab(self._config, 'Configuration')
        self._root.addTab(self._buttons, 'Game')
        self._root.addTab(self._ranking, 'Ranking')

        self._root.currentChanged.connect(self.resize_window)
        self._root.setCurrentIndex(1)
        # °°°°° END TAB WIDGET °°°°°

    # function called when the index of the clicked Tab changes
    def resize_window(self): # Ridmensione l'area della finestra, in relazione allo spazio occupato dai widgets presenti
        if(self._root.currentIndex() == 0):
            self.setFixedSize(500, 500)
        elif(self._root.currentIndex() == 1):
            width = self._buttons.sizeHint().width()
            height = self._buttons.sizeHint().height() + 30
            self.setFixedSize(QSize(width, height))
        elif((self._root.currentIndex() == 2)):
            width = self._ranking.sizeHint().width() + 40
            height = self._ranking.sizeHint().height() + 40
            self.setFixedSize(QSize(width, height))

    # This is the callback we pass into the constructor of ConfigPane
    # so that it can call us back with the 'New Game' button is
    # pressed.
    def on_configure(self):
        '''Callback for re-configure request on config pane.'''
        self.saving.setDisabled(False)
        self.difficulties = self._config.get_param()[0]['difficulties']
        parameters = self._config.get_param()[0]['values']

        if(len(parameters) > 0):
            n_rows = int(parameters[0].text())
            n_cols = int(parameters[1].text())
            self.bombs = int(parameters[2].text())
            if(n_rows < 1):
                n_rows = 1
            elif(n_rows > 25):
                n_rows = 25
            if(n_cols < 8):
                n_cols = 8
            elif(n_cols > 45):
                n_cols = 45

            if(n_rows == 1 and n_cols == 8):
                self.bombs = 2
            elif(n_rows == 25 and n_cols == 45):
                self.bombs = 500
            elif(n_rows//n_cols >= 1 and self.bombs > 500):
                self.bombs = int(n_rows*n_cols*0.5)
            elif(n_cols//n_rows >= 1 and self.bombs > 500):
                self.bombs = int(n_rows * n_cols * 0.5)
            elif(self.bombs >= n_rows*n_cols):
                self.bombs = int(n_rows * n_cols * 0.5)

            self._config._textinputs[3]['values'][0].setText(str(n_rows))
            self._config._textinputs[3]['values'][1].setText(str(n_cols))
            self._config._textinputs[3]['values'][2].setText(str(self.bombs))

            self.matrix = create_matrix_of_game(n_rows, n_cols, self.bombs)
            self.m_sum = compute_matrix_sum(self.matrix, n_rows, n_cols)
            self.path_matrix = np.asarray([[' ' for _ in range(n_cols)] for _ in range(n_rows)])

            print('__________________________________________________________________________')
            print('matrix')
            print()
            print(self.matrix)
            print('__________________________________________________________________________')
            print('m_sum')
            print()
            print(self.m_sum)
            print('__________________________________________________________________________')
            print()

            self._buttons = ButtonPane(width=n_rows, height=n_cols, bombs=self.bombs, diff=self.difficulties, matrix=self.matrix, m_sum=self.m_sum, path_matrix=self.path_matrix, saving=self.saving, restoring=self.restoring, on_configure=self.on_configure)
            self._buttons.manage_ranking.connect(self.set_ranking)
            self._root.removeTab(1)
            self._root.insertTab(1, self._buttons, 'Game')
            self._root.setCurrentIndex(1)
            self._buttons.timer.start(1000)

    def set_ranking(self, time): # Funzione responsabile dell'inserimento in classifica di un eventuale vincitore
        if(self.difficulties != 'Custom'):
            position = Ranking(class_type=self.difficulties).compute_pos(time)
            if(position <= 10 and position != -1):
                self.time = time
                self._buttons.name_zone.show()
                self.setFixedSize(self._buttons.sizeHint())
                self._buttons.submit_btn.clicked.connect(self.result_registration) # Cliccando sul bottone 'Submit' viene chiamata la funzione 'result registration', responsabile della registrazione in classifica

    def result_registration(self):
        name = self._buttons.name.text()
        if(name == ''):
            name = 'unknown'
        my_elem = name + '#' + self.time

        Ranking(class_type=self.difficulties).insert(my_elem=my_elem)
        self._buttons.name_zone.hide()
        self.setFixedSize(self._buttons.sizeHint())
        # Aggiornamento vista classifica
        self._root.removeTab(2)
        self._ranking = ShowRanking()
        self._root.insertTab(2, self._ranking, 'Ranking')

    def setDayMode(self):
        self.setStyleSheet('color: black')
        self.day_action.setDisabled(True)
        self.day_action.setChecked(True)
        self.night_action.setDisabled(False)
        self.night_action.setChecked(False)
        QDay = QPalette()
        self.setPalette(QDay)

    def setNightMode(self):
        self.setStyleSheet('color: gray')
        self.day_action.setDisabled(False)
        self.day_action.setChecked(False)
        self.night_action.setDisabled(True)
        self.night_action.setChecked(True)
        QDark = QDarkPalette()
        self.setPalette(QDark)

    def openRuleFile(self):
        os.system('open ' + sys.path[0] +'/Regole.pdf')

    def save(self): # Funzione responsabile del salvataggio della partita
        with open(sys.path[0] + '/Temp/objs.pkl', 'wb') as f:
            pickle.dump([self.matrix, self.m_sum, self.path_matrix, self.bombs, self.difficulties, self._buttons.curr_time, self._buttons.label_1.text(), self._buttons.label_3.text()], f)
        self.restoring.setDisabled(False)

    def restore(self): # Funzione responsabile del caricamento della partita salvata in precedenza
        exists = os.path.isfile(sys.path[0] + '/Temp/objs.pkl')
        if (exists == True):
            with open(sys.path[0] + '/Temp/objs.pkl', 'rb') as f:
                self.matrix, self.m_sum, self.path_matrix, self.bombs, self.difficulties, curr_time, label_1, label_3 = pickle.load(f)

                width = self.matrix.shape[0]
                height = self.matrix.shape[1]

                self._buttons = ButtonPane(width=width, height=height, bombs=self.bombs, diff=self.difficulties, matrix=self.matrix, m_sum=self.m_sum, path_matrix=self.path_matrix, saving=self.saving, restoring=self.restoring, on_configure=self.on_configure)

                self._buttons.label_1.setText(label_1)
                self._buttons.label_3.setText(label_3)
                self._buttons.manage_ranking.connect(self.set_ranking)
                self._buttons.curr_time = curr_time
                self._buttons.timer.start(1000)

                self._root.removeTab(1)
                self._root.insertTab(1, self._buttons, 'Game')
                self._root.setCurrentIndex(1)

                self.saving.setDisabled(False)

                print('__________________________________________________________________________')
                print('matrix')
                print()

                print(self.matrix)
                print('__________________________________________________________________________')
                print('m_sum')
                print()
                print(self.m_sum)
                print('__________________________________________________________________________')
                print()

                for i in range(width):
                    for j in range(height):
                        self._buttons.btn_matrix[i][j].update()

# °°°°°°°° END CLASSE RESPONSABILE DELLA CREAZIONE DELL'INTERA APPLICAZIONE °°°°°°°°


# Instantiate and run the application.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = CreateApp()
    mainWindow.show()
    app.exit(app.exec_())
    if(mainWindow.saving.isEnabled() == True): # Se è possibile salvare la partita, questa viene salvata
        mainWindow.save()