from app import create_app


app = create_app()

if __name__ == "__main__":
    # for development purpose only
    app.run("0.0.0.0", 5000, debug=True)
