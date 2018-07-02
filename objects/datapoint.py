class Datapoint:
    """
    This class represents a point of data, mean it represents one line of the input csv.

    Attributes:
        x_axis (float): the x coordinate of the point in the image space after n iterations
        y_axis (float): the y coordinate of the point in the image space after n iterations

        data (list): a list of float variables representing the original dimensions of the original space

        x_org (float): the x coordinate of the original point in the image space
        y_org (float: the y coordinate of the original point in the image space

        shifts (list): a list of 2D-tuple, saving all changes to x and y coordinates
    """

    def __init__(self,
                 x_axis=None,
                 y_axis=None,
                 data=None,
                 ):

        assert x_axis is not None
        self.x_axis = x_axis
        self.x_org = x_axis
        assert y_axis is not None
        self.y_axis = y_axis
        self.y_org = y_axis
        assert data is not None
        self.data = data

        self.shifts = None
        self.org = None

    @classmethod
    def from_csv(cls, point_as_list):
        """
        this method initializes the class with arguments from a list

        Args:
            :param point_as_list: a list in form [x_axis,y_axis,data]

        Returns:
            :return: a Point with coordinates, org and data set

        Raises:
            None

        Needs:
            None

        """

        point_as_list = point_as_list[0]
        new_point = Datapoint(point_as_list[0], point_as_list[1], point_as_list[2:])
        return new_point

    def set_org(self, cell):
        self.org = cell

    def get_org(self):
        return self.org

    def get_coordinates(self):
        """
        this method returns the actual coordinates as a list with two elements

        Args:
            None

        Returns:
            :return: the coordinates as list [x,y]

        Raises:
            None

        Needs:
            None
        """

        return [self.x_axis, self.y_axis]

    def add_shift(self, new_x_center, new_y_center, oldcenter):
        """
        this method adds a shift to the datapoint

        Args:
            :param new_x_center: shift to the x coordinate
            :param new_y_center: shift to the y coordinate
            :param oldcenter: the original position of this point

        Returns:
            None

        Raises:
            None

        Needs:
           None
        """

        divx = self.x_axis - oldcenter[0]
        divy = self.y_axis - oldcenter[1]

        if not self.shifts:
            self.shifts = [[new_x_center + divx - self.x_axis, new_y_center + divy - self.y_axis]]
        else:
            self.shifts.append([new_x_center + divx - self.x_axis, new_y_center + divy - self.y_axis])

        self.x_axis = new_x_center + divx
        self.y_axis = new_y_center + divy

    def to_dictionary(self):
        """
        this method returns this point in form of a dictionary

        Args:
            None

        Returns:
            :return: the point in form of a dictionary {x,y,xorg,yorg,data}

        Raises:
            None

        Needs:
            None
        """
        return {'x': self.x_axis, 'y': self.y_axis, 'xorg': self.x_org, 'yorg': self.y_org, 'data': [self.data]}
