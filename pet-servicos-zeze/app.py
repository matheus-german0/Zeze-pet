from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os, requests

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'zeze.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- MODELS ----------
class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default='user')

class Appointment(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    date = db.Column(db.String)
    time = db.Column(db.String)
    location = db.Column(db.String)
    name = db.Column(db.String)
    phone = db.Column(db.String)
    status = db.Column(db.String, default='pendente')
    service = db.Column(db.String)

class Finance(db.Model):
    id = db.Column(db.String, primary_key=True)
    tipo = db.Column(db.String)  # receita | despesa
    desc = db.Column(db.String)
    valor = db.Column(db.Float)
    data = db.Column(db.String)

# ---------- HELP ----------
def uid():
    import random, string
    return 'id_' + ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(8))

# ---------- INIT DB (compatível com Flask 3.x) ----------
with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        admin = User(id=uid(), username='admin', name='Administrador', phone='', email='', password='1234', role='admin')
        db.session.add(admin)
        db.session.commit()


# ---------- SERVE HTML ----------
@app.route('/')
def index():
    return render_template('tst30zeze.html')

# ---------- USERS ----------
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id, 'username': u.username, 'name': u.name,
        'phone': u.phone, 'email': u.email, 'role': u.role, 'password': u.password
    } for u in users])

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error':'no data'}), 400
    username = data.get('username') or (data.get('name','').lower().replace(' ',''))
    if User.query.filter_by(username=username).first():
        return jsonify({'error':'username exists'}), 400
    u = User(id=uid(), username=username, name=data.get('name',''), phone=data.get('phone',''), email=data.get('email',''), password=data.get('password','1234'), role=data.get('role','user'))
    db.session.add(u); db.session.commit()
    return jsonify({'ok':True,'id':u.id})

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error':'not found'}), 404
    Appointment.query.filter_by(user_id=user_id).delete()
    db.session.delete(u)
    db.session.commit()
    return jsonify({'ok':True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    u = User.query.filter_by(username=username, password=password).first()
    if not u:
        return jsonify({'error':'invalid credentials'}), 401
    return jsonify({'id':u.id,'username':u.username,'name':u.name,'phone':u.phone,'email':u.email,'role':u.role})

# ---------- APPOINTMENTS ----------
@app.route('/api/appointments', methods=['GET'])
def appts_list():
    appts = Appointment.query.all()
    return jsonify([{
        'id': a.id, 'userId': a.user_id, 'date': a.date, 'time': a.time, 'location': a.location,
        'name': a.name, 'phone': a.phone, 'status': a.status, 'service': a.service
    } for a in appts])

@app.route('/api/appointments', methods=['POST'])
def appt_create():
    data = request.get_json()
    a = Appointment(
        id=uid(),
        user_id=data.get('userId'),
        date=data.get('date'),
        time=data.get('time'),
        location=data.get('location'),
        name=data.get('name'),
        phone=data.get('phone'),
        status=data.get('status','pendente'),
        service=data.get('service')
    )
    db.session.add(a)
    fin = data.get('finance')
    if fin:
        f = Finance(id=uid(), tipo=fin.get('tipo','receita'), desc=fin.get('desc'), valor=float(fin.get('valor') or 0.0), data=fin.get('data') or datetime.now().strftime('%d/%m/%Y'))
        db.session.add(f)
    db.session.commit()
    return jsonify({'ok':True,'id':a.id})

@app.route('/api/appointments/<appt_id>', methods=['DELETE'])
def appt_delete(appt_id):
    a = Appointment.query.get(appt_id)
    if not a:
        return jsonify({'error':'not found'}), 404
    db.session.delete(a); db.session.commit()
    return jsonify({'ok':True})

@app.route('/api/appointments/<appt_id>/status', methods=['PUT'])
def appt_update_status(appt_id):
    a = Appointment.query.get(appt_id)
    if not a:
        return jsonify({'error':'not found'}), 404
    data = request.get_json()
    new_status = data.get('status')
    a.status = new_status
    db.session.commit()
    add_fin = data.get('register_finance')
    if add_fin:
        fin = Finance(id=uid(), tipo='receita', desc=add_fin.get('desc'), valor=float(add_fin.get('valor') or 0.0), data=add_fin.get('data') or datetime.now().strftime('%d/%m/%Y'))
        db.session.add(fin); db.session.commit()
    return jsonify({'ok':True})

# ---------- FINANCE ----------
@app.route('/api/finance', methods=['GET'])
def finance_list():
    f = Finance.query.all()
    return jsonify([{'id':x.id,'tipo':x.tipo,'desc':x.desc,'valor':x.valor,'data':x.data} for x in f])

@app.route('/api/finance', methods=['POST'])
def finance_create():
    data = request.get_json()
    if not data: return jsonify({'error':'no data'}), 400
    f = Finance(id=uid(), tipo=data.get('tipo'), desc=data.get('desc'), valor=float(data.get('valor') or 0), data=data.get('data') or datetime.now().strftime('%d/%m/%Y'))
    db.session.add(f); db.session.commit()
    return jsonify({'ok':True,'id':f.id})

@app.route('/api/finance/<fid>', methods=['DELETE'])
def finance_delete(fid):
    f = Finance.query.get(fid)
    if not f:
        return jsonify({'error':'not found'}), 404
    db.session.delete(f); db.session.commit()
    return jsonify({'ok':True})

# ---------- CEP PROXY ----------
@app.route('/api/cep/<cep>', methods=['GET'])
def cep_proxy(cep):
    cep = ''.join(filter(str.isdigit, cep))[:8]
    if len(cep) != 8:
        return jsonify({'error':'CEP inválido'}), 400
    r = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    if r.status_code != 200:
        return jsonify({'error':'viacep error'}), 502
    return jsonify(r.json())

# ---------- SYNC ENDPOINTS (para compatibilidade com localStorage do seu front) ----------
@app.route('/api/sync/users', methods=['POST'])
def sync_users():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error':'expected list'}), 400
    User.query.delete()
    for it in data:
        u = User(
            id=it.get('id') or uid(),
            username=it.get('username') or (it.get('name','').lower().replace(' ','')+uid()),
            name=it.get('name',''),
            phone=it.get('phone',''),
            email=it.get('email'),
            password=it.get('password','1234'),
            role=it.get('role','user')
        )
        db.session.add(u)
    db.session.commit()
    return jsonify({'ok':True})

@app.route('/api/sync/appointments', methods=['POST'])
def sync_appts():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error':'expected list'}), 400
    Appointment.query.delete()
    for it in data:
        a = Appointment(
            id=it.get('id') or uid(),
            user_id=it.get('userId'),
            date=it.get('date'),
            time=it.get('time'),
            location=it.get('location'),
            name=it.get('name'),
            phone=it.get('phone'),
            status=it.get('status','pendente'),
            service=it.get('service')
        )
        db.session.add(a)
    db.session.commit()
    return jsonify({'ok':True})

@app.route('/api/sync/finance', methods=['POST'])
def sync_finance():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error':'expected list'}), 400
    Finance.query.delete()
    for it in data:
        f = Finance(
            id=it.get('id') or uid(),
            tipo=it.get('tipo'),
            desc=it.get('desc'),
            valor=float(it.get('valor') or 0),
            data=it.get('data') or datetime.now().strftime('%d/%m/%Y')
        )
        db.session.add(f)
    db.session.commit()
    return jsonify({'ok':True})

# ---------- STATIC ----------
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
