import usefulFunctions as fn
import pyomo.environ as pe
import pyomo.opt as po
import pandas as pd
import ast
import math


class Instance:
	def __init__(self, fileName):
		self.initialMatrix = ast.literal_eval(fn.parseMatrix(fileName))
		self.matrixSize = int(math.sqrt(len(self.initialMatrix)))
		self.model = None

	def playMove(self, currentMatrix, move):
		for i in range(self.matrixSize):
			currentMatrix[i,move[1]] = 1 - currentMatrix[i,move[1]]
		for j in range(self.matrixSize):
			currentMatrix[move[0],j] = 1 - currentMatrix[move[0],j]
		currentMatrix[move[0],move[1]] = 1 - currentMatrix[move[0],move[1]]

	def playSolution(self):
		matrix = self.initialMatrix
		for i in self.model.x:
				if pe.value(self.model.x[i]) == 1:
					self.playMove(matrix, i)
		fn.printDictionary(matrix)

	

	def solveInstance(self):
		solver = pe.SolverFactory('glpk')
		solver.solve(self.model, tee = True)

	def printSol(self):
		print("Initial Matrix")
		fn.printDictionary(self.model.initialState)
		print("Turned on bulbs")
		fn.printPyomoDictionary(self.model.x)
		print("Final state")
		self.playSolution()

	def test(self):
		self.genereMIP()
		self.solveInstance()
		self.printSol()

	def genereMIP(self):

		#Model generation

		model = pe.ConcreteModel()

		#Index generation

		model.rows = pe.Set(initialize = range(0,self.matrixSize))
		model.cols = pe.Set(initialize = range(0,self.matrixSize))

		#Initial state matrix generation

		model.initialState = pe.Param(model.rows, model.cols, initialize = self.initialMatrix, default = 0)

		# Variable declaration

		model.x = pe.Var(model.rows, model.cols, domain = pe.Binary)

		# Objective function, aim at minimizing the sum of the variables

		expr = sum(model.x[l,c] for l in model.rows for c in model.cols)
		model.objective = pe.Objective(sense = pe.minimize, expr = expr)

		# Constraint 1 : Final state is a 1-matrix
		# for each element (x,y) of the matrix, check that the sum of the light bulbs lit in the row x and the column y plus the intial state of (x,y) are congruent to 1 mod 2

		model.constraint1 = pe.ConstraintList()
		    
		    #Variable list for computing modulos
		model.varMod = pe.Var(model.rows, model.cols, domain = pe.Integers)

		    #Constraints adding
		for l in model.rows:
			for c in model.cols:
				sumCurrentRows = sum(model.x[ltmp,c] for ltmp in model.rows)
				sumCurrentCols = sum(model.x[l,ctmp] for ctmp in model.cols)
				currentValue = model.x[l,c]
				initialCurrentValue = model.initialState[l,c]

				lhs = sumCurrentRows + sumCurrentCols - currentValue + initialCurrentValue
				rhs = 2*model.varMod[l,c] + 1
				model.constraint1.add(lhs == rhs)


		self.model = model




instanceTest = Instance("matrix.txt")
instanceTest.test()








