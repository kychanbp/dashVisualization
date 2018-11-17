from flask import Flask
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask('myproject')
app = dash.Dash(server=server, external_stylesheets=external_stylesheets)