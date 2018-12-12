import pandas as pd
import os
from os import path as p
import feather
import numpy as np
from typing import Union, List
import shutil

POSTFIX = '_featherhelper'

_dir = None
_name = None
_exc = ()  # list of names to raise exceptions, None means always raise.


def setdir(dir_: str='./feather'):
    """
    Set directory to store cache.
    """
    global _dir
    _dir = p.abspath(p.normpath(p.expanduser(p.expandvars(dir_))))
    if not p.isdir(_dir):
        os.makedirs(_dir)


def name(name_: Union[str, int]='default'):
    """
    Set current subfolder name. int is converted to str.
    Should not be empty string.
    """
    global _name, _dir
    if _dir is None:
        setdir()
    if isinstance(name_, int):
        name_ = str(name_)
    if isinstance(name_, str) and name_:
        _name = name_
    else:
        raise ValueError('Invalid name: {}'.format(name_))


def exc(*names: Union[str, int, None]):
    """
    Force raise exceptions for subfolder names,
    default is raise for all - no arguments.
    If ``exc(None)`` then do not raise exceptions.
    """
    global _exc

    names = tuple(names)
    if names == (None,):
        _exc = ()
    elif names == ():
        _exc = None
    else:
        _exc = tuple(str(n) for n in names if (n and isinstance(n, str)) or isinstance(n, int))
        if len(names) != len(_exc):
            raise ValueError('Invalid name in: {}'.format(names))


class FeatherHelperError(Exception):
    pass


def push(*data_frames: Union[np.ndarray, pd.DataFrame]):
    """
    Stores data frames or arrays.
    """
    global _name, _dir
    if _name is None:
        name()

    cwd = p.join(_dir, _name + POSTFIX)
    shutil.rmtree(cwd)
    if not p.isdir(cwd):
        os.makedirs(cwd)

    for i, df in enumerate(data_frames):
        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)
            dot_ext = '.np'
        elif isinstance(df, pd.DataFrame):
            dot_ext = '.df'
        else:
            raise ValueError('Unsupported input type. Only numpy.ndarray and pandas.DataFrame are supported.')
        if len(df.values.shape) > 2:
            raise ValueError('3D and multidimensional arrays are not supported.')
        feather.write_dataframe(df, p.join(cwd, str(i) + dot_ext))
        pass
    _name = 'default'


def pull(ret_len: int=None) -> List[Union[np.ndarray, pd.DataFrame]] or np.ndarray or pd.DataFrame:
    """
    Reads cached data frames or arrays.
    """
    global _name, _dir, _exc
    if _name is None:
        name()

    if _exc is None:
        raise FeatherHelperError()
    elif _name in _exc:
        raise FeatherHelperError()

    cwd = p.join(_dir, _name + POSTFIX)
    if not p.isdir(cwd):
        raise FeatherHelperError()

    file_names = sorted([p.basename(os.fsdecode(file))  # may be p.basename() is redundant
                         for file in os.listdir(os.fsencode(cwd))],
                        key=lambda filename: int(p.splitext(filename)[0]))
    ret = []
    for i, file_name in enumerate(file_names):
        if i != int(p.splitext(file_name)[0]):
            raise FeatherHelperError()
        dot_ext = p.splitext(file_name)[1]
        df = feather.read_dataframe(p.join(cwd, file_name))
        if dot_ext == '.np':
            ret.append(df.values)
        elif dot_ext == '.df':
            ret.append(df)
        else:
            raise FeatherHelperError()
    if (not ret) or (len(ret) != ret_len and ret_len):
        raise FeatherHelperError()

    _name = 'default'
    return ret if (len(ret) > 1) else ret[0]
