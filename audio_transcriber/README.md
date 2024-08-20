# Radio Audio Transcriber

Este directorio presenta la siguiente estructura:


---
**File Strucure**

:file_folder: audio_transcriber/  
│   ├── :page_facing_up: main.py                 *# The main entry point for the application*  
│   ├── :page_facing_up: README.md               *# Project documentation*  
│   ├── :page_facing_up: requirements.txt        *# List of dependencies for the project*  
│  
├── :file_folder: app/                           *# Core application logic*  
│   │   ├── :page_facing_up: \_\_init\_\_.py         *# Initializes the app package*  
│   │  
│   ├── :file_folder: controllers/               *# Controllers for handling user interactions and flow*  
│   │   ├── :page_facing_up: auth_controller.py  *# Controller for user login/authentication logic*  
│   │   ├── :page_facing_up: main_controller.py  *# Controller for main application logic*  
│   │   ├── :page_facing_up: \_\_init\_\_.py         *# Initializes the controllers package*  
│   │  
│   ├── :file_folder: models/                    *# Data models representing the application's state*  
│   │   ├── :page_facing_up: admin_user.py       *# Model for storing admin user data*  
│   │   ├── :page_facing_up: audio_clip.py       *# Model for storing audio clip data*  
│   │   ├── :page_facing_up: \_\_init\_\_.py         *# Initializes the models package*  
│   │  
│   ├── :file_folder: services/                  *# Core services and business logic*  
│   │   ├── :page_facing_up: audio_input.py      *# Handles audio input and recording*  
│   │   ├── :page_facing_up: audio_processor.py  *# Processes audio data before transcription*  
│   │   ├── :page_facing_up: clip_divider.py     *# Logic for dividing audio into distinct clips*  
│   │   ├── :page_facing_up: \_\_init\_\_.py         *# Initializes the services package*  
│   │  
│   └── :file_folder: views/                     *# User interface components using PyQt*  
│       ├── :page_facing_up: auth_view.py        *# View for user login/authentication UI*  
│       ├── :page_facing_up: main_view.py        *# Main application UI*  
│       ├── :page_facing_up: \_\_init\_\_.py         *# Initializes the views package*  
│  
├── :file_folder: config/                        *# Configuration files*  
│   ├── :page_facing_up: logging_config.py       *# Configuration for logging*  
│   ├── :page_facing_up: settings.py             *# General application settings*  
│  
├── :file_folder: data/                          *# Data storage and management*  
│   ├── :page_facing_up: database.py             *# Manages database connections and operations*  
│   ├── :page_facing_up: \_\_init\_\_.py             *# Initializes the data package*  
│   └── :file_folder: migrations/                *# Database migration scripts (if applicable)*  
│  
└── :file_folder: resources/                     *# Static resources for the application*  
|   ├── :file_folder: images/                    *# Image assets for the UI*  
|   └── :file_folder: stylesheets/               *# Stylesheets for the UI*  

---