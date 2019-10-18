
import logging

import numpy as np
import pandas as pd
import xarray as xr

from tools import area_grid, global_avg


def _pre_process(ds, variable_id='temp'):
    """ Some standard QoL to pre-process the data we pulled
    in from out catalog.
    
    """
    ds = ds.squeeze()
    ds = xr.decode_cf(ds)
    if 'member_id' in ds.dims:
        ds = ds.mean('member_id')
    da = ds[variable_id]
    da = da.groupby('time.year').mean()
    return da



class BaselineAnomalizer(object):
    """ Transformer-like object for analyzing and removing
    a climatological baseline to compute anomaly timeseries. 
    
    """
    
    def __init__(self, time_dim, time_bnds):
        self.time_dim = time_dim
        self.time_bnds = time_bnds
        
        self._baseline_mean = None
        
    @property
    def baseline_mean(self):
        return self._baseline_mean
        
    @property
    def time_slice(self):
        return slice(*self.time_bnds)
    
    @property
    def indexer(self):
        return {self.time_dim: self.time_slice}
    
    @staticmethod
    def remove_baseline(data, baseline):
        return data - baseline
    
    def fit(self, X, y=None, mean_dims=[]):
        _mean_dims = [self.time_dim, ]
        if mean_dims:
            _mean_dims += mean_dims
        self._baseline_mean = (
            X.sel(**self.indexer).mean(_mean_dims)
        )
        
    def transform(self, X):
        if self._baseline_mean is None:
            raise ValueError("Must call 'fit' before 'transform'")
        return self.remove_baseline(X, self._baseline_mean)
    
    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X)


class PolyFit(object):
    """ Estimator for fitting arbitrary degree polynomials to data. """
    
    def __init__(self, degree=1):
        self.degree = degree
        self._p = []
    
    @property
    def p(self):
        return self._p
    
    @staticmethod
    def poly_calc(x, p):
        y_hat = 0
        for i, pi in enumerate(reversed(p)):
            y_hat += x**i * pi
        return y_hat
    
    def fit(self, X, y=None):
        p = np.polyfit(X, y, self.degree)
        self._p = p
        
    def predict(self, X):
        return self.poly_calc(X, self._p)
    


class HawkinsSutton2012(object):
    """ Automation for running the HS2012 analysis
    
    """
    
    def __init__(self, pi, hist, fut, variable_id,
                 model_name="temp", pre_process=True):
        self.pi = pi
        self.hist = hist
        self.fut = fut
        self.variable_id = variable_id
        self.model_name = model_name
        self.pre_process = pre_process
        
        if self.pre_process:
            self.pi = _pre_process(self.pi, self.variable_id)
            self.hist = _pre_process(self.hist, self.variable_id)
            self.fut = _pre_process(self.fut, self.variable_id)
        
        self._setup()  
        
        
    def _setup(self):
        """ 
        1. Concatenate a "modern" time-series, for 1950-2100
        
        """
        
        print("Setting up the analysis...")
        
        # Modern time-series
        self.modern = xr.combine_by_coords([
            self.hist.to_dataset(name=self.variable_id),
            self.fut.to_dataset(name=self.variable_id)
        ])[self.variable_id]
        
        # Sub-select data for the "modern" timeseries for 1950-2100
        # TODO: user-configuration for this parameter
        self.modern = self.modern.sel(year=slice(1950, 2100))

        # Center the pi data around its mean
        self.pi = self.pi - self.pi.mean('year')

        # Fit anomaly calculator and then compute anomalies
        self.baseline_anomalizer = BaselineAnomalizer('year', (1980, 2010))
        self.baseline_anomalizer.fit(self.modern)
        self.modern_anom = self.baseline_anomalizer.transform(self.modern)

        # Global averages
        x = self.pi.isel(year=0)
        _area = area_grid(x['lon'].data, x['lat'].data, asarray=False)
        # We eagerly did the area grid calculation in memory, so let's
        # turn it into a dask array now (inside a DataArray)
        _area = _area.chunk()
        self.area = _area
        self.modern_anom_gavg = global_avg(self.modern_anom, weights=self.area)

    def _fit_signal(self):
        # Part 1) T^tilde_global(t)
        print("Computing smoothed global average timeseries... ")

        x = self.modern_anom_gavg['year'].values
        y = self.modern_anom_gavg.values

        model = PolyFit(degree=4)
        model.fit(x, y)
        ypred = model.predict(x)

        #########################################

        # Part 2) S(t) / local projections
        print("Projecting local timeseries against smoothed global average... ")

        _anoms_stacked = self.modern_anom.stack(cell=['lon', 'lat'])
        x = ypred # re-use from earlier - same scope
        y = _anoms_stacked.data

        model = PolyFit(degree=1)
        model.fit(x, y)
        # print(model.p.shape)
        alphas, betas = model.p
        # print(alphas.shape, betas.shape)

        _anoms_stacked = _anoms_stacked.to_dataset(name=self.variable_id)
        _anoms_stacked['alpha'] = (['cell', ], alphas)
        _anoms_stacked['beta'] = (['cell', ], betas)

        fitted = _anoms_stacked[['alpha', 'beta']].unstack('cell')
        fitted[f'{self.variable_id}_smoothed'] = (('year', ), ypred)

        self._signal_ds = fitted
        # Copy in the year coordinate, it got dropped
        self._signal_ds['year'] = self.modern_anom.year.values

    def _fit_noise(self):
        
        print("Computing interannual variabilty from PI run... ")
        # TODO: Should we be removing a global mean? Or local means?
        pi_demean = self.pi - global_avg(self.pi, weights=self.area).mean()
        N = pi_demean.std('year')

        self._noise_ds = N.to_dataset(name='N')

    def _calc_signal_to_noise(self):
        
        print("Preparing signal-to-noise analysis... ")

        years = range(2020, 2100)
        signal = self.model_predict(
            years, 
            self._signal_ds[f'{self.variable_id}_smoothed'],
            self._signal_ds['alpha'],
            self._signal_ds['beta']
        )

        self._noise_ds['year'] = (('year', ), years)
        self._noise_ds['S'] = (signal.dims, signal)
        self._noise_ds['S_N'] = self._noise_ds['S'] / self._noise_ds['N']

    def fit(self):
        self._fit_signal()
        self._signal_ds = self._signal_ds.compute()
        
        self._fit_noise()
        
        self._calc_signal_to_noise()
        self._noise_ds = self._noise_ds.compute()
        
        # Note that we load all the things!!!
        
    def time_of_emergence(self, ratio):
        sn_ds = self._noise_ds
        template = sn_ds['S'].isel(year=0).data
        toe_s = np.zeros_like(template)
        
        for year in sn_ds.year:
            _sn_year = sn_ds['S_N'].sel(year=year).data
            toe_s[(toe_s == 0) & (_sn_year > ratio)] = year

        # Mask out zeros
        toe_s = np.ma.masked_equal(toe_s, 0)
        toe_da = xr.DataArray(toe_s, 
                              dims=['lon', 'lat'], 
                              coords=[sn_ds.lon, sn_ds.lat])
        
        return toe_da.to_dataset(name='TOE')
    
        
    @staticmethod
    def model_predict(year, glbl_temp, alpha, beta):
        """ Compute S(year) = alpha*glbl_tmp(year) + beta

        Parameters
        ----------
        year : float or array-like
        glbl_tmp : xr.DataArray
            Must have a "year" dimension and 'year' must be in its range
        alpha : float or array-like
        beta : float or array-like

        """
        return alpha*glbl_temp.sel(year=year) + beta