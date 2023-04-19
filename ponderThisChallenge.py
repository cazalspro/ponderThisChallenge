import fonctionGestion as fn
import pyomo.environ as pe
import pyomo.opt as po
import pandas as pd
import ast
import math


class Instance:
	def __init__(self, fileName):
		self.initialMatrix = ast.literal_eval(fn.parse_Matrix('matrix.txt'))
		self.matrixSize = int(math.sqrt(len(self.initialMatrix)))
		self.model = None

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

	def solveInstance(self):
		solver = pe.SolverFactory('glpk')
		solver.solve(self.model, tee = True)

	def checkSol(self):
		correct = True
		for l in self.model.rows:
			for c in self.model.cols:
				a = sum(pe.value(self.model.x[ltmp,c]) for ltmp in self.model.rows) + sum(pe.value(self.model.x[l,ctmp]) for ctmp in self.model.cols) - pe.value(self.model.x[l,c]) + pe.value(self.model.initialState[l,c])
				if a % 2 == 0:
					correct = False
		return correct




	def printSol(self):
		model = self.model

		df = pd.DataFrame(index = pd.MultiIndex.from_tuples(model.x,names = ['row','col']))
		df['x'] = [pe.value(model.x[key]) for key in df.index]
		df['etatInitial'] = [model.initialState[key] for key in df.index]

		print("Initial Matrix")
		print((df['etatInitial']).unstack('col'))
		print("Turned on bulbs")
		print((df['x']).unstack('col'))





test = Instance("matrice.txt")
test.genereMIP()
test.solveInstance()
test.printSol()
print("Solution is correct ?")
print(test.checkSol())


