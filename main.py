from Website import create_app

app = create_app()

if __name__ == '__main__':
    #Start the web server 
    app.run(debug = True) 