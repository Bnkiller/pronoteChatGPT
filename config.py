class Config:
    SECRET_KEY = "votre_cle_secrete"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:rootpassword@localhost/pronote1"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_SIZE = 10
