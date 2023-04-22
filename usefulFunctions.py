import pandas as pd
import pyomo.environ as pe

def printDictionary(dictionnary):
	df = pd.DataFrame(index = pd.MultiIndex.from_tuples(dictionnary,names = ['row','col']))
	df['etatInitial'] = [dictionnary[key] for key in df.index]

	print((df['etatInitial']).unstack('col'))

def printPyomoDictionary(pyomoDict):
	df = pd.DataFrame(index = pd.MultiIndex.from_tuples(pyomoDict,names = ['row','col']))
	df['etatInitial'] = [pe.value(pyomoDict[key]) for key in df.index]

	print((df['etatInitial']).unstack('col'))



def parseMatrix(fileName):
    with open(fileName, "r") as f:
            lines = f.readlines()
            parsed_matrix = "{"
            posX = 0
            posY = 0
            for l in lines :
                    posY = 0
                    for c in l[:-1]:
                            parsed_matrix += "(" + str(posX) + "," + str(posY) + "):" + c + ","
                            posY +=1
                    posX += 1
            parsed_matrix = parsed_matrix[:-1]
            parsed_matrix += "}"
            return parsed_matrix