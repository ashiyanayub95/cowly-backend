
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @property
    def SECRET_KEY(self):
        return os.getenv("SECRET_KEY")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
