matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
sum_diagonal = 0
for i in range(3):
    for j in range(3):
        if i == j:
            sum_diagonal += matrix[i][j]
print(sum_diagonal)


