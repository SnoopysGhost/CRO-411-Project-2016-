
##CSC 411 project 
from __future__ import division
import numpy as np
from scipy.stats import gaussian_kde as gkde
import pandas as pd
from bokeh.plotting import figure, gridplot
from bokeh.models import ColumnDataSource
from bokeh.models.tools import BoxSelectTool


def datetime(x): #function to change data tipe of dates to dates
    return np.array(x, dtype=np.datetime64)
    
Stock_data = pd.read_csv("APLE.csv")
    
source = ColumnDataSource(data=dict(x=datetime(Stock_data['Date']),y=Stock_data['Adj Close']))

#Create scatter plot of data
#set up figure
time_plot = figure(plot_height= 400, plot_width= 800, title="Scatter plot",
            x_axis_label ='Time', 
            y_range = (min(source.data["y"]-5),max(source.data["y"]+5)),
            y_axis_label = 'Data', toolbar_location="left",  x_axis_type="datetime")
            
#Customize time_plot grid lines
time_plot.xgrid.grid_line_color = None
time_plot.ygrid.grid_line_alpha = 0.2

#modify the BoxSelectTool 
#dimensions = specify the dimension in which the box selection is free in
#select_every_mousemove = select points as box moves over
time_plot.add_tools(BoxSelectTool(dimensions=["width"],select_every_mousemove=True))
    
#add data to scatter plot (data points on time plot)
time_scat = time_plot.scatter("x","y", source=source,size=2)
    
#add time series line
time_line = time_plot.line("x","y",source=source,color="navy",alpha=0.5)
    
#Create reggression line (slectable tool)   
    
#Create marginal histogram for y-axis data density
#set up figure
hist_plot = figure(plot_height=400, plot_width=200,y_range = time_plot.y_range)

#Customize hist_plot grid lines
hist_plot.xgrid.grid_line_alpha = 0.2
hist_plot.ygrid.grid_line_alpha = 0.5


#get histogram data 
hist, edges = np.histogram(source.data["y"], density=True, bins=20)
#contruct histogram
hist_plot.quad(top=edges[1:], bottom=edges[:-1], left=0, right=hist,
               fill_color="white", alpha = 0.3)
#styleing histograms axises              
hist_plot.xaxis.axis_label = ""
hist_plot.yaxis.axis_label = ""
hist_plot.xaxis.visible = None
    
#add probibility density function line to histogram data (smooth)
#normal distributioin
#calculate arithmetic mean
mu = np.mean(source.data["y"])
    
#calculating standard deviation
sigma = np.std(source.data["y"])
    
#calculating normal distribution (probability density function)
y_span = np.linspace(np.min(source.data["y"]),np.max(source.data["y"]),np.size(source.data["y"]))
nd = 1/(2*np.pi*sigma)*np.exp(-(y_span - mu)**2/(2*sigma**2))
#construct normal distribution lines
hist_plot.line(nd,y_span,line_color="#668cff", line_width=1,alpha=0.5)
    
#add gaussian kernel density estomator
kde = gkde(source.data["y"]).evaluate(y_span)
#construct gaussian kernel density estomator lines    
hist_plot.line(kde,y_span,line_color="#ff6666",line_width=1,alpha=0.5)
    
#Create updateable plots
u_hist = hist_plot.quad(top=edges[1:], bottom=edges[:-1], left=0, right=np.zeros_like(edges),
        fill_color="navy", alpha = 0.5)
                   
kde_data = np.zeros((len(kde)))
kde_line = hist_plot.line(kde_data,y_span,line_color="red")    
                   
#create plot layout
layout = gridplot([[time_plot,hist_plot]])
    
#add updateing histogram construction
def update(attr, old, new):    
    inds = np.array(new["1d"]["indices"])
    print str(inds)
    #for zero selected or all selected 
    if len(inds) == 0:
        hist1 = np.zeros_like(edges)
        dfac= 1
    #update hist values on selection
    else:
        hist1, _ = np.histogram(source.data["y"][inds], bins=edges, density=True)
        dfac = len(source.data["y"])/len(source.data["y"])
        
    if len(inds) > 2:
        kde_span = np.linspace(np.min(source.data["y"][inds]),np.max(source.data["y"][inds]),np.size(source.data["y"][inds]))
        kde_data = gkde(source.data["y"][inds]).evaluate(kde_span)
    else:
        kde_data = np.zeros(2)
        kde_span = np.zeros(2)
        
    u_hist.data_source.data['right'] = hist1/dfac
    kde_line.data_source.data['x'] = kde_data
    kde_line.data_source.data['y'] = kde_span
        
time_scat.data_source.on_change('selected', update)