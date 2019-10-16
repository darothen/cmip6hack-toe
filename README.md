# CMIP6 Hackathon Project - [Time of Emergence](https://discourse.pangeo.io/t/can-we-better-quantify-the-time-of-emergence-of-regional-climate-change-signals-using-cmip6/117)

This repository is for planning and working on the ["Time of Emergence"](https://discourse.pangeo.io/t/can-we-better-quantify-the-time-of-emergence-of-regional-climate-change-signals-using-cmip6/117) project for the CMIP6 hackathon at NCAR, Boulder, CO, on 16-18 October 2019. Feel free to open PR's against this repository, or create Wiki pages.

### What's included?

1. `catalogs`: data catalogs that can be used by Intake-ESM.
1. `environments`: Conda environment files for the NCAR/Google Cloud deployments.
1. `notebooks`: a place for storing Jupyter Notebooks.
1. `README.md`: this document - a description of the repository and project.
1. `LICENSE`: MIT license file for your project. Do we want to change this?

### How to use this repository

Please clone this repository onto the compute system we plan to use for the hackathon.

1. Open a JupyterLab session.
2. Open a terminal in the JupyterLab environment.
3. Clone your project: `git clone https://github.com/darothen/cmip6hack-toe.git`
4. Get to work!

Additionally, we've created a library of utility tools and functions. 
We've set these up to be installable as a Python package; to do so, navigate to
the folder where you cloned `cmip6hack-toe` and execute the command

``` shell
$ pip install -e .
```

This will use setuptools to install an editable copy of the code; that means that
you can update the code at will without needing to re-install it!

### How to make our project citable

[Zenodo](https://about.zenodo.org/) is a data archiving tool that can help make your project citable by assigning a DOI to the project's GitHub repository.

Follow the guidelines here https://guides.github.com/activities/citable-code

-------------------

# Can We Better Quantify the "Time of Emergence" of Regional Climate Change Signals Using CMIP6?

## Scientific Motivation

Understanding where, when, and under what conditions climate-force trends will become "measurable" (that is, distinguishable from background climate variability or noise) is extremely helpful for both validating our understanding of large scale climate dynamics and framing climate risk assessments. Prior works such as [Hawkins and Sutton (2012)](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2011GL050087) have analyzed ensembles of model simulations from inter-comparison projects and worked out some important details, such as the idea that, despite experience a lower *magnitude* of warming, the lower latitudes will likely experience a measurable "climate change signal" before higher latitudes - a result which has been replicated by works such as [Mahlstein et al (2011)](https://iopscience.iop.org/article/10.1088/1748-9326/6/3/034009).

![Figure from Mahlstein et al (2011) showing how project signal/noise in warming varies by region of the globe](https://aws1.discourse-cdn.com/standard14/uploads/pangeo/original/1X/04f9ba462f766276a982b0c2f79e5fc7b613c22f.jpeg) 

**Figure from Mahlstein et al (2011) showing how project signal/noise in warming varies by region of the globe**

To help understand and break down the time of emergence of climate-forced signals, it's often helpful to perform spatial analyses, breaking up the globe into larger regions which we might expect to experience similar changes on similar timescales. Understanding what sets the spatial patterns of these regions is often then helpful in elucidating the dynamics at play which sets different regional climates apart from each other - and more interestingly, how those differences may play out in a warming world.


## Proposed Hacking

We will replicate some of the foundational work by [Hawkins and Sutton (2012)](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2011GL050087) and [Mahlstein and Rutti (2010)](http://dx.doi.org/10.1007/s00382-009-0654-0) but with an emphasis on CMIP6 models. This will entail:

1. Performing a spatial clustering analysis on different CMIP6 models to identify regions with similar baseline and climate trends; ideally we will explore using machine-learning techniques to "learn" these different regions across many different model simulations
2. Analyzing climate trends by aggregating them across each region (a) model-by-model and (b) across models
3. Develop visualizations and dashboards for exploring our results
4. Create reproducible workflows that automate the entire analyses we develop

Based on this work we would hope to answer a few scientific questions:

- Has our understanding of the time of emergency of regional warming/drying/wetting/etc trends changed with the data from CMIP6?
- What regions and what trends might we expect to "emerge" first? 

## Anticipated Data Needs

**TBD** - we will use standard dynamic/thermodynamic diagnostics (air temperature, humidity, precipitation, wind components, 500mb geopotential heights etc); a list will be forthcoming with the Data Request thread.

Although it would be interesting to break down these analyses for many combinations of CMIP6 experiments, we will focus on pre-industrial runs (for quantifying the background noise/climate variability in the simulations) and future warming scenarios.

## Anticipated Software Tools

We'll try to use as much of the standard suite of scientific Python tools as possible. In particular, we expect to use xarray, dask, pandas, and scikit-learn. We will probably build some interactive visualization tools for helping to understand our results, and for that we will likely use bokeh and Panel.

Ideally the entire research chain will be automated with a few Jupyter notebooks and a Snakemake build (or similar workflow management tool) to enhance reproducibility. Any core modules will be developed as an open source package.

## Desired Collaborators

Anyone! If you can bring some timeseries statistical analysis expertise that would be *sweet* - we'll definitely need that to solve some of the core science problems!
