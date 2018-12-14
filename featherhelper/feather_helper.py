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
    if p.isdir(cwd):
        shutil.rmtree(cwd)
    if not p.isdir(cwd):
        os.makedirs(cwd)

    for i, df in enumerate(data_frames):
        if isinstance(df, np.ndarray):
            arr = df
            if len(arr.shape) > 2:
                s = arr.shape
                arr = arr.view()
                arr.shape = (np.prod(s[:-1]), s[-1])
                dot_ext = '.{}.np'.format('_'.join(map(str, s)))
            else:
                dot_ext = '.np'
            df = pd.DataFrame(arr)
        elif isinstance(df, pd.DataFrame):
            dot_ext = '.df'
        else:
            raise ValueError('Unsupported input type. Only numpy.ndarray and pandas.DataFrame are supported.')
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
        raise FeatherHelperError('forced exception for all')
    elif _name in _exc:
        raise FeatherHelperError('forced exception for {} subfolder'.format(_name))

    cwd = p.join(_dir, _name + POSTFIX)
    if not p.isdir(cwd):
        raise FeatherHelperError('dir "{}" was not found'.format(cwd))

    file_names = sorted([p.basename(os.fsdecode(file))  # may be p.basename() is redundant
                         for file in os.listdir(os.fsencode(cwd))],
                        key=lambda filename: int(p.splitext(filename)[0].split('.')[0]))
    ret = []
    for i, file_name in enumerate(file_names):
        num_shape, dot_ext = p.splitext(file_name)
        num_shape = num_shape.split('.')
        num = int(num_shape[0])
        if i != num:
            raise FeatherHelperError('wrong file name: {}'.format(num))

        shape = None
        if len(num_shape) == 1:
            pass
        elif len(num_shape) == 2:
            try:
                shape = tuple(map(int, num_shape[1].split('_')))
                if len(shape) < 3:
                    raise FeatherHelperError('wrong array shape stored in the name: len(shape) < 3')
            except ValueError:
                raise FeatherHelperError('wrong array shape stored in the name: {}'.format(num_shape[1]))
        else:
            raise FeatherHelperError('file name contains more than two dots')

        df = feather.read_dataframe(p.join(cwd, file_name))
        if dot_ext == '.np':
            if shape is None:
                ret.append(df.values)
            else:
                v = df.values.view()
                v.shape = shape
                ret.append(v)
        elif dot_ext == '.df':
            ret.append(df)
        else:
            raise FeatherHelperError('wrong file name ext: {}'.format(dot_ext))
    if (not ret) or (len(ret) != ret_len and ret_len):
        raise FeatherHelperError('no *.np and *.df files in the subfolder or control sum mismatch')

    _name = 'default'
    return ret if (len(ret) > 1) else ret[0]
