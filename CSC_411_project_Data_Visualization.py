
##CSC 411 project 
from __future__ import division
import numpy as np
from scipy.stats import gaussian_kde as gkde
import pandas as pd
from bokeh.plotting import figure, gridplot
from bokeh.models import ColumnDataSource, Range1d, LinearAxis
from bokeh.models.tools import BoxSelectTool


def datetime(x): #function to change data tipe of dates to dates
    return np.array(x, dtype=np.datetime64)
    
#data scraped from yahoo finacne
Stock_data = pd.read_csv("AAPL.csv")
source = ColumnDataSource(data=dict(x=datetime(Stock_data['Date']),y=Stock_data['Adj Close']))
Stock_data = pd.read_csv("SBUX.csv")
source2 = ColumnDataSource(data=dict(x=datetime(Stock_data['Date']),y=Stock_data['Adj Close']))    

#Create scatter plot of data
#set up figure
#plot_tools = ['crosshair']
time_plot = figure(plot_height= 400, plot_width= 800, title="", x_axis_label ='Time', 
            y_range = (min(source.data["y"]-5),max(source.data["y"]+5)), tools='',  #need to add crosshair tool (messing up inds in update function)
            y_axis_label = 'AAPL', toolbar_location="left",  x_axis_type="datetime")
            
#Customize time_plot grid lines
time_plot.xgrid.grid_line_color = None
time_plot.ygrid.grid_line_alpha = 0.2

#modify the BoxSelectTool 
#dimensions = specify the dimension in which the box selection is free in
#select_every_mousemove = select points as box moves over
time_plot.add_tools(BoxSelectTool(dimensions=["width"],select_every_mousemove=True))

#add anther axis
time_plot.extra_y_ranges = {"foo": Range1d(start = min(source2.data["y"] - 5),
                                          end = max(source2.data["y"] + 5))}
                                          
#add data to scatter plot (data points on time plot)
time_scat = time_plot.scatter("x","y", source=source,size=1,color="green")
time_scat2 = time_plot.scatter("x","y", source=source2,size=1,color="red",y_range_name="foo")
  
#add time series line
time_line = time_plot.line("x","y",source=source,color = time_scat.glyph.fill_color,
                           alpha=0.5,legend='AAPL Adj Close')
                           
time_line2 = time_plot.line("x","y",source=source2,color="red",
                            alpha=0.5,y_range_name="foo",legend='SBUX Adj Close')   
time_plot.legend.background_fill_alpha = 0.2
#add second axis to time_plot
time_plot.add_layout(LinearAxis(y_range_name = "foo", axis_line_color = 'red',
                                major_label_text_color = "red", 
                                major_tick_line_color = "red",
                                axis_label='SBUX'),"left") 

#edit axis colors
time_plot.yaxis.axis_line_color = time_scat.glyph.fill_color
time_plot.yaxis.major_label_text_color = time_scat.glyph.fill_color
time_plot.yaxis.major_tick_line_color = time_scat.glyph.fill_color

#edit second axis on time_plot
#time_plot.yaxis.axis_line_color = time_scat2.glyph.fill_color
    
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
y_span = np.linspace(np.min(source.data["y"]),
                     np.max(source.data["y"]),np.size(source.data["y"]))
#nd = 1/(2*np.pi*sigma)*np.exp(-(y_span - mu)**2/(2*sigma**2))
#construct normal distribution lines
#hist_plot.line(nd,y_span,line_color="#668cff", line_width=1,alpha=0.5)
    
#add gaussian kernel density estomator
kde = gkde(source.data["y"]).evaluate(y_span)
#construct gaussian kernel density estomator lines    
hist_plot.line(kde,y_span,line_color="#ff6666",line_width=1,alpha=0.5)
    
#Create updateable plots
u_hist = hist_plot.quad(top=edges[1:], bottom=edges[:-1], left=0,
                        right=np.zeros_like(edges),
                        fill_color=time_scat.glyph.fill_color, alpha = 0.5)
                   
kde_data = np.zeros((len(kde)))
kde_line = hist_plot.line(kde_data,y_span,line_color="red")

#create scatter plot from of data sets
scat_plot = figure(plot_height= 400, plot_width= 400, title="", x_axis_label ='', 
            y_axis_label = '')
           
u_scat_points = scat_plot.scatter(x=np.zeros_like(source.data["y"]),
                                  y=np.zeros_like(source.data["y"]),size=2)
                   
#create plot layout
layout = gridplot([[time_plot, hist_plot], [scat_plot, None]])
    
#add updateing histogram construction
def update(attr, old, new):    
    inds = np.array(new["1d"]["indices"])  #error when crosshair is added
    
    #for zero selected or all selected 
    if len(inds) == 0:
        hist1 = np.zeros_like(edges)
        u_scat_data = np.array([np.zeros_like(source.data["y"]),
                                np.zeros_like(source.data["y"])])
    #update hist values on selection
    else:
        hist1, _ = np.histogram(source.data["y"][inds], bins=edges, density=True)
        u_scat_data = np.array([source.data["y"][inds], source2.data["y"][inds]])
        
    if len(inds) > 2:
        kde_span = np.linspace(np.min(source.data["y"][inds]),
                               np.max(source.data["y"][inds]),
                               np.size(source.data["y"][inds]))
        kde_data = gkde(source.data["y"][inds]).evaluate(kde_span)
    else:
        kde_data = np.zeros(2)
        kde_span = np.zeros(2)
    #update ploting data sources    
    u_hist.data_source.data['right'] = hist1
    kde_line.data_source.data['x'] = kde_data
    kde_line.data_source.data['y'] = kde_span
    u_scat_points.data_source.data['x'] = u_scat_data[0]
    u_scat_points.data_source.data['y'] = u_scat_data[1]
    print str(inds) #too see repose on server (will be removed)
    
time_scat.data_source.on_change('selected', update)