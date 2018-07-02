import logging
import math
import numpy as np

# logger1 for logging in logfile.txt
logger = logging.getLogger('math')


def calc_distance_2D(grid, cell, neighbour):
    """
    Calculates the distance between a cell and a neighbour in the dimensional reduction space.

    Raises:
        ValueError raises a ValueError if the neighbour is not in the list of neighbours from the first cell

    :param grid: the grid to work on
    :param cell: the first cell
    :param neighbour: the second cell
    :return: the distance between the two points
    """
    is_direct_neighbour = False
    for c in cell.direct_neighbours:
        if c == neighbour:
            is_direct_neighbour = True
            break

    if is_direct_neighbour:
        return grid.cellwidth + pow(cell.height - neighbour.height, 2)
        # alternative version:
        # E1
        # return 1 + pow(cell.height - neighbour.height, 2)

    else:
        for pair in grid.get_cell(cell_id=cell.id).neighbourhood:
            if pair[0] == neighbour:
                return pair[1]
        raise ValueError
        pass


def calc_distance_nD(inputvector, inputvector2):
    """
    this method calculates the distance between our grid and an input vector with an given measure.

    Args:
        :param inputvector: a n dimensional data vector, with n = dimensions in our input
        :param inputvector2: the n dimensional representative, with n = dimensions in our input

    Returns:
        :return: returns the diversity between inputvector and neuron in form of [sum(error_i²), [error_1,error_2,...]]

    Raises:
        None

    Needs:
        None

    """

    error = [(a - b) for a, b in zip(inputvector, inputvector2)]
    array = np.array(error)
    e = np.linalg.norm(array)  # euclidian norm
    e = pow(e, 2)
    return [e, error]


def calc_neutral_variance(grid, n):
    """
    Calculates the neutral variance
    :param grid: the grid to work on
    :param n: the number of dimensions
    :return: the neutral variance
    """
    return n / 12 * ((1 / (grid.rows * grid.columns)) ** (n ** -1))


def calc_mountain_height(cell, neutral_variance):
    """
    Calculates a new height for the cell. The new height will minimize the localerror.
    :param cell: the cell to calculate the error for
    :param neutral_variance: the neutral variance from the grid
    :return: the new height
    """

    sum_of_weights = 0

    for neighbour in cell.direct_neighbours:
        sum_of_weights += len(neighbour.list_of_points)

    if sum_of_weights == 0:
        return 0

    f = [1 for x in cell.direct_neighbours]  # prefactor (not used)
    h = [x.height for x in cell.direct_neighbours]  # Heights
    r = [neutral_variance / max(neutral_variance, cell.ICV) * math.sqrt(
        calc_distance_nD(cell.representative, x.representative)[0]) for x in
         cell.direct_neighbours]  # representatives

    a = np.real(4 * sum(f))
    b = np.real(-12 * sum([fi * hi for fi, hi in zip(f, h)]))
    c = np.real(4 * cell.grid.cellwidth * sum(f) - 4 * sum([fi * ri for fi, ri in zip(f, r)]) + 12 * sum(
        [fi * hi ** 2 for fi, hi in zip(f, h)]))
    d = np.real(
        -4 * cell.grid.cellwidth * sum([fi * hi for fi, hi in zip(f, h)]) + 4 * sum(
            [fi * hi * ri for fi, hi, ri in zip(f, h, r)]) - 4 * sum(
            [fi * hi ** 3 for fi, hi in zip(f, h)]))

    ppar = [a, b, c, d]
    roots = np.roots(ppar)
    logger.debug("Roots calculated: '%s'", roots)

    roots = roots[np.isreal(roots)]

    dic = {}
    for root in roots:
        if root >= -0.1:
            dic.update({root: cell.calc_localerror(height_to_test=root)})

    if not dic:
        for root in roots:
            dic.update({root: cell.calc_localerror(height_to_test=root)})

    minmum = min(dic.items(), key=lambda x: x[1])
    return np.real(minmum[0])
