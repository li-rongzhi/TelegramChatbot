from datetime import datetime
from pymongo import MongoClient
from utils.utils import GENERAL

class MongoDB:
    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.client = None

    def connect(self):
        try:
            self.client = MongoClient(self.host, self.port)
            print("Connected to MongoDB")
        except Exception as e:
            print(f"Error: {e}")

    def initialize(self):
        try:
            db = self.client[self.database]
            collections = db.list_collection_names()
            # Create 'users' collection
            if "users" not in collections:
                db.create_collection("users")
                db.users.create_index([('user_id', 1)], unique=True)

            # Create 'states' collection
            if "states" not in collections:
                db.create_collection('states')
                db.states.create_index([('user_id', 1)], unique=True)
                db.states.create_index([('state', 1)])

            # Create 'tasks' collection
            if "tasks" not in collections:
                db.create_collection('tasks')
                db.tasks.create_index([('user_id', 1), ('task_id', 1)], unique=True)
                db.tasks.create_index([('due', 1)])

            print("MongoDB initialization script executed successfully")
        except Exception as e:
            print("Error executing MongoDB initialization script:", e)

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    def check_user_state(self, user_id: str, target: int) -> bool:
        db = self.client[self.database]
        states_collection = db['states']

        # Find the state for the given user_id
        user_state = states_collection.find_one({'user_id': user_id})

        if user_state is not None and user_state.get('state') == target:
            return True
        else:
            return False

    def get_user_state(self, user_id: str) -> int:
        db = self.client[self.database]
        states_collection = db['states']

        user_state = states_collection.find_one({'user_id': user_id})

        if user_state is not None:
            return user_state.get('state', 0)
        else:
            return None

    def initialize_user_state(self, user_id: str) -> None:
        db = self.client[self.database]
        states_collection = db['states']

        # Try to insert a new document or update an existing one
        result = states_collection.update_one(
            {'user_id': user_id},
            {'$set': {'state': GENERAL}},
            upsert=True  # Creates a new document if it doesn't exist
        )

        if result.modified_count == 0 and not result.upserted_id:
            print("Error initializing user state")

    def update_user_state(self, user_id, new_state) -> None:
        db = self.client[self.database]
        states_collection = db['states']
        result = states_collection.update_one(
            {'user_id': user_id},
            {'$set': {'state': new_state}},
        )

        if result.modified_count == 0:
            print("Error updating user state")

    def add_task(self, user_id, description, duetime, remark):
        db = self.client[self.database]
        tasks_collection = db['tasks']

        # Determine the next task_id for the user
        if tasks_collection.count_documents({'user_id': user_id}) > 0:
            max_task_id = tasks_collection.find({'user_id': user_id}).sort('task_id', -1).limit(1)
            next_task_id = max_task_id[0]['task_id'] + 1
        else:
            next_task_id = 1

        task_document = {
            'user_id': user_id,
            'task_id': next_task_id,
            'isDone': False,
        }

        if description:
            task_document['description'] = description
        else:
            print("No description provided")

        if duetime:
            try:
                datetime_obj = datetime.strptime(duetime, "%Y-%m-%d %H:%M")
                task_document['due'] = datetime_obj
            except ValueError:
                print("Invalid datetime format for 'duetime'")
        if remark:
            task_document['remark'] = remark

        try:
            tasks_collection.insert_one(task_document)
            print("Task added successfully")
        except Exception as e:
            print(f"Error adding task: {e}")

    def delete_task(self, user_id, task_id):
        db = self.client[self.database]
        tasks_collection = db['tasks']

        # Find the task document to delete
        task_to_delete = tasks_collection.find_one({'user_id': user_id, 'task_id': task_id})

        if task_to_delete:
            tasks_collection.delete_one({'_id': task_to_delete['_id']})
            print("Task deleted successfully")

        else:
            print("Task not found")

    def mark_task(self, user_id, task_id):
        db = self.client[self.database]
        tasks_collection = db['tasks']

        result = tasks_collection.update_one(
            {'user_id': user_id, 'task_id': task_id},
            {'$set': {'isDone': True}}
        )

        if result.modified_count == 0:
            print("Task not found or already marked")
        else:
            print("Task marked as done")

    def list_tasks(self, user_id):
        db = self.client[self.database]
        tasks_collection = db['tasks']

        # Query tasks for the specified user
        tasks = tasks_collection.find({'user_id': user_id})

        task_list = [
            {
                'task_id': task['task_id'],
                'description': task.get('description', None),
                'isDone': task['isDone'],
                'remark': task.get('remark', None),
                'due': task.get('due', None)
            }
            for task in tasks
        ]

        return task_list