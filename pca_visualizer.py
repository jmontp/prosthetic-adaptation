#Fourier Coefficient PCA vizualizer using Dash
# Relevant references
#   Dash tutorial: https://www.youtube.com/watch?v=hSPmj7mK6ng&ab_channel=CharmingData
#   Did similar layout to: https://github.com/plotly/dash-svm/blob/master/app.py


import dash
import dash_core_components as dcc
import dash_html_components as html
import utils.dash_reusable_components as drc
from dash.dependencies import Input,Output,State

import plotly.express as px

import numpy as np

from sklearn.decomposition import PCA

import math

from fourier_calculations import get_fourier_prediction



#Initialize the app
app = dash.Dash(__name__)
server = app.server

#Here comes the logic

#Load the numpy array from memory that contains the fourier coefficients
np_parameters = np.load('fourier coefficient matrix.npy')

default_fourier_parameters=np_parameters.shape[1]

n_pca_axis=min(np_parameters.shape)

pca=PCA(n_components=n_pca_axis)

pca.fit(np_parameters)

fourier_paramaters_pca = pca.transform(np_parameters)

pca_input_list=[Input('pca'+str(i),'value') for i in range(n_pca_axis)]


def update_variance_graph():
 	return px.line(y=np.cumsum(pca.explained_variance_ratio_), x=np.linspace(1,n_pca_axis,n_pca_axis), title='Cumulative Sum of variance', labels={'x': 'pca axis', 'y': 'percentage of variance covered'})


pca_sliders=[]

pca_sliders=[drc.NamedSlider(
							name='Step length (meters)',
							id='step-length',
							min=0,
							max=2,
							step=0.01,
							marks={i: str(i/10) for i in range(21)},
							value = 1
						)]

for i in range(n_pca_axis):
	variance=pca.explained_variance_[i]
	pca_sliders+= [drc.NamedSlider(
							name='PCA axis '+str(i),
							id='pca'+str(i),
							min=-variance,
							max=variance,
							step=variance/100,
							marks={i: str(i) for i in range(-math.floor(variance),math.floor(variance), math.floor(variance/10)+1)},
							value = 0
						)]





#Going to copy the container layout from https://github.com/plotly/dash-svm

app.layout = html.Div(children=[

	#Create a banner
	html.Div(className="banner", children=[
		# Change app name here?
		html.Div(className='container scalable', children=[
			# Change app name here??
			html.H2(html.A(
				'Fourier Coefficient PCA Vizualizer',
				href='https://github.com/jmontp/prosthetic-adaptation',
				style={
				'text-decoration':'none',
				'color':'inherit'
				}
			))

		# 	html.A(
		# 		html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"),
  #               href='https://plot.ly/products/dash/'
  #           )

		# ])
	]),

	html.Div(id='body', className='container scalable', children=[
		html.Div(
			
			children=[
				html.Div(
					className='three cloumns', 
					style={'width': '49%', 'display': 'inline-block'},
					children=[
              		dcc.Graph(
							id='graph-fourier-pca',
						),
             	 	dcc.Graph(
					   		id='explained-variance',
							figure=update_variance_graph()
              		)]		
				),
            

				html.Div(
					className='three cloumns', 
					style={'width': '49%', 'display': 'inline-block'},
					children=[
                    drc.Card(pca_sliders)
				])
			])
		])
	])
])


#This is the callback that updates the graphs
@app.callback(Output('graph-fourier-pca', 'figure'),
			 [Input('step-length', 'value'),
			  *pca_input_list])
def update_pca_graph(step_length, *pca_argv):

    
    #Recreate the phi and step length inputs
    phi=np.linspace(0,1,150)#.reshape(1,150)
    step_length_array=np.full((150,),step_length)
    num_params=12
       
    #Get the axis for the first three pca vectors
    parameter_tuples = zip(pca.components_,pca_argv)

    parameter=np_parameters[0]+sum([pca_axis*pca_slider_value for pca_axis,pca_slider_value in parameter_tuples])
    #Get the predicted y from the model
    y_pred=get_fourier_prediction(parameter,
                                  phi, 
                                  step_length_array,
                                  num_params)
    # print('Phi is ' + str(phi))
    # print('Step length is ' + str(step_length_array))
    # print('Params is '+str(np_parameters[0]))
    # print('Predicted y is ' + str(y_pred))
    
    return px.line(x=phi, y=y_pred,title='Fourier Model Prediction', labels={'x': 'Phi', 'y': 'Thigh Angle'})




#Run the server
if __name__=='__main__':
	app.run_server(debug=True)


# #This is the callback that updates the graphs
# @app.callback(Output('graph-fourier-pca', 'figure'),
# 			 [Input('pca1','value'),
# 			  Input('pca2', 'value'), 
# 		      Input('pca3','value'), 
# 		      Input('step-length', 'value')])
# def update_pca_graph(pca1_slider, pca2_slider, pca3_slider, step_length):

    
#     #Recreate the phi and step length inputs
#     phi=np.linspace(0,1,150)#.reshape(1,150)
#     step_length_array=np.full((150,),step_length)
#     num_params=12
       
#     #Get the axis for the first three pca vectors
#     pca1_axis=pca.components_[0]
#     pca2_axis=pca.components_[1]
#     pca3_axis=pca.components_[2]
#     #Get the predicted y from the model
#     y_pred=get_fourier_prediction(np_parameters[0]+pca1_slider*pca1_axis+pca2_slider*pca2_axis+ pca3_slider*pca3_axis,
#                                   phi, 
#                                   step_length_array,
#                                   num_params)
#     # print('Phi is ' + str(phi))
#     # print('Step length is ' + str(step_length_array))
#     # print('Params is '+str(np_parameters[0]))
#     # print('Predicted y is ' + str(y_pred))
    
#     return px.line(x=phi, y=y_pred)



#This is the callback for the explained variance
#@app.callback(Output('explained-variance', 'figure'))
# def update_variance_graph():
# 	return px.line(np.cumsum(pca.explained_variance_ratio_))



