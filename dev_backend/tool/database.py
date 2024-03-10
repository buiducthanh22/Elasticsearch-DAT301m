# from Vietocr.predictOCR import Rec_text
from source.paddle_OCR import Rec_text
from tool.postgre import PostgreSQLManager

from PIL import Image
from transformers import AutoTokenizer, AutoModel
from io import BytesIO
from elasticsearch import Elasticsearch

import numpy as np
import os
import torch
import psycopg2
import base64
import configparser

config = configparser.ConfigParser()
config.read(r"C:\DAT301m\dev_backend\data\example.ini")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


tokenizer = AutoTokenizer.from_pretrained\
('sentence-transformers/all-mpnet-base-v2')
model = AutoModel.from_pretrained\
('sentence-transformers/all-mpnet-base-v2')


class Data_base:
    """A class to interact with a PostgreSQL database.

    Attributes:
        conn: A psycopg2 connection object.
        cur: A psycopg2 cursor object.
        db: A PostgreSQLManager object.

    Methods:
        return_path: Returns the current working directory.
        text: Extracts text from an image using BOCR.
        vector: Converts text to a dense vector using a pre-trained
        language model.
        up_data: Inserts a new data entry into the database.
        run_pgsync: Synchronizes the database schema with a given schema file.
    """
    def __init__(self):
        """Initializes the database connection."""
        self.conn = psycopg2.connect(
            dbname="thanhbd",
            user="postgres",
            password="1",
            host="localhost",
            port="5432"
        )
        self.es = Elasticsearch(
            cloud_id=config['ELASTIC']['cloud_id'],
            basic_auth=(config['ELASTIC']['user'],config['ELASTIC']['password'])
        )
        self.postgresql_table_name = "data"
        self.elasticsearch_index_name = "demo"
        self.cur = self.conn.cursor()
        self.db = PostgreSQLManager(
            dbname="thanhbd",
            user="postgres",
            password="1",
            # host="172.22.0.1",
            host="localhost",
            port="5432"
            )

    def return_path(self):
        """Returns the current working directory.

        Returns:
            A string representing the current working directory.
        """
        path = str(os.getcwd())
        path = path.replace("\\", "/")
        return path

    def text(self, image):
        """Extracts text from an image using OCR.

        Args:
            image: A base64-encoded image.

        Returns:
            A string containing the extracted text.
        """
        a = Rec_text()
        try:
            
            labels = a(image)
        except Exception:
            return "="
        return labels

    def vector(self, text):
        """Converts text to a dense vector using a pre-trained language model.

        Args:
            text: A string containing the text to be converted.

        Returns:
            A list containing the dense vector representation of the text.
        """
        data = text.split(' ')
        if len(data) > 1:
            inputs = tokenizer(text, padding=True,
                               truncation=True, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
                embeddings = outputs.last_hidden_state
            dense_vector = torch.mean(embeddings, dim=1)
            dense_vector = dense_vector.tolist()
            dense_vector = dense_vector[0]
            return dense_vector
        else:
            if len(data[0]) > 1:
                inputs = tokenizer(text, padding=True,
                                   truncation=True, return_tensors="pt")
                with torch.no_grad():
                    outputs = model(**inputs)
                    embeddings = outputs.last_hidden_state
                dense_vector = torch.mean(embeddings, dim=1)
                dense_vector = dense_vector.tolist()
                dense_vector = dense_vector[0]
                return dense_vector
            else:
                num_dimensions = 768
                default_value = 1e-10
                dense_vector = np.full(num_dimensions, default_value)
                dense_vector = dense_vector.tolist()
                return dense_vector

    def normalize_vector(self, vector):
        """
        After converting the text into a vector,
        use the normalize_vector function to normalize the vector.

        Args:
            vector: A vector after converting text to vector.

        Returns:
            nor_vector: Returns the normalized vector.
        """
        vector_array = np.array(vector)
        norm = np.linalg.norm(vector_array)
        if norm == 0:
            return vector
        nor_vector = vector_array/norm
        nor_vector = nor_vector.tolist()
        return nor_vector

    def up_data(self, name, base64_data):
        """Inserts a new data entry into the database.

        Args:
            name (str): The name of the data entry.
            base64_data (str): The base64-encoded image data.

        Returns:
            None.
        """
        split_data = base64_data.split(",", 1)
        base64_only = split_data[1]
        image_data = base64.b64decode(base64_only)
        self.cur.execute("SELECT * FROM data WHERE name = %s", (name, ))
        if not self.cur.fetchone():
            im1 = Image.open(BytesIO(image_data))
            im = im1.convert('RGB')
            buff = BytesIO()
            im.save(buff, format="JPEG")
            image_base64 = base64.b64encode(buff.getvalue()).decode("utf-8")
            labels = self.text(image_base64)
            print(labels)
            vectors = self.vector(labels)
            nor_vector = self.normalize_vector(vectors)
            labels = [labels]
            data = (name, labels, nor_vector, base64_only)
            self.db.insert_data('data', data)
        self.conn.commit()

    def run_pgsync(self):
        """
        Synchronizes data from a PostgreSQL table to an Elasticsearch index.

        Assumes the instance has a `cur` (cursor) attribute for PostgreSQL interaction,
        an `elasticsearch_index_name` attribute for the target index, and an `es`
        attribute for Elasticsearch connection.
        """
        self.cur.execute(f"SELECT * FROM {self.postgresql_table_name}")
        bulk_data = []
        for record in self.cur.fetchall():
            bulk_data.append(
                {"index": {"_index": self.elasticsearch_index_name, "_id": str(record[0])}}
            )
            bulk_data.append( {
                "id": str(record[0]),
                "name": record[1],
                "label": record[2],
                "vector": record[3],
                "image": record[4],
            })
            self.es.bulk(body=bulk_data, refresh=True)