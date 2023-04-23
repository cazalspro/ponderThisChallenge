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
		self.bigM = 10000

	def playMove(self, currentMatrix, move):
		for i in range(self.matrixSize):
			currentMatrix[i,move[1]] = 1 - currentMatrix[i,move[1]]
		for j in range(self.matrixSize):
			currentMatrix[move[0],j] = 1 - currentMatrix[move[0],j]
		currentMatrix[move[0],move[1]] = 1 - currentMatrix[move[0],move[1]]

	def playSolution(self):
		matrix = self.initialMatrix
		for i in self.model.x:
				if pe.value(self.model.x[i]) == 1: # and matrix[i] == 0
					self.playMove(matrix, i)
		fn.printDictionary(matrix)

	def solveInstance(self):
		solver = pe.SolverFactory('glpk')
		solver.solve(self.model, tee = True)

	def printSol(self):
		print("Initial Matrix")
		fn.printDictionary(self.model.initialState)
		print("Turned on bulbs")
		#fn.printPyomoDictionary(self.model.x)
		self.printVar()
		print("Final state")
		#self.playSolution()

	def test(self):
		self.genereMIP()
		self.solveInstance()
		self.printSol()

	def writeLpFile(self):
		self.genereMIP()
		self.model.write("model.lp")

	def printVar(self):
		sol = []
		for s in self.model.slots:
			for l in self.model.rows:
				for c in self.model.cols:
					if pe.value(self.model.x[l,c,s]) == 1:
						sol.append([l,c,s])
		print(sol)

	def genereMIP(self):

		#Model generation

		model = pe.ConcreteModel()

		#Index generation

		model.rows = pe.Set(initialize = range(0,self.matrixSize))
		model.cols = pe.Set(initialize = range(0,self.matrixSize))
		model.slots = pe.Set(initialize = range(0,self.matrixSize ** 2))

		#Initial state matrix generation

		model.initialState = pe.Param(model.rows, model.cols, initialize = self.initialMatrix, default = 0)

		# Variable declaration

		model.x = pe.Var(model.rows, model.cols, model.slots, domain = pe.Binary)

		# Objective function, aim at minimizing the sum of the variables

		expr = sum(model.x[l,c,s] for l in model.rows for c in model.cols for s in model.slots)
		model.objective = pe.Objective(sense = pe.minimize, expr = expr)

		# Constraint : Final state is a 1-matrix
		# for each element (x,y) of the matrix, check that the sum of the light bulbs lit in the row x and the column y plus the intial state of (x,y) are congruent to 1 mod 2

		model.constraint1 = pe.ConstraintList()
		    
		    #Variable list for computing modulos
		model.varMod = pe.Var(model.rows, model.cols, domain = pe.Integers)

		    #Constraints adding
		for l in model.rows:
			for c in model.cols:
				sumCurrentRows = sum(model.x[ltmp,c,s] for ltmp in model.rows for s in model.slots)
				sumCurrentCols = sum(model.x[l,ctmp,s] for ctmp in model.cols for s in model.slots)
				currentValue = sum(model.x[l,c,s] for s in model.slots)
				initialCurrentValue = model.initialState[l,c]

				lhs = sumCurrentRows + sumCurrentCols - currentValue + initialCurrentValue
				rhs = 2*model.varMod[l,c] + 1
				model.constraint1.add(lhs == rhs)
		

		#Constraint : Only turned off bulbs are turned on

			#For each s1, sum operation s2 < s1 is equal to 0 mod 2

		model.constraint2 = pe.ConstraintList()

		model.varMod2 = pe.Var(model.rows, model.cols, model.slots, domain = pe.Integers)

		for s in model.slots:
			if s >= 1:
				for l in model.rows:
					for c in model.cols:
						#Sum of the lamp ignitions of a column c for the time windows before s
						sumCurrentRows = sum(model.x[ltmp,c,stmp] for ltmp in model.rows for stmp in range(s))
						#Sum of the lamp ignitions of a rows l for the time windows before s
						sumCurrentCols = sum(model.x[l,ctmp,stmp] for ctmp in model.cols for stmp in range(s))
						# sumCurrentcols \cap sumCurrentrows
						sumCountedTwice = sum(model.x[l,c,stmp] for stmp in range(s))
						
						currentValue = model.x[l,c,s]
						initialCurrentValue = model.initialState[l,c]

						lhs = sumCurrentRows + sumCurrentCols - sumCountedTwice + initialCurrentValue
						#Two operations in one
						#(1-currentValue)*self.bigM represents the if currentvalue ==1
						#2*model.varMod2[l,c,s] represents the modulo 2
						rhsSup = 2*model.varMod2[l,c,s] + (1-currentValue)*self.bigM
						rhsInf = 2*model.varMod2[l,c,s] - (1-currentValue)*self.bigM
						model.constraint2.add(lhs <= rhsSup)
						model.constraint2.add(lhs >= rhsInf)
				




			#For each time slot s, one operation is allowed

		model.constraint3 = pe.ConstraintList()

		for s in model.slots:
			lhs = sum(model.x[l,c,s] for l in model.rows for c in model.cols)
			rhs = 1
			model.constraint2.add(lhs <= rhs)

			# Each operation is affected to only one slot

		model.constraint4 = pe.ConstraintList()
		for l in model.rows:
			for c in model.cols:
				lhs = sum(model.x[l,c,s] for s in model.slots)
			rhs = 1
			model.constraint3.add(lhs <= rhs)



		self.model = model




instanceTest = Instance("matrix.txt")

#instanceTest.writeLpFile()
instanceTest.test()








