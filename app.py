from flask import Flask, render_template, request, redirect, url_for
import json
import pandas as pd
import os

app = Flask(__name__)

FILENAME = 'produtos.json'
CATEGORIES = [
    'Maturado - artesanal',
    'Fresco - artesanal',
]

def load_data():
    if not os.path.exists(FILENAME):
        with open(FILENAME, 'w', encoding='utf-8') as file:
            json.dump([], file)
        return []
    try:
        with open(FILENAME, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Arquivo de dados está corrompido. Reinicializando o arquivo.")
        with open(FILENAME, 'w', encoding='utf-8') as file:
            json.dump([], file)
        return []

def save_data(data):
    with open(FILENAME, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_product', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        quantidade = int(request.form['quantidade'])
        categoria = request.form['categoria']
        data = load_data()
        new_id = get_next_id(data)
        produto = {
            'id': new_id,
            'nome': nome,
            'preco': preco,
            'quantidade': quantidade,
            'vendido': 0,
            'estoque': quantidade,
            'categoria': categoria
        }
        data.append(produto)
        save_data(data)
        return redirect(url_for('view_data'))
    return render_template('create_product.html', categories=CATEGORIES)

@app.route('/view_data')
def view_data():
    data = load_data()
    return render_template('view_data.html', data=data)

@app.route('/update_product/<int:produto_id>', methods=['GET', 'POST'])
def update_product(produto_id):
    data = load_data()
    produto = next((p for p in data if p['id'] == produto_id), None)
    if request.method == 'POST':
        if produto:
            produto['nome'] = request.form['nome']
            produto['preco'] = float(request.form['preco'])
            produto['quantidade'] = int(request.form['quantidade'])
            produto['categoria'] = request.form['categoria']
            produto['estoque'] = produto['quantidade'] - produto['vendido']
            save_data(data)
        return redirect(url_for('view_data'))
    return render_template('update_product.html', produto=produto, categories=CATEGORIES)

@app.route('/delete_product/<int:produto_id>', methods=['POST'])
def delete_product(produto_id):
    data = load_data()
    data = [p for p in data if p['id'] != produto_id]
    save_data(data)
    return redirect(url_for('view_data'))

@app.route('/register_sale', methods=['GET', 'POST'])
def register_sale():
    if request.method == 'POST':
        produto_id = int(request.form['produto_id'])
        quantidade_vendida = int(request.form['quantidade_vendida'])
        data = load_data()
        produto = next((p for p in data if p['id'] == produto_id), None)
        if produto and 0 < quantidade_vendida <= produto['estoque']:
            produto['vendido'] += quantidade_vendida
            produto['estoque'] -= quantidade_vendida
            save_data(data)
        return redirect(url_for('view_data'))
    data = load_data()
    return render_template('register_sale.html', data=data)

@app.route('/generate_report')
def generate_report():
    data = load_data()
    if data:
        df = pd.DataFrame(data)
        df.to_csv('relatorio_produtos.csv', index=False)
    return render_template('report.html')

def get_next_id(data):
    if not data:
        return 1
    return max(produto['id'] for produto in data) + 1

if __name__ == '__main__':
    app.run(debug=True)
