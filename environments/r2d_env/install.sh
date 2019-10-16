#!/bin/bash
set -euo pipefail

ENV_NAME="pangeo"

conda env create --name $ENV_NAME --file ./r2d_base_env.yaml
conda activate $ENV_NAME 
conda env update --name $ENV_NAME --file ./pangeo_base_env.yaml
conda env update --name $ENV_NAME --file ./pangeo_notebook_env.yaml
conda env update --name $ENV_NAME --file ./pangeo_ocean_env.yaml

# labextensions
jupyter labextension install dask-labextension@1.0.0 \
                             @jupyter-widgets/jupyterlab-manager \
                             @pyviz/jupyterlab_pyviz \
                             jupyter-leaflet
