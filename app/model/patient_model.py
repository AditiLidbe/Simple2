from sqlalchemy import Column, String, Integer, ForeignKey
from ..db.base import Base

class Patient_Model(Base):
    __tablename__="patient_model"
    id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    