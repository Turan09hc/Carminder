from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚗 CarMinder starting...")
    print("Access: http://localhost:5000/admin")
    app.run(debug=True)