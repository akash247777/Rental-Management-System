from app import app

if __name__ == '__main__':
    print("Starting rental data management backend server...")
    app.run(debug=True, port=5000) 