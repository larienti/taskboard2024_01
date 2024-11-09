def create_app(config_name=None):
    # ... existing setup code ...

    @app.route('/test-db')
    def test_db():
        try:
            # Try raw psycopg2 connection first
            conn = psycopg2.connect(
                dbname="railway",
                user="postgres",
                password="UvVNaBnMprSeoBhjIVolZzExVXKGiqAA",
                host="postgres.railway.internal",
                port="5432"
            )
            conn.close()
            
            # Then try SQLAlchemy
            db.session.execute('SELECT 1')
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Database connection successful',
                'config': {
                    'host': app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1].split('/')[0],
                    'database': app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1],
                    'user': 'postgres'
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'uri': app.config['SQLALCHEMY_DATABASE_URI'].replace(
                    app.config.get('DB_PASSWORD', ''), '***'
                )
            }, 500

    return app