from views.login import create_login_window
from app import create_main_application

if __name__ == "__main__":
    create_login_window(on_login_success=create_main_application)
