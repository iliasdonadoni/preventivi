from flask import Flask, render_template, request, redirect, url_for, send_file, session
from utils.pdf_generator import genera_pdf
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    session.clear()
    return redirect(url_for('step1'))


@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        session['cliente_nome'] = request.form['nome']
        session['cliente_email'] = request.form['email']
        session['cliente_azienda'] = request.form.get('azienda', '')
        return redirect(url_for('step2'))
    return render_template('step1.html')


@app.route('/step2', methods=['GET', 'POST'])
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
def result():
    pdf_path, ore, costo = genera_pdf(session)
    session['pdf_path'] = pdf_path
    pdf_url = url_for('static', filename=os.path.basename(pdf_path))
    return render_template('result.html',
                           ore=ore,
                           costo=costo,
                           pdf_url=pdf_url)


@app.route('/view_pdf')
def view_pdf():
    if 'pdf_path' not in session:
        return redirect(url_for('result'))

    pdf_url = url_for('static', filename=os.path.basename(session['pdf_path']))
    return render_template('view_pdf.html', pdf_url=pdf_url)


@app.route('/download')
def download():
    return send_file(session['pdf_path'], as_attachment=True)


@app.route('/remove_page/<nome>')
def remove_page(nome):
    pagine = session.get('pagine_dettaglio', {})
    if nome in pagine:
        del pagine[nome]
        session['pagine_dettaglio'] = pagine
        session.modified = True
    return redirect(url_for('step2'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
