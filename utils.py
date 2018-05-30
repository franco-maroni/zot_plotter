'''
Created on Jan 7, 2017

@author: francesco
'''
import os
import errno
from fractions import Fraction


def make_sure_path_exists(path):
    """"Check if the provided path exists. If it does not exist, create it."""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def get_grid_dimensions(num_elems):
    """ Given the number of elements to display,
        determines the number of  rows and columns"""
    rows = cols = 1
    while rows * cols < num_elems:
        if rows == cols:
            rows += 1
        else:
            cols += 1
    return rows, cols


def lcm(values):
    '''
    simple algorithm to find least common multiple of a list of integer values
    :param values: list of integer values
    :return: least common multiple
    '''
    values = set([abs(v) for v in values])
    if values and 0 not in values:
        candidate = max_num = max(values)
        values.remove(candidate)
        while any(candidate % v for v in values):
            candidate += max_num
        return candidate
    return 0


def normalize_list(values):
    '''
    :param values: list of floating point numbers
    :return: list of integer numbers corresponding to the integer counterpart of the input values
    '''
    rationals = [Fraction(v).limit_denominator(1000000)
                 for v in values]
    common_denom = lcm([f.denominator for f in rationals])
    normalized_values = [f.numerator * common_denom/f.denominator
              for f in rationals]
    return normalized_values


def get_normalization_dict(values, tolerance):
    '''
    given a list of floating point numbers, and a tolerance value,
    it returns a dictionary in which the keys correspond to the same numbers in the list,
    while the values are those numbers scaled to be all integers.
    It approximates to the closest rational number when needed.
    Each value must be scaled also according to the value of tolerance.
    :param values: list of floating point numbers.
    :param tolerance: factor (<1) by which some of the values (e.g. alpha) are multiplied in the model. Those numbers are multiplied by tolerance also here.
    :return: "normalization dictionary", associating each number in 'values' with its integer scaled counterpart.
    '''
    tolerance = Fraction(tolerance).limit_denominator(1000000)
    rationals_dict = {v: Fraction(v).limit_denominator(1000000) * tolerance
                 for v in values}
    # print "rational_dict:{}".format(rationals_dict)
    common_denom = lcm([f.denominator for f in rationals_dict.values()])
    # print "common_denom:{}".format(common_denom)
    normalization_dict = {k: int(f.numerator/tolerance) * (common_denom/f.denominator)
                         for (k, f) in rationals_dict.items()}
    # print "normalization_dict: {}".format(normalization_dict)
    return normalization_dict


def order_int(a, b):
    if int(a[0]) > int(b[0]):
        return 1
    elif int(a[0]) < int(b[0]):
        return -1
    else:
        return 0


def compare_keys(x, y):
    try:
        x = int(x)
    except ValueError:
        xint = False
    else:
        xint = True
    try:
        y = int(y)
    except ValueError:
        if xint:
            return -1
        return cmp(x.lower(), y.lower())
        # or cmp(x, y) if you want case sensitivity.
    else:
        if xint:
            return cmp(x, y)
    return 1