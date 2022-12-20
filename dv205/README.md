# 205_data_viewer
Dataviewer for ASHRAE 205 data files



Setting up environment for developing with dash 

conda create --name dash python=3.9
conda activate dash

# install the latest pandas, plotly, and dash in your new environment
conda install pandas
conda install plotly
conda install -c conda-forge dash  # use conda-forge to get dash 2.x rather than 1.x
conda install pyyaml
conda install openpyxl

pip install cbor2


# only used on ralph's install during development, not needed for running
conda install jupyterlab
conda install -c conda-forge jupyter-dash
conda install pylint
conda install flake8
