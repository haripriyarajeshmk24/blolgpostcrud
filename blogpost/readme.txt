### BlogPost Application - README

#### Overview
The **BlogPost Application** is a FastAPI-based web application for managing blog posts.
It provides features like user authentication, role-based access control, and CRUD operations on posts and comments.
The application supports two user roles: `admin` and `user`.

- **Admin**: Can view all posts and manage users.
- **User**: Can view and manage only their posts.


#### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/haripriyarajeshmk24/blolgpostcrud
   cd blogpost
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python3 -m venv venv
   ```

3. **Install Dependencies**
   ```bash
   pip install fastapi
   pip install sql_alchemy
   pip install python-crypto
   pip install python-decouple
   ```

4. **Set Up the Database**
   - Create a PostgreSQL database named `fastapi`.
   - Connect with database providing your username and password

5. **Provide mandatory datas in `.env` file**
   ```
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ```

6. **Run the Application**
   ```bash
   uvicorn blogpost.main:app --reload
   ```

7. **Access the Application**
   - Open your browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs) for the API documentation.





