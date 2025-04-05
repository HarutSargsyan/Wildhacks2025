from app.services.db import db

class User:
    @staticmethod
    def find_by_email(email):
        return db.users.find_one({'email': email})
    
    @staticmethod
    def create_user(user_data):
        return db.users.insert_one(user_data)
    
    @staticmethod
    def update_user(user_id, update_data):
        return db.users.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )
    
    @staticmethod
    def get_user(user_id):
        return db.users.find_one({'_id': user_id}) 