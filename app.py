from flask import Flask, render_template, request, jsonify
import nest_asyncio
import os
from werkzeug.utils import secure_filename
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
nest_asyncio.apply()


app = Flask(__name__)


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf'}


os.environ['OPENAI_API_KEY'] = 'OPENAI_API_KEY'
llama_api_key = 'LLAMA_API_KEY'


parser = LlamaParse(api_key=llama_api_key, result_type="markdown")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():

    if 'uploaded_file' not in request.files:
        return jsonify({"response": "No file uploaded"}), 400

    file = request.files['uploaded_file']


    if file.filename == '':
        return jsonify({"response": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)


        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()


        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()

        user_query = request.form.get('query')

        response = query_engine.query(user_query)

        return jsonify(response=response.response)

    return jsonify({"response": "Invalid file type"}), 400

if __name__ == '__main__':

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)