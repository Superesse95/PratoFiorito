import random
import numpy as np

def padding_function(matrix): # Aggiunge zeri intorno alla matrice 'matrix'
    n_row = matrix.shape[0] + 2
    n_col = matrix.shape[1] + 2
    pad_matrix = np.zeros((n_row,n_col))
    for r in range(1,n_row-1):
        pad_matrix[r][1:n_col-1] = matrix[r-1]
    return pad_matrix

def explore_area(matrix, m_sum, path_matrix, row, col):
    # Verifica nell'intorno del punto (row, col) eventuali celle libere da bombe

    points_to_explore = []
    if(m_sum[row][col] == 0):

        path_matrix[row][col] = '0'

        if(row - 1 >= 0  and matrix[row - 1][col] != 1):
            if(path_matrix[row - 1][col] != 'p'):
                if(m_sum[row - 1][col] == 0):
                    path_matrix[row - 1][col] = '0'
                    points_to_explore.append([row - 1, col])
                else:
                    path_matrix[row - 1][col] = m_sum[row - 1][col]

        if(row + 1 <= m_sum.shape[0] - 1 and matrix[row + 1][col] != 1):
            if(path_matrix[row + 1][col] != 'p'):
                if(m_sum[row + 1][col] == 0):
                    path_matrix[row + 1][col] = '0'
                    points_to_explore.append([row + 1, col])
                else:
                    path_matrix[row + 1][col] = m_sum[row + 1][col]

        if(col - 1 >= 0  and matrix[row][col - 1] != 1):
            if(path_matrix[row][col - 1] != 'p'):
                if(m_sum[row][col - 1] == 0):
                    path_matrix[row][col - 1] = '0'
                    points_to_explore.append([row, col - 1])
                else:
                    path_matrix[row][col - 1] = m_sum[row][col - 1]

        if(col + 1 <= m_sum.shape[1] - 1 and matrix[row][col + 1] != 1):
            if(path_matrix[row][col + 1] != 'p'):
                if(m_sum[row][col + 1] == 0):
                    path_matrix[row][col + 1] = '0'
                    points_to_explore.append([row, col + 1])
                else:
                    path_matrix[row][col + 1] = m_sum[row][col + 1]

        if(row - 1 >= 0 and col - 1 >= 0 and matrix[row - 1][col - 1] != 1):
            if(path_matrix[row - 1][col - 1] != 'p'):
                if(m_sum[row - 1][col - 1] != 0):
                   path_matrix[row - 1][col - 1] = m_sum[row - 1][col - 1]

        if(row + 1 <= m_sum.shape[0] - 1 and col - 1 >= 0 and matrix[row + 1][col - 1] != 1):
            if(path_matrix[row + 1][col - 1] != 'p'):
                if(m_sum[row + 1][col - 1] != 0):
                    path_matrix[row + 1][col - 1] = m_sum[row + 1][col - 1]

        if(row - 1 >= 0 and col + 1 <= m_sum.shape[1] - 1 and matrix[row - 1][col + 1] != 1):
            if(path_matrix[row - 1][col + 1] != 'p'):
                if(m_sum[row - 1][col + 1] != 0):
                    path_matrix[row - 1][col + 1] = m_sum[row - 1][col + 1]

        if(row + 1 <= m_sum.shape[0] - 1 and col + 1 <= m_sum.shape[1] - 1 and matrix[row + 1][col + 1] != 1):
            if(path_matrix[row + 1][col + 1] != 'p'):
                if(m_sum[row + 1][col + 1] != 0):
                    path_matrix[row + 1][col + 1] = m_sum[row + 1][col + 1]
    else:
        path_matrix[row][col] = m_sum[row][col]
    return points_to_explore

def click_on_card(matrix, m_sum, path_matrix, row, col, n_bombs):
    state = 1 # state = -1 -> Problema, state = 0 -> Sconfitta, state = 1 -> Gioco, state = 2 -> Vittoria
    if ((row >= 0 and row < m_sum.shape[0]) and (col >= 0 and col < m_sum.shape[1])):
        if(matrix[row][col] == 1): # Giocata perdente
            for r, row_elements in enumerate(matrix):
                for c, element in enumerate(row_elements):
                    if(element == 1 and path_matrix[r][c] != 'p'):
                        path_matrix[r][c] = '*'
            path_matrix[row][col] = '!'
            state = 0

        elif(path_matrix[row][col] != 'p'): # Rilevamento eventuali celle libere
            points_to_explore = explore_area(matrix, m_sum, path_matrix, row, col)
            already_explored = [[row, col]]
            while (len(points_to_explore) > 0):
                for elem in points_to_explore:
                    new_points_to_explore = explore_area(matrix, m_sum, path_matrix, elem[0], elem[1])
                    points_to_explore.remove(elem)
                    already_explored.append(elem)
                    for new_point in new_points_to_explore:
                        find = False
                        for old_point in already_explored:
                            if (new_point == old_point):
                                find = True
                        if (find == False):
                            points_to_explore.append(new_point)
            #path_matrix[row][col] = '0'

            count = 0 # Verifica eventuale vittoria
            for row, row_elements in enumerate(path_matrix):
                for col, element in enumerate(row_elements):
                    if(path_matrix[row][col] == ' ' or path_matrix[row][col] == 'p'):
                        count+=1
            if(count == n_bombs):
                state = 2
    else: # Errore
        state = -1
    return state

def compute_matrix_sum(matrix, n_rows, n_cols):
    # Calcolo delle bombe attorno a ciscun punto della matrice

    m = padding_function(matrix).astype('int')
    m_sum = np.zeros((n_rows, n_cols)).astype('int')
    for r in range(1, m.shape[0] - 1):
        for c in range(1, m.shape[1] - 1):
            sum = m[r - 1][c - 1] + m[r - 1][c] + m[r - 1][c + 1] + m[r][c - 1] + m[r][c + 1] + m[r + 1][c - 1] + m[r + 1][c] + m[r + 1][c + 1]
            m_sum[r - 1][c - 1] = sum
    return m_sum

def create_matrix_of_game(n_rows, n_cols, n_bombs):
    # Generazione casuale della matrice del gioco

    matrix = np.zeros((n_rows, n_cols)).astype('int')
    i = 0
    while (i < n_bombs):
        row = random.randint(0, matrix.shape[0] - 1)
        col = random.randint(0, matrix.shape[1] - 1)
        if (matrix[row][col] != 1):
            i += 1
            matrix[row][col] = 1
    return matrix

if __name__ == '__main__':
    n_rows = 9; n_cols = 9; n_bombs = 10
    flags = [[0, 0], [0, 1], [0,2], [1, 0]]
    matrix = create_matrix_of_game(n_rows, n_cols, n_bombs)
    print(matrix)
    print()
    m_sum = compute_matrix_sum(matrix, n_rows, n_cols)
    print(m_sum)
    print()
    path_matrix = np.asarray([[' ' for i in range(n_rows)] for j in range(n_cols)])

    '''
    for i in range(3):
        for j in range(3):
            if(i == 1 and j == 1):
                path_matrix[i][j] = path_matrix[i][j]
            else:
                path_matrix[i][j] = 'p'
    '''

    r_clicked = 5; c_clicked = 5
    click_on_card(matrix, m_sum, path_matrix, r_clicked, c_clicked, n_bombs)
    print(path_matrix)