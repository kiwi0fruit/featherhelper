Feather Helper
==============

Feather Helper is a concise interface to cache and load numpy arrays and
pandas dataframes. I use it with
`Pandoctools/Knitty <https://github.com/kiwi0fruit/pandoctools>`__.

Contents
========

-  `Feather Helper <#feather-helper>`__
-  `Contents <#contents>`__
-  `Install <#install>`__
-  `Usage example <#usage-example>`__

Install
=======

Via conda (should be ``"pip>=10.0.1"`` and ``"conda>=4.5.4"``):

::

   conda install -c defaults -c conda-forge numpy pandas "feather-format>=0.4.0" "pyarrow>=0.11.1"
   pip install featherhelper

Via pip:

::

   pip install featherhelper

Usage example
-------------

.. code:: py

   import pandas as pd
   import numpy as np
   import featherhelper as fh
   fh.setdir("~/feather/mydoc")  # (optional)
   # fh.exc(1, 2)  # force raise exceptions for names (optional)

   # %%
   fh.name(1)  # can also be fh.name('id1'), default is 'default', 1 is the same as '1'
   try:
       # raise fh.Err  # (optional)
       df, A = fh.pull()  # control length can be set: fh.pull(N)
   except fh.Err:
       # calculate:
       print('push')  
       df = pd.DataFrame(np.random.random(16).reshape(4, 4))
       A = df.values
       #
       fh.push(df, A)

   print(df, '\n', A)
