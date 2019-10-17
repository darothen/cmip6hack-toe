import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt




def open_file(experiment_id='piControl', source_id='BCC-CSM2-MR', path='/glade/u/home/molina/CMIP6_pathnames.csv'):
    
    """
    Parameters
    ----------
    Input:
    experiment_id = type of experiment (e.g., piControl, ssp585, historical)
    
    """
    
    data_list = pd.read_csv(path)
    
    if source_id:
        new_data_list = data_list[(data_list['experiment_id']==experiment_id)&(data_list['source_id']==source_id)]
        
        return xr.open_mfdataset(new_data_list.path.values[0],combine='by_coords')
    
    else:
        new_data_list = data_list[(data_list['experiment_id']==experiment_id)]
        
        return xr.open_mfdataset(new_data_list.path.values,combine='by_coords')
    

    
def compute_demonthly(data, var='tas'):
    monthly_climo = data[var].groupby('time.month').mean()
    return data[var].groupby('time.month') - monthly_climo
    
    
def standardize_data(data, dim='time'):
    data_std = data.std(dim=dim)
    return data/data_std
    
    
def plot_contourf(data, **kwargs):
    
    ax = plt.axes(projection=ccrs.Robinson())
    data.plot.contourf(ax=ax, transform=ccrs.PlateCarree(), **kwargs)
    ax.coastlines()
    plt.gcf().set_size_inches((12,5))
    
    return plt.show()



    
    
    
def plot_timeseries(data, lats=[0,10], lons=[10,30], time1='1850-01-16T12:00:00', time2='1860-01-16T12:00:00', **kwargs):
    """
    Parameters
    ----------
    Inputs:
    data: already reduced to 1-D time series.
    time1: first time point (str; ex. '1850-01-16T12:00:00')
    time2: final time point (str; ex. '1860-01-16T12:00:00')
    
    """
    fig = plt.figure(figsize=(12,5))
    for x,y in zip(lats,lons):
        data.sel(time=slice(time1, time2)).isel(lat=y,lon=x).plot(**kwargs)
    return plt.show()
    

if __name__ == "__main__":

    data = open_file()
    
    
    
# data_list = pd.read_csv('/glade/u/home/molina/CMIP6_pathnames.csv')
    
# new_data_list = data_list[(data_list['experiment_id']=='piControl')]


# data = 


