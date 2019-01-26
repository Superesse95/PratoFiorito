import sys

class Ranking():

    def __init__(self, class_type = 'Beginner'):  # Inizializzazione della classe
        self.class_type = class_type
        # °°°°° START LETTURA CLASSIFICA ATTUALE DA FILE °°°°°
        filename = sys.path[0] + '/Rankings/' + self.class_type + ".txt"
        file = open(filename, "r")
        self.ranking = []
        for line in file:
            line = line.split('#')
            line[2] = line[2][0:8]
            self.ranking.append(line)
        file.close()
        # °°°°° END LETTURA CLASSIFICA ATTUALE DA FILE °°°°°

    def compute_pos(self, my_time_elem): # Determina l'eventuale posizione di classifica
        h, m, s = my_time_elem.split(":")
        my_time = int(h + m + s)  # Da 01:02:03 A 10203

        position = -1

        for i, elem in enumerate(self.ranking):  # Determino l'eventuale posizione di classifica
            h, m, s = elem[2].split(":")
            time = int(h + m + s)

            if (my_time < time and position == -1):
                position = i + 1

        if (len(self.ranking) == 0):
            position = 1
        elif (len(self.ranking) < 10 and position == -1):
            position = len(self.ranking) + 1

        return position

    def insert(self, my_elem): # Inserisce il giocatore nella rispettiva posizione, aggiornando tutta la classica

        upgrade = False

        pos = self.compute_pos(my_elem.split("#")[1]) # ESEMPIO: Isolamento 01:02:03 DAL Nome
        print(pos)
        if(pos <= 10 and pos != -1):

            line = my_elem.split("#")
            line.insert(0, str(pos))

            self.ranking.insert(pos-1, line)

            for index in range(pos, len(self.ranking)):
                position = int(self.ranking[index][0])
                if (position < 10):
                    position += 1
                    self.ranking[index][0] = str(position)
                else:
                    self.ranking.remove(self.ranking[10])

            upgrade = True
        # °°°°° START SCRITTURA NUOVA CLASSIFICA SU FILE °°°°°
        if(upgrade == True):
            filename = sys.path[0] + '/Rankings/' + self.class_type + ".txt"
            file = open(filename, "w")
            for line in self.ranking:
                file.write(line[0] + '#' + line[1] + '#' + line[2] + '\n')
            file.close()
        # °°°°° END SCRITTURA NUOVA CLASSIFICA SU FILE °°°°°

        return upgrade

if __name__ == '__main__':
    A = Ranking()
    A.insert('Patrizio#00:00:10')
