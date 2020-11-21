# 
# Programming Assignment 2, CS640
#
# A Gomoku (Gobang) Game
#
# Adapted from CS111
# By Yiwen Gu
#
# You need to implement an AI Player for Gomoku
# A Random Player is provided for you
# 
#


from pa2_gomoku import Player
import random

FIVE = 7
FOUR, THREE, TWO = 6 ,4 ,2
SFOUR, STHREE, STWO = 5 ,3 ,1

class AIPlayer(Player):
 
    def __init__(self,checker, depth=2):
        super().__init__(checker)
        self.depth = depth
        self.moves = []
        self.count = [[0 for i in range(8)] for j in range(2)] 
        self.record = [[[0,0,0,0] for row in range(10)] for col in range(10)]
        self.pos_score = [[(5 - max(abs(x - 5), abs(y - 5))) for x in range(10)] for y in range(10)]
        self.num_moves = 0
        
    def reset(self):
        for row in range(10):
            for col in range(10):
                for i in range(4):
                    self.record[row][col][i] = 0
                    
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0
        
    """ a subclass of Player that looks ahead some number of moves and 
    strategically determines its best next move.
    """

    def next_move(self, board):
        """ returns the called AIPlayer's next move for a game on
            the specified Board object. 
            input: board is a Board object for the game that the called
                     Player is playing.
            return: row, col are the coordinated of a vacant location on the board 
        """
        self.num_moves += 1
       
        assert (not board.is_full())       
        self.moves.clear()
        
        if self.is_empty(board):
            # if it's the 1st move, and it's AI's turn
            # then ai will randomly choose one in the center of the board.
            cent_row = board.width // 2
            cent_col = board.height // 2
            buff_row = round(board.width / 20)
            buff_col = round(board.width / 20)
            self.moves.append(
                (random.randint(-buff_row, buff_row) + cent_row,
                 random.randint(-buff_col, buff_col) + cent_col))
        else:
            self.minimax(board,float('-inf'),float('inf'),self.depth,True)
        row, col = random.choice(self.moves)
        return row, col
        
        ################### TODO: ######################################
        # Implement your strategy here. 
        # Feel free to call as many as helper functions as you want.
        # We only cares the return of this function
        ################################################################
    def is_empty(self,board):
        for r in range(board.height):
            for c in range(board.width):
                if board.slots[r][c]!=' ':
                    return False
        return True
    
    def has_neighbor(self,node,board):
        r=node[0]
        c=node[1]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if 0 <= r + i < board.width and 0 <= c + j < board.height:
                    if board.slots[r+i][c+j] != ' ':
                        return True
        return False
    
    def genmove(self,board):
        nodes=[]
        for row in range(board.height):
                for col in range(board.width):
                    node=[row,col]
                    if board.slots[row][col] ==' ' and self.has_neighbor(node,board):
                        score = self.pos_score[row][col]
                        nodes.append((score, row, col))
        nodes.sort(reverse=True)                
        return nodes
                            
    def minimax(self,board,alpha,beta,depth,maximizingPlayer):
        
        if depth==0:
            return self.evaluate(board)
        
        nodes=self.genmove(board)
        
        for node in nodes:
            if maximizingPlayer:
                board.add_checker(self.checker,node[1],node[2])
            else:
                board.add_checker(self.opponent_checker(),node[1],node[2]) 
                
            value= - self.minimax(board,-beta,-alpha,depth-1,not maximizingPlayer)
            board.slots[node[1]][node[2]]=' '
            if value > alpha:
                if depth == self.depth:
                    self.moves.clear()
                    self.moves.append((node[1],node[2]))
                alpha = value
                if alpha >= beta:
                    break   
            elif value == alpha:
                if depth == self.depth:
                    self.moves.append((node[1],node[2]))
        return alpha
    
    
    def evaluate(self,board):
        
        self.reset()
        score_sum= 0
        me = self.checker
        other=self.opponent_checker()
        
        for row in range(board.height):
            for col in range(board.width):
                if board.slots[row][col] == me:
                    self.checkPoint(board, row, col, me, other)
                elif board.slots[row][col] == other:
                    self.checkPoint(board, row, col, other, me)	
        count1 = self.count[0]
        count2 = self.count[1]
        score1, score2 = self.getScore(count1, count2)
        score_sum= score1 - score2 
        return score_sum
    
    def checkPoint(self, board, row, col, player1, player2):
        direction = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for i in range(4):
            if self.record[row][col][i] == 0:
                if player1==self.checker:
                    self.scan(board, row, col, i, direction[i], player1, player2, self.count[0])
                elif player1==self.opponent_checker():
                    self.scan(board, row, col, i, direction[i], player1, player2, self.count[1])
                
    def getLine(self, board, row, col, direction, player1, player2):
        line=[]
        for i in range(9):
            line.append(0)
        
        j=0
        for i in range(-4,5):
            tempX = row + i * direction[0]
            tempY = col + i * direction[1]
            if (tempX < 0 or tempX >= board.height or 
                tempY < 0 or tempY >= board.width):
                line[j] = player2
            else:
                line[j] = board.slots[tempX][tempY]
            j += 1
        return line
    
    def scan(self, board, row, col, index, direction, player1, player2, count):
		# record line range[left, right] as analysized
        def setRecord(self, row, col, left, right, index, direction):
            tmp_x = row + (-5 + left) * direction[0]
            tmp_y = col + (-5 + left) * direction[1]
            for i in range(left, right+1):
                tmp_x += direction[0]
                tmp_y += direction[1]
                self.record[tmp_x][tmp_y][index] = 1
	
        left_idx, right_idx = 4, 4
		
        line = self.getLine(board, row, col, direction, player1, player2)

        while right_idx < 8:
            if line[right_idx+1] != player1:
                break
            right_idx += 1
        while left_idx > 0:
            if line[left_idx-1] != player1:
                break
            left_idx -= 1
		
        left_range, right_range = left_idx, right_idx
        while right_range < 8:
            if line[right_range+1] == player2:
                break
            right_range += 1
        while left_range > 0:
            if line[left_range-1] == player2:
                break
            left_range -= 1
		
        chess_range = right_range - left_range + 1
        if chess_range < 5:
            setRecord(self, row, col, left_range, right_range, index, direction)
            return 0
		
        setRecord(self, row, col, left_idx, right_idx, index, direction)
		
        m_range = right_idx - left_idx + 1
		
		# M:mine chess, P:opponent chess or out of range, X: empty
        if m_range == 5:
            count[FIVE] += 1
		
		# Live Four : XMMMMX 
		# Chong Four : XMMMMP, PMMMMX
        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx-1] == ' ':
                left_empty = True			
            if line[right_idx+1] == ' ':
                right_empty = True
            if left_empty and right_empty:
                count[FOUR] += 1
            elif left_empty or right_empty:
                count[SFOUR] += 1
		
		# Chong Four : MXMMM, MMMXM, the two types can both exist
		# Live Three : XMMMXX, XXMMMX
		# Sleep Three : PMMMX, XMMMP, PXMMMXP
        if m_range == 3:
            left_empty = right_empty = False
            left_four = right_four = False
            if line[left_idx-1] == ' ':
                if line[left_idx-2] == player1: # MXMMM
                    setRecord(self, row, col, left_idx-2, left_idx-1, index, direction)
                    count[SFOUR] += 1
                    left_four = True
                left_empty = True
				
            if line[right_idx+1] == ' ':
                if line[right_idx+2] == player1: # MMMXM
                    setRecord(self, row, col, right_idx+1, right_idx+2, index, direction)
                    count[SFOUR] += 1
                    right_four = True 
                right_empty = True
			
            if left_four or right_four:
                pass
            elif left_empty and right_empty:
                if chess_range > 5: # XMMMXX, XXMMMX
                    count[THREE] += 1
                else: # PXMMMXP
                    count[STHREE] += 1
            elif left_empty or right_empty: # PMMMX, XMMMP
                count[STHREE] += 1
		
		# Chong Four: MMXMM, only check right direction
		# Live Three: XMXMMX, XMMXMX the two types can both exist
		# Sleep Three: PMXMMX, XMXMMP, PMMXMX, XMMXMP
		# Live Two: XMMX
		# Sleep Two: PMMX, XMMP
        if m_range == 2:
            left_empty = right_empty = False
            left_three = right_three = False
            if line[left_idx-1] == ' ':
                if line[left_idx-2] == player1:
                    setRecord(self, row, col, left_idx-2, left_idx-1, index, direction)
                    if line[left_idx-3] == ' ':
                        if line[right_idx+1] == ' ': # XMXMMX
                            count[THREE] += 1
                        else: # XMXMMP
                            count[STHREE] += 1
                        left_three = True
                    elif line[left_idx-3] == player2: # PMXMMX
                        if line[right_idx+1] == ' ':
                            count[STHREE] += 1
                            left_three = True
						
                left_empty = True
			
            if line[right_idx+1] == ' ':
                if line[right_idx+2] == player1:
                    if line[right_idx+3] == player1:  # MMXMM
                        setRecord(self, row, col, right_idx+1, right_idx+2, index, direction)
                        count[SFOUR] += 1
                        right_three = True
                    elif line[right_idx+3] == ' ':
						#setRecord(self, x, y, right_idx+1, right_idx+2, dir_index, dir)
                        if left_empty:  # XMMXMX
                            count[THREE] += 1
                        else:  # PMMXMX
                            count[STHREE] += 1
                        right_three = True
                    elif left_empty: # XMMXMP
                        count[STHREE] += 1
                        right_three = True
						
                right_empty = True
			
            if left_three or right_three:
                pass
            elif left_empty and right_empty: # XMMX
                count[TWO] += 1
            elif left_empty or right_empty: # PMMX, XMMP
                count[STWO] += 1
		
		# Live Two: XMXMX, XMXXMX only check right direction
		# Sleep Two: PMXMX, XMXMP 
        if m_range == 1:
            left_empty = right_empty = False
            if line[left_idx-1] == ' ':
                if line[left_idx-2] == player1:
                    if line[left_idx-3] == ' ':
                        if line[right_idx+1] == player2: # XMXMP
                            count[STWO] += 1
                left_empty = True
                
            if line[right_idx+1] == ' ':
                if line[right_idx+2] == player1:
                    if line[right_idx+3] == ' ':
                        if left_empty: # XMXMX
							#setRecord(self, x, y, left_idx, right_idx+2, dir_index, dir)
                            count[TWO] += 1
                        else: # PMXMX
                            count[STWO] += 1
                elif line[right_idx+2] == ' ':
                    if line[right_idx+3] == player1 and line[right_idx+4] == ' ': # XMXXMX
                        count[TWO] += 1
						
        return 0
    
   
    
    def getScore(self, mine_count, opponent_count):
        mscore, oscore = 0, 0
        if mine_count[FIVE] > 0:
            return (10000, 0)
        if opponent_count[FIVE] > 0:
            return (0, 10000)
				
        if mine_count[SFOUR] >= 2:
            mine_count[FOUR] += 1
        if opponent_count[SFOUR] >= 2:
            opponent_count[FOUR] += 1
				
        if mine_count[FOUR] > 0:
            return (9050, 0)
        if mine_count[SFOUR] > 0:
            return (9040, 0)
			
        if opponent_count[FOUR] > 0:
            return (0, 9030)
        if opponent_count[SFOUR] > 0 and opponent_count[THREE] > 0:
            return (0, 9020)
			
        if mine_count[THREE] > 0 and opponent_count[SFOUR] == 0:
            return (9010, 0)
			
        if (opponent_count[THREE] > 1 and mine_count[THREE] == 0 and mine_count[STHREE] == 0):
            return (0, 9000)

        if opponent_count[SFOUR] > 0:
            oscore += 400

        if mine_count[THREE] > 1:
            mscore += 500
        elif mine_count[THREE] > 0:
            mscore += 100
			
        if opponent_count[THREE] > 1:
            oscore += 2000
        elif opponent_count[THREE] > 0:
            oscore += 400

        if mine_count[STHREE] > 0:
            mscore += mine_count[STHREE] * 10
        if opponent_count[STHREE] > 0:
            oscore += opponent_count[STHREE] * 10
			
        if mine_count[TWO] > 0:
            mscore += mine_count[TWO] * 6
        if opponent_count[TWO] > 0:
            oscore += opponent_count[TWO] * 6
				
        if mine_count[STWO] > 0:
            mscore += mine_count[STWO] * 2
        if opponent_count[STWO] > 0:
            oscore += opponent_count[STWO] * 2
		
        return (mscore, oscore)