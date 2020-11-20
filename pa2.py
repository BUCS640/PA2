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



class AIPlayer(Player):
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
        
        point=[0,0]
        value,position=self.minimax(self,board,float('-inf'),float('inf'),3,point,True)  
        return int(position[0]), int(position[1])
        
        
        ################### TODO: ######################################
        # Implement your strategy here. 
        # Feel free to call as many as helper functions as you want.
        # We only cares the return of this function
        ################################################################
    def minimax(self,board,alpha,beta,depth,point,maximizingPlayer):
        
        if depth==0 and board.is_full() == True and board.is_win_for(self.checker, point[0], point[1]) and board.is_win_for(self.opponent_checker(), point[0], point[1]):
            return evaluate(board), []
        nodes=[]
        for row in range(board.height):
                for col in range(board.width):
                    if board.can_add_to(row, col):
                        nodes.append([row,col])
        next_point = [0, 0]
        
        if maximizingPlayer:
            best_value = float('-inf')
            for node in nodes:
                        board.add_checker(self.checker,node[0],node[1])
                        value_child,next_move=self.minimax(self,board,alpha,beta,depth-1,node,False)
                        board.slots[node[0]][node[1]]=' '
                        if value_child > best_value:
                            best_value=value_child
                            next_point[0]=node[0]
                            next_point[1]=node[1]
                            alpha=max(alpha,best_value)
                            if beta <= alpha:
                                break
        else:
            best_value= float('inf')
            for node in nodes:
                        board.add_checker(self.opponent_checker(),node[0],node[1])
                        value_child,next_move=self.minimax(self,board,alpha,beta,depth-1,True)
                        board.slots[node[0]][node[1]]=' '
                        if value_child < best_value:
                            best_value=value_child
                            next_point[0]=node[0]
                            next_point[1]=node[1]
                            beta=min(alpha,best_value)
                            if beta <= alpha:
                                break
        return best_value, next_point
    
    
    def evaluate(self,board):
            
