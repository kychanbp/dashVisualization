from myproject.app import app

if __name__ == '__main__':
    app.run_server(host="0.0.0.0",  port = "8080", debug=True)