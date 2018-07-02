import logging
import matplotlib.pyplot as plt
import scipy.ndimage as sp
import numpy as np

logger = logging.getLogger(__name__)


def draw_topogram(grid, inputfile=None, drawcenters=False, drawpoints=None, levelcount=7, colormap='gist_earth',):
    """
    This method draws a topogram of a grid.
    :param grid: the grid to visualize
    :param inputfile: if a file is given, we use the points in this csv instead of the grid.
    :param drawcenters: if True, the topogram shows the centerpoints of the cells
    :param drawpoints: the topogram shows the given data points
    :param levelcount: the levelcount is uses to set how many layers the contour plot will have. The default is 7
    :param colormap: the colormap to use. The default is gist_earth
    :return: It draws the topogram
    """


    points = []
    if inputfile:
        for line in open(inputfile):
            list = line.split(",")
            points.append([list[1], list[2], list[3]])
    else:
        for cell in grid.list_of_cells:
            points.append([cell.posx, cell.posy, cell.height])

    from matplotlib.mlab import griddata  # interpolation of my data for better mountains

    # matplotlib.griddata needs numPy arrays, so we change the data type to numpy array.
    array_with_x_coordinates = np.array([x[0] for x in points])
    array_with_y_coordinates = np.array([x[1] for x in points])
    array_with_z_coordinates = np.array([x[2] for x in points])

    # define grid
    grid_x_axis = np.linspace(0, 1, 80)
    grid_y_axis = np.linspace(0, 1, 80)

    fig = plt.figure()
    ax = fig.gca()
    # ax.set_xticks(grid_x_axis)
    # ax.set_yticks(grid_y_axis)
    plt.title('griddata')

    # grid the data.
    # noinspection PyTypeChecker
    zi = griddata(array_with_x_coordinates, array_with_y_coordinates, array_with_z_coordinates, grid_x_axis,
                  grid_y_axis, interp='linear')

    # contour the gridded data, plotting dots at the nonuniform data points.
    plt.contour(grid_x_axis, grid_y_axis, zi, levelcount, linewidths=0.2, colors='k')
    plt.contourf(grid_x_axis, grid_y_axis, zi, levelcount, vmax=abs(zi).max(), vmin=-abs(zi).max(),
                 cmap=plt.cm.get_cmap(colormap))

    # draw colorbar
    plt.colorbar()

    # plot data points.
    if drawcenters:
        plt.scatter(array_with_x_coordinates, array_with_y_coordinates, marker='o', s=5, zorder=10)

    if drawpoints:
        ax.scatter([x.x_axis for x in drawpoints], [x.y_axis for x in drawpoints], marker='o', s=1, zorder=10,
                   color='#fb2943')

    # plt.grid()
    plt.savefig('images/topogram.png', papertype='a4', dpi=300)
    plt.show()

def draw_heatmap(grid, heights=False, gaussian=False, cm='gist_earth'):
    """
    This method draws a heatmap. The default is to visualize the localerrors for every cell.
    :param grid: the grid to visualize
    :param heights: If heights is true, the heights will be used instead of the localerror.
    :param gaussian: If gaussian is true, the visualizing will be blured.
    :param cm: the colormap to use. The default is gist earth
    :return: it shows the map
    """

    tmp = []
    counter = 0
    array = []

    for neuron in grid.list_of_cells:
        counter += 1
        if not heights:
            if not len(neuron.list_of_points):
                tmp.append(0)
            else:
                tmp.append(neuron.localerror)
        else:
            tmp.append(neuron.height)
        if counter == grid.rows:
            array.append(tmp)
            tmp = []
            counter = 0

    error_map = np.array(array)
    if gaussian:
        error_map = sp.filters.gaussian_filter(error_map, sigma=2, order=0)

    if not heights:
        fig = plt.imshow(error_map, cmap=cm, interpolation='nearest', vmin=0)
        cb = plt.colorbar()
        cb.set_label('localerror')
    else:
        fig = plt.imshow(error_map, cmap=plt.cm.get_cmap(cm), interpolation='nearest', vmin=0)
        cb = plt.colorbar()
        cb.set_label('height')

    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)

    plt.savefig('images/localheatmap.png', papertype='a4', dpi=300)
    plt.show()


def draw_isochrone(grid, cell, max_distance, colormap='binary'):
    """
    Draws an isochrone for the given cell
    :param grid: the grid to work on
    :param cell:  the cell to work on
    :param max_distance: the maximal distance
    :param colormap: the colormap to use. The default is black and white
    :return: a heatmap visualizing the distances from one cell to his neighbours
    """

    data = grid.calc_neighbourhood(max_distance=max_distance, neuron=cell)

    tmp = []
    counter = 0
    array = []

    for cell in grid.list_of_neurons:
        counter += 1
        is_element = False
        for distance in data:
            if cell == distance[0]:
                tmp.append(distance[1])
                is_element = True
        if not is_element:
            tmp.append(2 * max_distance)
        if counter == grid.rows:
            array.append(tmp)
            tmp = []
            counter = 0

    error_map = np.array(array)

    fig = plt.imshow(error_map, cmap=colormap, interpolation='nearest', vmin=0)
    cb = plt.colorbar()
    cb.set_label('path costs')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.savefig('images/isochrone_1.png', papertype='a4', dpi=300)
    plt.show()


def draw_scatterplot(points):
    """Draws a scatterplot with the given points.
    Retrieves a list of triples (x,y,z) or tuples (x,y) and returns a scatterplot.

    Args:
        :param points: a list of 2D-Coordinates given as triples or tuples (third dimension is ignored)
    Returns:
        :return An image in form of an matplotlib.pyplot

    Raises:
        None

    Needs:
        matplotlib.pyplot
    """
    if not isinstance(points, list):
        points = points.values

    fig = plt.figure()
    ax = fig.gca()
    ax.scatter([x.x_axis for x in points], [x.y_axis for x in points], marker='o', s=1)
    plt.grid()
    plt.show()

