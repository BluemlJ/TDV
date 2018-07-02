import logging
import math
import pandas as pd
import math_functions as mf

# Logger1 logs everything in logfile.txt
logger = logging.getLogger('Cell')
# Logger2 logs a minimal set of information in logfile2.txt
logger2 = logging.getLogger('main2')


class Cell:
    """
    This class represents one cell in the grid. A cell is a group of points, represented by a representative. It has
    information about his neighbourhood, his homogeneity and height.
    It has 4 direct neighbours, a x and y position (lower left corner) and has a unique id.
    """

    def __init__(self,
                 id,
                 grid,
                 posx=0,
                 posy=0,
                 height=0):

        self.id = id
        self.posx = posx
        self.posy = posy
        self.height = height
        self.list_of_points = []
        self.neighbourhood = []
        self.direct_neighbours = []
        self.representative = []
        self.grid = grid
        self.ICV = 0

    def __eq__(self, other):
        """
        A cell is compared by his id. Is the id the same so the cell is the same
        :param other the id of the cell to compare
        :return: if the cells are equal
        """
        return self.id == other.id

    def __hash__(self):
        """
        the hashed key
        :return: a hashed key in form of the hashed id.
        """
        return hash(self.id)

    def add_point(self, point):
        """
        this method adds a point or a list of points to the list
        :param point: the points to add
        """
        if not self.list_of_points:
            self.list_of_points = [point]
        else:
            self.list_of_points.append(point)

    def calc_representative(self, cells_with_points=True, empty_cells=False):
        """
        This method calculates the representative. The representative is the mean value of all points
        :param cells_with_points: if true the representative of all cells with points are calculated. The default
        is True
        :param empty_cells: if true the representative of all empty cells are calculated. The default is False.
        """
        if self.list_of_points:
            # calculate the representative of all cells with points
            if cells_with_points:
                self.representative = self.points_to_dataframe(only_data=True).mean(axis=0)
                logger.debug("Cell '%i' has '%i' points", self.id, len(self.list_of_points))
                logger.debug("Cell '%i' finished calculation of rep '%s'", self.id, str(self.print_rep()))
                self.ICV = self.calc_ICV()[0]
                logger.debug("ICV for '%i' calculated: '%f'", self.id, self.ICV)

        # calculate the representative of all cells without points
        elif empty_cells:
            # How to calculate the Representative of an empty cell:
            # sum_n((len(direct-neighbour_n.list_of_points)*direct-neighbour_n.representative)/
            # sum_n(len(direct-neighbour_n.list_of_points)
            sum_of_elements = 0
            tmp = pd.Series()
            for cell in self.direct_neighbours:
                if not isinstance(cell.representative, list):
                    if not cell.representative.empty:
                        if tmp.empty:
                            tmp = cell.representative.mul(len(cell.list_of_points))
                        else:
                            tmp = tmp.add(cell.representative.mul(len(cell.list_of_points)))
                        sum_of_elements += len(cell.list_of_points)

            if sum_of_elements > 0:
                tmp = tmp.div(sum_of_elements)
                tmp = [a + 0.00000001 for a in tmp]  # adding an epsilon of 0.00000001

            self.representative = tmp

            logger.debug("Cell '%i' has no points = '%s'. The Rep is '%s' ", self.id, len(self.list_of_points) == 0,
                         self.print_rep())
            self.ICV = self.calc_ICV()[0]
            logger.debug("ICV for '%i' calculated: '%f'", self.id, self.ICV)

    def manipulate_representative(self):
        """
        This method manipulates the representative by bringing the representative closer to his neighbourhood.
        For this it calculates the distance between the representative and calculates
        a tmp_delta to add on the representative. the shorter the distance the bigger the influence of the neighbour
        """

        delta = []
        new_x = 0
        new_y = 0

        if not self.neighbourhood:
            return [self, self.representative]

        for neighbour in self.neighbourhood:
            neighbour = neighbour[0]
            dist = mf.calc_distance_2D(self.grid, self, neighbour)
            tmp_delta = [(rep - dimension) * (-1 / (1 + dist)) for dimension, rep in
                         zip(neighbour.representative, self.representative)]
            delta_x = 1 / (1 + dist) * (neighbour.posx - self.posx)
            delta_y = 1 / (1 + dist) * (neighbour.posy - self.posy)
            new_x = new_x + delta_x
            new_y = new_y + delta_y

        if delta:
            delta = [a + b for a, b in zip(delta, tmp_delta)]
        else:
            delta = tmp_delta

        sum_representative = [a + b / len(self.neighbourhood) for a, b in zip(self.representative, delta)]

        return [self, sum_representative]

    def shift_points(self):
        """
        This method shifts the points. Shifting means, it searches for a better representative in the neighbourhood for
        every points. If it founds some, it will remove the point and add it in the new cell.
        :return the number of shifts
        """

        i = 0
        list_to_remove = []
        list_to_add = []
        for point in self.list_of_points:
            in_neighbourhood = False
            for n in self.neighbourhood:
                if point.get_org() == n[0]:
                    in_neighbourhood = True
                    break
            if in_neighbourhood:
                best = [self, mf.calc_distance_nD(self.representative, point.data)]
                for neighbour in self.neighbourhood:
                    attemp = [neighbour[0], mf.calc_distance_nD(neighbour[0].representative, point.data)]
                    if attemp[1] < best[1]:
                        best = attemp
                if best[0] is not self:
                    list_to_remove.append(point)
                    best[0].list_of_points.append(point)
                    list_to_add.append(best[0])
                    i = i + 1

                point.add_shift(new_x_center=best[0].posx + best[0].grid.cellwidth / 2,
                                new_y_center=best[0].posy + best[0].grid.cellwidth / 2,
                                oldcenter=[self.posx + self.grid.cellwidth / 2, self.posy + self.grid.cellwidth / 2])

        for point in list_to_remove:
            self.list_of_points.remove(point)
            self.calc_representative()

        return i

    def calc_localerror(self, height_to_test=None):
        """
        This method calculates the localerror of the cell. It also has the possibility to calculate a hypothetical
        error when given a height as parameter.
        :param height_to_test: a height to test
        :return: the possible error, if height_to_test is None the actual error of this cell
        """
        sum_of_error = 0

        if height_to_test is not None:
            logger.debug("Test new height: '%f'", height_to_test)
            tmp = self.height
            self.height = height_to_test
        else:
            logger.debug("actual height: '%f'", self.height)

        for neighbour in self.direct_neighbours:

            error_neighbour = pow(math.sqrt(
                (self.grid.neutral_variance / max(self.grid.neutral_variance, self.ICV)) *
                mf.calc_distance_nD(self.representative, neighbour.representative)[0]) - mf.calc_distance_2D(self.grid,
                                                                                                             self,
                                                                                                             neighbour),
                                  2)

            '''
            Alternative implementations:
            #E1
            error_neighbour = pow(math.sqrt(
                mf.calc_distance_nD(self.representative, neighbour.representative)[0])
                     - mf.calc_distance_2D(self.grid, self, neighbour), 2)
            
            #E2
            error_neighbour = pow(math.sqrt(
                (1 / max(1, self.ICV)) *
                    mf.calc_distance_nD(self.representative, neighbour.representative)[0]) 
                    - mf.calc_distance_2D(self.grid, self, neighbour), 2)
            
            #E3
            s = 0
            for neighbour in self.direct_neighbours:
                s += len(neighbour.list_of_points)
            if s == 0:
                s=1
            
            error_neighbour = len(neighbour.list_of_points)/s * pow(math.sqrt(
                (self.grid.neutral_variance / max(self.grid.neutral_variance, self.ICV)) *
                    mf.calc_distance_nD(self.representative, neighbour.representative)[0]) 
                    - mf.calc_distance_2D(self.grid, self, neighbour), 2)
            '''

            logger.debug("Part of Error between '%i' and '%i' is '%f'", self.id, neighbour.id, error_neighbour)
            sum_of_error += error_neighbour

            if height_to_test:
                self.height = tmp

        return sum_of_error

    # noinspection PyPep8Naming
    def calc_ICV(self):
        """
         this method calculates the localerror by considering the variance within the cell.
         This method does not consider neighbourhood.
         """
        if len(self.list_of_points) == 1:
            return [0, 0]

        tmp = self.points_to_dataframe(only_data=True).var(axis=0).values.tolist()
        return [sum(tmp), tmp]

    def points_to_dataframe(self, only_data=False):
        """
        This method gets all points of the cell and add it to a pandas dataframe.
        :param only_data: if True, the generate x and y coordinate will not be in the dataframe
        :return: the dataframe object
        """
        df = pd.DataFrame()
        if not only_data:
            for point in self.list_of_points:
                if df.empty:
                    df = pd.DataFrame(point.to_dictionary())
                else:
                    tmp = pd.DataFrame(point.to_dictionary())
                    df = pd.concat([df, tmp])
        else:
            for point in self.list_of_points:
                if df.empty:
                    df = pd.DataFrame(point.to_dictionary()['data'])
                else:
                    tmp = pd.DataFrame(point.to_dictionary()['data'])
                    df = pd.concat([df, tmp])
        return df

    def print_rep(self):
        """
        prints the representative in a readable form
        """
        msg = "["
        for n in self.representative:
            msg = msg + str(n) + "|"
        return msg + "]"

    def print_neighbourhood(self):
        """
        prints the neighbourhood in a readable form
        """
        msg = "["
        for n in self.neighbourhood:
            msg = msg + str(n[0].id) + ":" + str(n[1]) + "|"
        return msg + "]"

    def print_direct_neighbour(self):
        """
        prints the four direct neighbours in a readable form
        :return:
        """
        msg = "["
        for n in self.direct_neighbours:
            msg = msg + str(n.id) + "|"
        return msg + "]"
