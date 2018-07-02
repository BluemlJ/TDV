import pandas as pd

import math_functions
from objects.datapoint import Datapoint


def floyd_warshall(grid):
    """ dist[][] will be the output matrix that will finally
        have the shortest distances between every pair of vertices
        initializing the solution matrix same as input graph matrix
        OR we can say that the initial values of shortest distances
        are based on shortest paths considerting no
        intermedidate vertices
    """
    # noinspection PyPep8Naming
    INF = 999999
    dist = [[INF for x in range(len(grid.list_of_cells))] for y in range(len(grid.list_of_cells))]
    for cell_id in range(len(grid.list_of_cells)):
        cell1 = grid.get_cell(cell_id=cell_id)
        for dN in cell1.direct_neighbours:
            dist[cell_id][dN.id] = math_functions.calc_distance_2D(grid, cell1, dN)
        dist[cell_id][cell_id] = 0
    print(dist)

    for k in range(len(grid.list_of_cells)):
        print(k)
        # pick all vertices as source one by one
        for i in range(len(grid.list_of_cells)):
            # Pick all vertices as destination for the
            # above picked source
            for j in range(len(grid.list_of_cells)):
                dist[i][j] = min(dist[i][j],
                                 dist[i][k] + dist[k][j]
                                 )

    new_csv = pd.DataFrame(dist)
    pd.DataFrame.to_csv(new_csv, 'dmmatrix.csv', index=int, header=None)

    # disttodist(dist, grid, 'csvs/tsne.csv', 'result.csv')
    calc_neighborhood_preservation(dist, grid, 'csvs/FCPS/atom_pca.csv', 'result.csv')


def print_solution(dist):
    """
    This Method helps to print the solution in a readable form
    :param dist: the distance matrix
    """
    print("Following matrix shows the shortest distances between every pair of vertices")
    for i in range(len(dist)):
        for j in range(len(dist)):
            if dist[i][j] == 999999:
                print("INF ,", end='')
            else:
                print(dist[i][j], ",", end='')
            if j == len(dist) - 1:
                print("")


def disttodist(distmatrix, grid, list_of_points_before, list_of_points_after):
    """
    This method calculates a distance to distance evaluation. It compares every distance between points and calculates
    the difference after the dimensional reduction
    :param distmatrix: the distance matrix for the original dataset
    :param grid: the grid of our approach
    :param list_of_points_before: lists of points before iteration 0
    :param list_of_points_after:  lists of point after n iterations
    :return: prints out the difference
    """
    import math

    inputframe = pd.read_csv(list_of_points_before, index_col=0, header=None)
    outputframe = pd.read_csv(list_of_points_after, index_col=0, header=None)

    dred_val = inputframe.values
    listof_points = []
    tdv_val = outputframe.values
    listof_points2 = []

    for index in range(0, len(dred_val)):
        listof_points.append(Datapoint.from_csv(dred_val[index:index + 1]))

    for index in range(0, len(tdv_val)):
        listof_points2.append(Datapoint.from_csv(tdv_val[index:index + 1]))

    dist_in_org = []
    dist_after_dim_red = []
    dist_after_tdv = []
    for i in range(len(listof_points)):
        point = listof_points[i]
        for j in range(len(listof_points)):
            point2 = listof_points[j]
            dist_in_org.append(math_functions.calc_distance_nD(point.data, point2.data)[0])
            dist_after_dim_red.append(
                math.sqrt(math.pow(point.x_axis - point2.x_axis, 2) + math.pow(point.y_axis - point2.y_axis, 2)))
            dist_after_tdv.append(
                distmatrix[grid.get_cell(point=listof_points2[i]).id][grid.get_cell(point=listof_points2[j]).id])

            # print(point.x_axis, point2.x_axis, point.x_org, point2.x_org)
    max1 = max(dist_in_org)
    tmp = [a / max1 for a in dist_in_org]
    dist_in_org = tmp

    max1 = max(dist_after_dim_red)
    tmp = [a / max1 for a in dist_after_dim_red]
    dist_after_dim_red = tmp

    max1 = max(dist_after_tdv)
    tmp = [a / max1 for a in dist_after_tdv]
    dist_after_tdv = tmp

    dif1 = 0
    dif2 = 0
    for a in range(len(dist_in_org)):
        print(a, "DORG:", dist_in_org[a], "DDIMRED", dist_after_dim_red[a], "DTDV", dist_after_tdv[a])
        dif1 = dif1 + abs(dist_in_org[a] - dist_after_dim_red[a])
        dif2 = dif2 + abs(dist_in_org[a] - dist_after_tdv[a])


def calc_neighborhood_preservation(distmatrix, grid, list_of_points_before, list_of_points_after):
    """
    Calculates the difference between the neighbourhoods in the original high dimensional dataset and the neighbourhoods
    in after the dimensional reduction. This method prints the differences to evaluate different approaches
    :param distmatrix: the distance matrix
    :param grid: the grid to use
    :param list_of_points_before: the list of points before iterartion 0
    :param list_of_points_after:  the list of points after n iterations
    :return: the difference between the high dimensional and 2 dimensional space in form of neighbourhood preservation
    """
    import math

    inputframe = pd.read_csv(list_of_points_before, index_col=0, header=None)
    outputframe = pd.read_csv(list_of_points_after, index_col=0, header=None)

    dred_val = inputframe.values
    listof_points = []
    tdv_val = outputframe.values
    listof_points2 = []

    for index in range(0, len(dred_val)):
        listof_points.append(Datapoint.from_csv(dred_val[index:index + 1]))
    for index in range(0, len(tdv_val)):
        listof_points2.append(Datapoint.from_csv(tdv_val[index:index + 1]))

    dist_in_org = []
    dist_after_dim_red = []
    dist_after_tdv = []
    for i in range(len(listof_points)):
        point = listof_points[i]
        for j in range(len(listof_points)):
            point2 = listof_points[j]
            dist_in_org.append(math_functions.calc_distance_nD(point.data, point2.data)[0])
            dist_after_dim_red.append(
                math.sqrt(math.pow(point.x_axis - point2.x_axis, 2) + math.pow(point.y_axis - point2.y_axis, 2)))
            dist_after_tdv.append(
                distmatrix[grid.get_cell(point=listof_points2[j]).id][grid.get_cell(point=listof_points2[i]).id])

    max_distance_in_org = max(dist_in_org)
    max_distance_in_red = max(dist_after_dim_red)
    max_distance_after_tdv = max(dist_after_tdv)

    avg_precision1 = 0
    avg_recall1 = 0
    avg_precision2 = 0
    avg_recall2 = 0
    lenghtof_reduction = 0
    leghttof_tdv = 0
    lenghtof_orginal = 0

    for i in range(len(listof_points)):
        point = listof_points[i]
        neighbourhood_in_o = []
        neighbourhood_in_r = []
        neighbourhood_in_tdv = []
        for j in range(len(listof_points)):
            point2 = listof_points[j]
            if math_functions.calc_distance_nD(point.data, point2.data)[0] / max_distance_in_org < 0.1:
                neighbourhood_in_o.append(point2)
            if (math.sqrt(math.pow(point.x_axis - point2.x_axis, 2) + math.pow(point.y_axis - point2.y_axis,
                                                                               2)) / max_distance_in_red < 0.1):
                neighbourhood_in_r.append(point2)
            if distmatrix[grid.get_cell(
                    point=listof_points2[i]).id][grid.get_cell(
                        point=listof_points2[j]).id] / max_distance_after_tdv < 0.1:
                neighbourhood_in_tdv.append(point2)
        lenghtof_reduction += len(neighbourhood_in_r)
        leghttof_tdv += len(neighbourhood_in_tdv)
        lenghtof_orginal += len(neighbourhood_in_o)

        from collections import Counter
        print(i, len(neighbourhood_in_o), len(neighbourhood_in_r), len(neighbourhood_in_tdv))
        counter1 = Counter(neighbourhood_in_o)
        counter2 = Counter(neighbourhood_in_r)
        false_neighbours1 = len(list(counter2 - counter1)) / len(neighbourhood_in_r)
        precision = 1 - false_neighbours1
        avg_precision1 += precision
        miss1 = len(list(counter1 - counter2)) / len(neighbourhood_in_o)
        avg_recall1 += (1 - miss1)

        counter2 = Counter(neighbourhood_in_tdv)
        false_neighbour2 = len(list(counter2 - counter1)) / len(neighbourhood_in_tdv)
        precision = 1 - false_neighbour2
        avg_precision2 += precision
        miss2 = len(list(counter1 - counter2)) / len(neighbourhood_in_o)
        avg_recall2 += (1 - miss2)

    avg_precision1 = avg_precision1 / len(listof_points)
    avg_precision2 = avg_precision2 / len(listof_points)
    avg_recall1 = avg_recall1 / len(listof_points)
    avg_recall2 = avg_recall2 / len(listof_points)
    avg_neigbourhood_size1 = lenghtof_reduction / len(listof_points)
    avg_neigbourhood_size2 = leghttof_tdv / len(listof_points)
    avg_neigbourhood_size3 = lenghtof_orginal / len(listof_points)

    print("Precision of R:", avg_precision1)
    print("Precision of T:", avg_precision2)
    print("Recall of R:", avg_recall1)
    print("Recall of T:", avg_recall2)
    print("avg Neighbourhoodsize of R:", avg_neigbourhood_size1)
    print("avg Neighbourhoodsize of T", avg_neigbourhood_size2)
    print("avg Neighbourhoodsize of 0", avg_neigbourhood_size3)
