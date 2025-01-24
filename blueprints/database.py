# from flask import Flask, request, render_template, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# import datetime

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# db = SQLAlchemy(app)

# class Visit(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#     ip_address = db.Column(db.String(50))

# class LiveUser(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     session_id = db.Column(db.String(100), unique=True, nullable=False)
#     ip_address = db.Column(db.String(50))
#     timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# db.create_all()

# @app.before_request
# def track_user_visit():
#     ip = request.remote_addr
#     visit = Visit(ip_address=ip)
#     db.session.add(visit)
#     db.session.commit()

# @app.route('/')
# def index():
#     ip = request.remote_addr
#     session_id = request.cookies.get('session_id')

#     if not session_id:
#         session_id = str(uuid.uuid4())
#         response = redirect(url_for('index'))
#         response.set_cookie('session_id', session_id, max_age=60*60*24*365)
#         return response

#     live_user = LiveUser.query.filter_by(session_id=session_id).first()
#     if not live_user:
#         live_user = LiveUser(session_id=session_id, ip_address=ip)
#         db.session.add(live_user)
#     else:
#         live_user.timestamp = datetime.datetime.utcnow()

#     db.session.commit()

#     live_users = LiveUser.query.filter(LiveUser.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).all()

#     return render_template('index.html', live_users=live_users)

# @app.route('/admin')
# def admin():
#     visits = Visit.query.order_by(Visit.timestamp.desc()).all()
#     live_users = LiveUser.query.filter(LiveUser.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).all()
#     return render_template('admin.html', visits=visits, live_users=live_users)

# if __name__ == '__main__':
#     app.run(debug=True)
