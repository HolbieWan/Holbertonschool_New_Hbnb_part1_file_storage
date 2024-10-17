from base_model import BaseModel
from email_validator import validate_email, EmailNotValidError


class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.places = []

    def add_place(self, place):
        self.places.append(place)    
    
    def is_valid(self):
        try:
            if not all(isinstance(attr, str) for attr in [self.email, self.first_name, self.last_name]):
                raise TypeError("email, first_name, and last_name must be strings (str).")
            
            if len(self.first_name) > 50 or len(self.last_name) > 50:
                raise ValueError("first_name and last_name must be less than 50 characters.")

            valid = validate_email(self.email)
            return valid.email

        except TypeError as te:
            print(f"Type error: {str(te)}")
            return False
        
        except EmailNotValidError as e:
            print(f"E-mail not valid: {str(e)}")
            return False

        except ValueError as ve:
            print(f"Value error: {str(ve)}")
            return False

    def to_dict(self):
        return {
            "user_id" : self.id,
            "first_name" : self.first_name,
            "last_name" : self.last_name,
            "email" : self.email,
            "is_admin" : self.is_admin,
            "places" : self.places,
            "created_at" : self.created_at,
            "updated_at" : self.updated_at
        }
