





def parse_Matrix(fileName):
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