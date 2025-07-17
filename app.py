from flask import Flask, render_template, request, redirect, url_for, send_file, session
from utils.pdf_generator import genera_pdf
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'  # scegli una password più sicura in produzione


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('step1'))
        else:
            error = 'Username o password errati'
            return render_template('login.html', error=error)
    return render_template('login.html')


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    session.clear()
    return redirect(url_for('login'))  # obbliga login prima di tutto


@app.route('/step1', methods=['GET', 'POST'])
@login_required
def step1():
    if request.method == 'POST':
        session['cliente_nome'] = request.form['nome']
        session['cliente_email'] = request.form['email']
        session['cliente_azienda'] = request.form.get('azienda', '')
        return redirect(url_for('step2'))
    return render_template('step1.html')


@app.route('/step2', methods=['GET', 'POST'])
@login_required
def step2():
    if 'pagine_dettaglio' not in session:
        session['pagine_dettaglio'] = {}

    if request.method == 'POST':
        nome_pagina = request.form['nome_pagina']
        moduli = request.form.getlist('moduli')
        if nome_pagina:
            session['pagine_dettaglio'][nome_pagina] = moduli
            session.modified = True
        return redirect(url_for('step2'))  # reload per aggiungere più pagine

    return render_template('step2.html', pagine=session['pagine_dettaglio'])


@app.route('/step3', methods=['GET', 'POST'])
@login_required
def step3():
    if request.method == 'POST':
        session['features'] = {
            'eventi': request.form.get('eventi'),
            'prenotazioni': request.form.get('prenotazioni'),
            'appuntamenti': request.form.get('appuntamenti'),
            'email': 'email' in request.form,
            'dominio': 'dominio' in request.form
        }
        return redirect(url_for('result'))
    return render_template('step3.html')


@app.route('/result')
@login_required
def result():
    pdf_path, ore, costo = genera_pdf(session)
    session['pdf_path'] = pdf_path
    pdf_url = url_for('static', filename=os.path.basename(pdf_path))
    return render_template('result.html',
                           ore=ore,
                           costo=costo,
                           pdf_url=pdf_url)


@app.route('/view_pdf')
@login_required
def view_pdf():
    if 'pdf_path' not in session:
        return redirect(url_for('result'))

    pdf_url = url_for('static', filename=os.path.basename(session['pdf_path']))
    return render_template('view_pdf.html', pdf_url=pdf_url)


@app.route('/download')
@login_required
def download():
    if 'pdf_path' not in session:
        return redirect(url_for('result'))
    return send_file(session['pdf_path'], as_attachment=True)


@app.route('/remove_page/<nome>')
@login_required
def remove_page(nome):
    pagine = session.get('pagine_dettaglio', {})
    if nome in pagine:
        del pagine[nome]
        session['pagine_dettaglio'] = pagine
        session.modified = True
    return redirect(url_for('step2'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
