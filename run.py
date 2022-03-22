from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_restful import reqparse
from flask import session
from flask_sockets import Sockets

app = Flask(__name__)
app.debug = True
app.secret_key = 'test'

@app.route('/')
def login():
  return render_template("login.html")

@app.route('/loginSuccess')
def loginSuccess():
  data = {
    'login_id': session.get('login_id')
  }
  return render_template("loginSuccess.html", **data)



import database
database_params = {
	'host': 'localhost',
  'user': 'eun',
  'password': 'softonnet',
	'database': 'eun',
	'connection_timeout': 60,
	'pool_size': 8
}
db = database.Database.from_config(database_params)

@app.route('/webapi/idpw', methods=['POST'])
def idpw():
  # id = request.form.get('id')
  # passwd = request.form.get('pw')
  # print(id, passwd)

  # return jsonify(status='true')

  reqparse.RequestParser()
  parser = reqparse.RequestParser()
  parser.add_argument('id', required=True)  # sessionKey
  parser.add_argument('pw', required=True)  # sessionKey
  args = parser.parse_args()
  print(args['id'], args['pw'])


  sql = 'SELECT * ' \
        'FROM users ' \
        'WHERE login_id = %s AND login_pass = %s'

  dbcon = db.connection()
  a = dbcon.execute(sql, args['id'], args['pw']) # execute()가 return하는 값이 있으므로 그걸 받아와서 a로 넘겨주기!
  account = a.fetchone()
  if account:
    session['login_id'] = args['id']
    return jsonify(status='ok')
  else:
    return jsonify(status='fail', reason='login.fail')



sockets = Sockets(app)
ws_list = dict()
@sockets.route('/webSocket/chatchat')
def chatchat(ws):
    # recevied key (중요)
    reqparse.RequestParser()
    parser = reqparse.RequestParser()
    parser.add_argument('keyy', required=True)  # sessionKey
    args = parser.parse_args()
    print('[new] {}'.format(args.keyy))
    # print(args.keyy)
    # print(args['keyy'])

    ws_list[args.keyy] = ws
    while not ws.closed:
        message = ws.receive()
        if message:
            # send message
            for keyy, value in ws_list.items():
                ws_list[keyy].send(message)

    # delete websocket by key
    print('del keyy {}'.format(args.keyy))
    del ws_list[args.keyy]

    for keyy, _ in ws_list.items():
        print('exist keyy {}'.format(keyy))



if __name__ == "__main__":
  from gevent import pywsgi
  from geventwebsocket.handler import WebSocketHandler
  from gevent import monkey
  monkey.patch_all(select=False, thread=False)
  server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
  server.serve_forever()
  # app.run(host="0.0.0.0") # http://0.0.0.0:5000/


