# Feather Helper

Feather Helper is a concise interface to cache 2D numpy arrays and pandas dataframes. 


# Contents

* [Feather Helper](#feather-helper)
* [Contents](#contents)
* [Install](#install)
* [Usage example](#usage-example)


# Install

**_Via conda_** (should be `"pip>=10.0.1"` and `"conda>=4.5.4"`):

```
conda install -c defaults -c conda-forge numpy pandas feather-format
pip install featherhelper
```

**_Via pip_**:

```
pip install featherhelper
```


## Usage example

```py
import pandas as pd
import numpy as np
import featherhelper as fh
fh.setdir("~/feather/mydoc")  # optional

# %%
fh.name('id1')
try:
    # raise Exception  # <- this is a switch
    df, A = fh.pull()  # control length can be set: fh.pull(N)
except Exception as e:
    print('push')  # calculate stuff:
    df = pd.DataFrame(np.random.random(16).reshape(4, 4))
    A = df.values
    fh.push(df, A, e=e)

print(df, '\n', A)
```
