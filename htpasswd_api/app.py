from htpasswd_api import app, IP, PORT, DEBUG

if __name__ == '__main__':
    app.run(host=IP, port=PORT, debug=DEBUG)
