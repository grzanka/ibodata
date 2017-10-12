import os
from datetime import datetime

import numpy as np

from ibodata.lateral_profile import LateralProfile
from ibodata.depth_profile import DepthProfile


def remove_incorrect_values(array_x_y):
    """
    Remove rows with incorrect values, such as Inf, -Inf, NaN, from given array
    :param array_x_y: 2D array with 2 columns
    :return: array without incorrect values
    """
    ret = np.asarray([array_x_y[:, 0][np.isfinite(array_x_y[:, -1])],
                      array_x_y[:, -1][np.isfinite(array_x_y[:, -1])]]).transpose()
    return ret


def identify_profile_type(axis):
    """
    :param axis: name of axis
    :return: 'L' for LateralProfile, 'D' for DepthProfile
    :raises: Exception if couldn't identify profile type
    """
    if axis == 'PB' or axis == 'Z':
        return 'D'
    elif axis == 'X' or axis == 'Y':
        return 'L'

    raise Exception("Can't identify profile type")


def get_axis(cvs_file_data):
    """
    :param cvs_file_data: data from file with named axis
    :return: name of axis
    """
    axis_candidate_list = []
    possible_axis = []
    for axis in ('X', 'Y', 'Z', 'PB'):
        if np.isin(axis, cvs_file_data.dtype.names):
            possible_axis.append(axis)
    for axis in possible_axis:
        if np.all(np.diff(cvs_file_data[axis]) != 0):
            axis_candidate_list.append(axis)
    if len(axis_candidate_list) == 1:
        return axis_candidate_list[0]
    else:
        raise Exception("Cannot find axis, candidates: " + str(axis_candidate_list))


class ProfileDataset:
    def __init__(self, profile, date):
        self.profile = profile
        self.date = date


class FileReader:
    def __init__(self, source):
        """
        :param source: directory path which will be searched
        """
        self.Lprofiles = list()
        self.Dprofiles = list()

        for dirname, dirnames, filenames in os.walk(source):
            for filename in filenames:

                # find file with .dat extension
                if filename.endswith('.dat'):

                    # extract date from directory name
                    split = os.path.split(dirname)
                    date = datetime.strptime(split[-1], '%Y-%m-%d_%H_%M_%S')

                    # get data from the file
                    file_data = np.genfromtxt(os.path.join(dirname, filename), dtype=float, names=True)

                    axis = None
                    try:
                        axis = get_axis(file_data)
                    except Exception as e:
                        print("Profile in file: " + str(os.path.join(dirname, filename)) +
                              ": " + str(e))
                        continue

                    if not np.isin('Wylicz', file_data.dtype.names):
                        print("Profile in file: " + str(os.path.join(dirname, filename)) +
                              ": no 'Wylicz.' column found")
                        continue

                    # extract array with relevant columns from file's data
                    array_x_y = np.asarray((file_data[axis], file_data['Wylicz'])).transpose()
                    # remove rows with Inf, -Inf and NaN
                    array_x_y = remove_incorrect_values(array_x_y)

                    # Construct Profiles and add them to lists
                    profile_type = identify_profile_type(axis)
                    if profile_type == 'L':
                        self.Lprofiles.append(ProfileDataset(LateralProfile(array_x_y), date))
                    elif profile_type == 'D':
                        self.Dprofiles.append(ProfileDataset(DepthProfile(array_x_y), date))

        self.Lprofiles = np.asarray(self.Lprofiles)
        self.Dprofiles = np.asarray(self.Dprofiles)
