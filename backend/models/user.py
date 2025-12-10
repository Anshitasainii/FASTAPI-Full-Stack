from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, MetaData, Date, Text
from sqlalchemy.sql.sqltypes import Integer,String
from config.db import meta
users= Table(
    'users',meta,
    Column('id',Integer,primary_key = True),
    Column('name',String(225)),
    Column('email',String(225)),
    Column('password',String(225)),
    Column("otp", String(6), nullable=True),
    Column("otp_expiry", DateTime, nullable=True),
    Column("verified", Boolean, default=False),
    Column("profile_image", String(500),nullable=True),
    Column("first_name", String(100), nullable=True),
    Column("last_name", String(100), nullable=True),
    Column("dob", Date, nullable=True),
    Column("mobile", String(20), nullable=True),
    Column("professional_summary", Text, nullable=True),
    Column("gender", String(20), nullable=True),
    Column("job_status", String(50), nullable=True)
)