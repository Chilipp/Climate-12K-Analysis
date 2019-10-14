# Jupyter notebooks for Temperature12K

This directory contains a collection of Jupyter notebooks that can be run to
analyse the Temperature12K database. You can either run them online using mybinder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Chilipp/Temperature12K-Tests/master)

or offline on your local computer. More information about jupyter notebooks in
general can be found at https://jupyter.org.

## Online (remote server)
You can run the [notebooks](notebooks) online through mybinder.org by clicking
here:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Chilipp/Temperature12K-Tests/master)

Any results that you produce, however, will not be stored unless you download
them afterwards.

## Offline (your local computer)
Follow the installation instructions as desribed in the
[Installation](../README.md#installation) section.

Afterwards, with the activated conda environment, you should install the
ipython kernel via

```bash
python -m ipykernel install --user
```

to make sure that the notebook server uses the correct environment.

Then start the notebook server via

```bash
jupyter notebook
```

which will open your browser and let you run the corresponding notebook.

More information

## Adding new analysis
We very much welcome contributions with further analysis scripts for the
Temperature12K database! Please head over to our
[contributing guide](../CONTRIBUTING.md#adding-new-analysis-notebooks) to
learn more.
