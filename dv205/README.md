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


# added 

conda install -c conda-forge streamlit  --> this didn't work - I got permission errors when trying to run
instead use pip install streamlit

Still got errors.  Turns out the default port wasn't working
do the following to change the default port
create a file ./.streamlit/config.toml
add the following:
[server]
port = XXXX

I suggest you try 8080

alternatively run 


Full config info at
https://docs.streamlit.io/library/advanced-features/configuration

# only used on ralph's install during development, not needed for running
conda install jupyterlab
conda install -c conda-forge jupyter-dash
conda install pylint
conda install flake8


With streamlit installed you need to run the script in one of two ways:
python -m streamlit run script.py 
  or
streamlit run script.py

If you don't configure a port as above and have a problem with socket permissions
try giving a port on the command line (below for port 8080)
streamlit run script.py --server.port 8080