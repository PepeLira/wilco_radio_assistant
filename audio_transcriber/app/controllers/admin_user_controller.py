from app.models.admin_user import AdminUser
from peewee import DoesNotExist

class AdminUserController:
    @staticmethod
    def add_admin_user(name, email, company):
        """Add a new AdminUser to the database."""
        try:
            user = AdminUser.create(name=name, email=email, company=company)
            return user
        except Exception as e:
            print(f"Error adding user: {e}")
            return None

    @staticmethod
    def get_admin_user(user_id=None, email=None):
        """Retrieve an AdminUser by ID or email."""
        try:
            if user_id:
                return AdminUser.get(AdminUser.id == user_id)
            elif email:
                return AdminUser.get(AdminUser.email == email)
            else:
                raise ValueError("Either user_id or email must be provided.")
        except DoesNotExist:
            print("AdminUser not found.")
            return None

    @staticmethod
    def remove_admin_user(user_id):
        """Remove an AdminUser from the database by ID."""
        try:
            user = AdminUser.get(AdminUser.id == user_id)
            user.delete_instance()
            return True
        except DoesNotExist:
            print("AdminUser not found.")
            return False