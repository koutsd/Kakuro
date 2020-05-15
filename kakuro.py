import time
from csp import *


def varStr(i, j):   # Variable Xij --> 2 Digits for i,j
    var = "X"
    if i < 10:
        var += "0"
    var += str(i)
    if j < 10:
        var += "0"
    return var + str(j)


class Model:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.rows = len(puzzle)             # Number of rows
        self.columns = len(puzzle[0])       # Number of columns
        self.sums = []                      # List of [Variable Sums, Results] --> [[variables], Result]
        self.variables = []                 # Variable Xij (i = row, j = column)
        self.domains = {}                   # Domain for each variable Xij = [1,2,3,4,5,6,7,8,9]
        self.neighbors = {}                 # Neighbors for each Xij = List of variables

        sumVars = []
        res = 0
        # Get row sums
        for i in range(self.rows):
            for j in range(self.columns):
                var = varStr(i, j)
                if puzzle[i][j] == '_':                     # If current cell is variable
                    sumVars.append(var)
                    self.variables.append(var)              # Store Variable
                    self.domains[var] = range(1, 10)        # Store domain of Variable
                else:           # If current cell is black (with or without sum hint)
                    if sumVars:
                        self.sums.append([sumVars, res])    # Store Sum
                    if isinstance(puzzle[i][j], list) and isinstance(puzzle[i][j][1], int):
                        res = puzzle[i][j][1]               # Store Sum result
                    sumVars = []
        # Get column sums
        for j in range(self.columns):
            for i in range(self.rows):
                var = varStr(i, j)
                if puzzle[i][j] == '_':                     # If current cell is variable
                    sumVars.append(var)
                else:
                    if sumVars:
                        self.sums.append([sumVars, res])    # Store Sum
                    if isinstance(puzzle[i][j], list) and isinstance(puzzle[i][j][0], int):
                        res = puzzle[i][j][0]               # Store Sum result
                    sumVars = []
        # Get neighbors of each variable
        for var in self.variables:
            self.neighbors[var] = []
            for sumVars, _ in self.sums:
                if var in sumVars:
                    for neighborVar in sumVars:
                        if neighborVar != var and neighborVar not in self.neighbors[var]:
                            self.neighbors[var].append(neighborVar)

    # Display solution in the form of "X(i,j) = Val" for each variable (X)
    def display_variables(self, solution):
        print("\nSolution:", end="")
        for i in range(self.rows):
            for j in range(self.columns):
                if varStr(i, j) in (var for var, value in solution.items()):
                    for var, value in solution.items():
                        if var == varStr(i, j):
                            print("X(%d,%d) = %d" % (i, j, value), end="  ")
            print("")

    # Display puzzle in grid form with or without solution
    def display_grid(self, solution=None):
        for i, row in enumerate(self.puzzle):
            print("")
            for c in range(self.columns):
                print("|-----", end="")
            print("|\n|", end="")
            for j, elem in enumerate(row):
                if elem == '*':
                    print("*****|", end="")         # Black cell without Hint
                elif elem == '_':                   # Variable cell
                    if not solution:
                        print("     |", end="")
                    else:
                        print("  %d  |" % solution[varStr(i, j)], end="")
                else:                               # Black cell with Hint
                    cell = str(elem[0])
                    if elem[0] == '':
                        cell = '**'
                    elif elem[0] < 10:
                        cell = ' ' + cell
                    cell += "\\" + str(elem[1])
                    if elem[1] == '':
                        cell += '**'
                    elif elem[1] < 10:
                        cell += ' '
                    print("%s|" % cell, end="")
        print("")
        for c in range(self.columns):
            print("|-----", end="")
        print("|")


class Kakuro(CSP):
    def __init__(self, model):
        self.rows = model.rows
        self.columns = model.columns
        self.sums = model.sums

        CSP.__init__(self, model.variables, model.domains, model.neighbors, self.constraints)

    # Check if A,B variables satisfy constraints
    def constraints(self, varA, valueA, varB, valueB):      # A,B Variables --> a,b values of A,B
        if varB not in self.neighbors[varA]:                # B not dependent on A
            return True
        if valueA == valueB:                                # All Diff constraint not satisfied
            return False

        values = []
        for variables, result in self.sums:
            if varA not in variables or varB not in variables:
                continue

            for var in variables:
                if var == varA:
                    values.append(valueA)
                elif var == varB:
                    values.append(valueB)
                elif len(self.curr_domains[var]) == 1:
                    values.append(self.curr_domains[var][0])
            # If some variables aren't filled yet check if sum constraint can still be satisfied
            if len(values) < len(variables):
                currNum = 10
                newValues = list(values)
                while len(newValues) < len(variables):
                    currNum -= 1
                    if currNum not in newValues:
                        newValues.append(currNum)
                # If max possible sum < result: Sum constraint cannot be satisfied
                if sum(newValues) < result:
                    return False

                currNum = 0
                newValues = list(values)
                while len(newValues) < len(variables):
                    currNum += 1
                    if currNum not in newValues:
                        newValues.append(currNum)
                # If min possible sum <= result: Sum constraint can still be satisfied
                if sum(newValues) <= result:
                    return True
            elif sum(values) == result:         # Sum constraint is satisfied
                return True

            return False

    # Solve Kakuro problem
    def solve(self,
              inference=no_inference,
              select_unassigned_variable=first_unassigned_variable,
              order_domain_values=unordered_domain_values):

        start = int(round(time.time() * 1000))
        result = backtracking_search(self,
                                     select_unassigned_variable=select_unassigned_variable,
                                     order_domain_values=order_domain_values,
                                     inference=inference)
        end = int(round(time.time() * 1000))
        print("Solved in %dms with %d assignments" % (end - start, self.nassigns))

        return result


if __name__ == '__main__':
    puzzles = [kakuro1, kakuro2, kakuro3, kakuro4]

    for puzzle in puzzles:
        print("\n--------------- Puzzle%d ---------------" % (puzzles.index(puzzle) + 1))
        model = Model(puzzle)

        # print("BT: ", end="")
        # BT = Kakuro(model)
        # solution = BT.solve()
        # # model.display_variables(solution)

        print("FC: ", end="")
        FC = Kakuro(model)
        FC.solve(forward_checking)
        # model.display_variables(solution)

        print("FC_MRV: ", end="")
        FC_MRV = Kakuro(model)
        solution = FC_MRV.solve(forward_checking, mrv)
        # model.display_variables(solution)

        # print("MAC: ", end="")
        # MAC = Kakuro(model)
        # solution = MAC.solve(mac)
        # # model.display_variables(solution)

        model.display_grid(solution)
        print("")
