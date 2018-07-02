import logging.config
import pandas as pd
import math_functions as mf
from objects.grid import Grid
import draw_image as di

# The input file, a csv with index, without header. First two columns are x and y.
INPUT_CSV: str = 'example/isolet_tsne.csv'
# The output file, a csv with index, without header, First three columns are x,y and z.
OUTPUT_CSV: str = 'example/result.csv'
# Number of rows
ROWS: int = 22
# Number of rows
ITERATIONS: int = 10
# Number of columns, if None, ROWS will be used instead
COLUMNS: int or None = None
# Start value for x (mostly 0-1/rows)
STARTX: int or None = None
# Start value for y (mostly 0-1/rows)
STARTY: int or None = None
# If True, the topogram will draw the centerpoints for each cell
DRAW_CENTERS: bool = False
# If True, the topogram will draw every point
DRAW_POINTS: bool = False
# Number of layers for the topogram
LEVELCOUNT: int = 7
# Color map to use for heatmap and topogram
COLOR_MAP: str = 'gist_earth'
# If True, the topogram takes the OUTPUT_CSV and the points instead of the centerpoints from the cells
TAKE_POINTS_INSTEAD_OF_GRID: bool = False
# The maximal distance for the initial neighbourhood. Will be multiplied with 1/rows
MAX_DISTANCE: int = 5
# The percentage indication when to cut the lists of highest error and highest icv. Will be multiplied with 1/100
CUT_LIST_AT: int = 75


def iteration(grid, list_to_manipulate):
    logger.debug("new iteration started")

    for cell in list_to_manipulate:
        cell.localerror = cell.calc_localerror()
        logger.debug("calculate localerror for '%i' with LE = '%f' ", cell.id, cell.localerror)

    logger.info("------------------Calculation of localerror finished")
    logger2.debug("------------------Calculation of localerror finished")

    cell_with_high_errors = grid.sort_and_cut(percent=CUT_LIST_AT)
    cell_with_ICVs = grid.sort_and_cut(percent=CUT_LIST_AT, searchparameter=lambda cell: cell.ICV)

    for cell in cell_with_high_errors:
        grid.set_mountains({cell.id: mf.calc_mountain_height(cell=cell, neutral_variance=grid.neutral_variance)})
        logger.debug("calulate new height for '%i' = '%f', with LE = '%f'", cell.id, cell.height, cell.localerror)

    logger.info("------------------Mountains set")
    logger2.debug("------------------Mountains set")

    for cell in list_to_manipulate:
        cell.neighbourhood = grid.calc_neighbourhood(cell=cell, max_distance=MAX_DISTANCE)
        logger.debug("NEIGHBOURHOOD calculation for cell '%i' finished '%s'", cell.id, cell.print_neighbourhood())

    logger.info("------------------Neighbourhood calculation finished")
    logger2.debug("------------------Neighbourhood calculation finished")

    nos = 0
    for cell in cell_with_ICVs:
        nos += cell.shift_points()

    logger2.debug("Number of Shifts: '%d', Shifts done.", nos)
    logger.info("------------------Shifts done")

    list_of_new_reps = []
    for cell in list_to_manipulate:
        list_of_new_reps.append(cell.manipulate_representative())
    for pair in list_of_new_reps:
        pair[0].representative = pair[1]
        # logger.debug("manipulation of cell representative of '%i' with '%s' finished", pair[0].id, pair[1])

    logger.info("------------------Manipulation is finished")
    logger2.debug("------------------Manipulation is finished")

    global_icv = 0
    for cell in grid.list_of_cells:
        global_icv += cell.ICV
    logger2.debug("Global ICV ist '%f'", global_icv)

    numer_of_empty_cells = 0
    for cell in grid.list_of_cells:
        if not cell.list_of_points:
            numer_of_empty_cells += 1

    tmp = numer_of_empty_cells / len(grid.list_of_cells)
    logger2.debug("------------------ '%f' of cells are empty", tmp)

    return grid.list_of_cells


if __name__ == '__main__':

    # detailed logger for logfile.txt
    logger = logging.getLogger('main')
    # minimal logger for logfile2.txt
    logger2 = logging.getLogger('main2')
    logging.config.fileConfig(fname='logger_config.ini', disable_existing_loggers=False)

    input_dataset = pd.read_csv(INPUT_CSV, index_col=0, header=None)
    dimensions = input_dataset.shape[1] - 2

    # generate grid
    grid = Grid.autogenerated(rows=ROWS, columns=COLUMNS, dimension=dimensions, start_x=STARTX, start_y=STARTY)

    # init points
    grid.init_points_to_right_cell(input_dataset)
    di.draw_scatterplot(grid.get_all_points())

    # init representative
    for cell in grid.list_of_cells:
        cell.calc_representative()
    for cell in grid.list_of_cells:
        cell.calc_representative(cells_with_points=False, empty_cells=True)

    logger.info("------------------Representative calculation finished")
    logger.info("NEUTRAL VARIANCE is calculated: '%f' ", grid.neutral_variance)
    logger2.debug("NEUTRAL VARIANCE is calculated: '%f' ", grid.neutral_variance)

    tmp_list = grid.list_of_cells
    for i in range(ITERATIONS):
        tmp_list = iteration(grid, tmp_list)
        globalE = 0
        for neuron in grid.list_of_cells:
            globalE += neuron.localerror

        logger.info(
            "---------------------------------------Iteration '%i' finished with '%f' "
            "------------------------------------\n",
            i + 1, globalE)
        logger2.debug("Iteration '%i' finished with '%f' \n", i, globalE)

    # sort the points in the original order (like the original dataset)
    points = []
    c = 0
    index = []
    for point in grid.get_all_points():
        df = (input_dataset.loc[input_dataset[1] == point.x_org])
        index.append(df.index.tolist())
        points.append([point.x_axis + c, point.y_axis + c, grid.get_cell(point=point).height])

    import itertools

    merged = list(itertools.chain(*index))
    mergeIn = [0 for i in merged]
    mergeIn.append(0)
    mergeIn.append(0)

    for num in range(0, len(merged)):
        mergeIn[merged[num] - 1] = num

    input_dataset = input_dataset.reindex(merged)
    input_dataset = input_dataset.reset_index(drop=True)

    tmp = pd.DataFrame(points, columns=['dred1', 'dred2', 'heights'])
    tmp2 = input_dataset.drop(columns=1, axis=1)
    tmp2 = tmp2.drop(columns=2, axis=1)

    # generates the output csv
    new_csv = pd.concat([tmp, tmp2], axis=1)
    new_csv = new_csv.reindex(mergeIn)
    new_csv = new_csv.reset_index(drop=True)
    pd.DataFrame.to_csv(new_csv, OUTPUT_CSV, index=int, header=None)

    # Evaluate
    # eval.floydWarshall(grid)

    # Visualize
    di.draw_scatterplot(grid.get_all_points())
    di.draw_heatmap(grid, cm=COLOR_MAP)
    di.draw_heatmap(grid, heights=True, gaussian=True, cm=COLOR_MAP)
    di.draw_heatmap(grid, heights=True, gaussian=False, cm=COLOR_MAP)

    di.draw_topogram(grid, drawcenters=DRAW_CENTERS, drawpoints=grid.get_all_points() if DRAW_POINTS else None,
                     levelcount=LEVELCOUNT, colormap=COLOR_MAP)

    di.draw_topogram(grid, inputfile=OUTPUT_CSV if TAKE_POINTS_INSTEAD_OF_GRID else None, drawcenters=DRAW_CENTERS,
                     drawpoints=grid.get_all_points() if DRAW_POINTS else None,
                     levelcount=LEVELCOUNT, colormap=COLOR_MAP)