from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os  # Fixed import

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Reduces overhead
db = SQLAlchemy(app)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        if not task_content.strip():  # Prevent empty tasks
            return redirect('/')
            
        new_task = ToDo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"There was an error: {str(e)}", 500

    else:
        tasks = ToDo.query.order_by(ToDo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = ToDo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = ToDo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"Unexpected error occurred: {str(e)}", 500
    
    else:
        return render_template('update.html', task=task)

if __name__ == "__main__":
    if 'PORT' in os.environ:
        port = int(os.environ.get('PORT'))
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(debug=True)