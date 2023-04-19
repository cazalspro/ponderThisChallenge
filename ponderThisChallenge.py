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

		model.rows = pe.Set(initialize = set(range(0,self.matrixSize)))
		model.cols = pe.Set(initialize = set(range(0,self.matrixSize)))

		#Initial state matrix generation

		model.initialState = pe.Param(model.rows, model.cols, initialize = self.initialMatrix, default = 0)

		# Variable declaration

		model.x = pe.Var(model.rows, model.cols, domain = pe.Binary)

		# Objective function

		expr = sum(model.x[l,c] for l in model.rows for c in model.cols)
		model.objective = pe.Objective(sense = pe.minimize, expr = expr)

		# Constraint 1 : Final state is a 1-matrix

		model.constraint1 = pe.ConstraintList()
		    
		    #Variable list for computing modulos
		model.varMod = pe.Var(model.rows, model.cols, domain = pe.Integers)

		    #Constraint
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
		solver.solve(self.model, tee=True)

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

		print((df['etatInitial']).unstack('col'))
		print((df['x']).unstack('col'))
		#print((df['x']).groupby('row').sum().to_frame())
		#print(df['x'].groupby('col').sum().to_frame().T)





test = Instance("matrice.txt")
test.genereMIP()
test.solveInstance()
test.printSol()
print(test.checkSol())


