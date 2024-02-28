from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId 
from bson.errors import InvalidId 
# from bson.errors import InvalidId as BSONInvalidId

# Initialize Flask app
app = Flask(__name__)

# Configure Flask app
app.config['JWT_SECRET_KEY'] = 'OvEjf-zLC4-nJmHRRfAmDdQD6ncwq8u14LtE3NXzSKFArjI413AN1Tj2HGCC0hIH' 
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
jwt = JWTManager(app)

# Connect to MongoDB
client = MongoClient('mongodb+srv://piyushchaukade21:SyW8IF9J8mCn4tQ3@cluster0.1lseizv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client['Todo_py']


users = db['users']

sample_user = {
    'username': 'user1',
    'password': 'password1'
}

sample_todo = {
    'id':'sample id',
    'name': 'Sample Todo',
    'description': 'This is a sample todo item',
   'created_at': 'sample created_at',  
}
# Middleware for JWT token validation
@app.before_request
@jwt_required()
def jwt_token_validation():
    pass

# Middleware for input validation
@app.before_request
def input_validation():
    operation = request.args.get('operation', '').upper()
    
    if operation in ['POST', 'PUT']:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'JSON data is required for this operation'}), 400
        required_fields = ['name', 'description', 'created_at']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required in the JSON data'}), 400

# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    #storing user data directly in MongoDB
    users.insert_one(sample_user)
    return jsonify({'message': 'User registered successfully'}), 200

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    #authenticate user directly from MongoDB
    user = users.find_one({'username': username, 'password': password})
    if user:
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Protected endpoint for creating a new todo item
@app.route('/todos', methods=['POST'])
def create_todo():
    current_user = get_jwt_identity()
    # For demonstration purposes, simply return the sample todo item
    return jsonify(sample_todo), 200

# Terminal input for performing CRUD operations
if __name__ == '__main__':
    while True:
        operation = input("Enter operation (GET, PUT, POST, DELETE): ").upper()
        
        if operation == 'GET':
              # Input 'ALL' to retrieve all data or enter ID of todo to retrieve
            todo_id_or_all = input("Enter 'ALL' to retrieve all todos or enter ID of todo to retrieve: ")

            if todo_id_or_all.upper() == 'ALL':
                # Get all database data
                data = list(db['todos'].find({}, {'_id': False}))
                print(data)
            else:
                # Retrieve specific todo item from database by ID
                try:
                    todo_item = db['todos'].find_one({'_id': ObjectId(todo_id_or_all)}, {'_id': False})
                    
                    if todo_item:
                        print(todo_item)
                    else:
                        print("No data found with the provided ID")
                except InvalidId:
                    print("Invalid ID provided")
        elif operation == 'POST':
            # Input data for POST operation
            todo_data = {
                'id':input("Enter id: "),
                'name': input("Enter name: "),
                'description': input("Enter description: "),
                'created_at': input("Anter created_at: ")
            }
            # Insert data into database
            db['todos'].insert_one(todo_data)
            print("Data inserted successfully")
        elif operation == 'PUT':
            # Input data for PUT operation
            todo_id = input("Enter ID of todo to update: ")  # ID is a string here
            try:
                    existing_todo = db['todos'].find_one({'_id': ObjectId(todo_id)})
                    if existing_todo:
                        todo_data = {
                            'id':input("Enter new id: "),
                            'name': input("Enter new name: "),
                            'description': input("Enter new description: "),
                            'created_at': input("Enter new created_at: ")
                        }
                        # Update data in database by ID
                        db['todos'].update_one({'_id': ObjectId(todo_id)}, {'$set': todo_data}, upsert=True)
                        print("Data updated successfully")
                    else:
                        print("No data found with the provided ID")
            except InvalidId:
                print("Invalid ID provided")
           
        elif operation == 'DELETE':
            # Input data for DELETE operation
            todo_id = input("Enter ID of todo to delete: ")  # ID is a string here
            try:
                # Delete data from database by ID
                result = db['todos'].delete_one({'_id': ObjectId(todo_id)})  # Import ObjectId from pymongo
                if result.deleted_count == 1:
                    print("Data deleted successfully")
                else:
                    print("No data found with the provided ID")
            except InvalidId:
                print("Invalid ID provided")