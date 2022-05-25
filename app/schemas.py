from lib2to3.pgen2.token import OP
from pydantic import BaseModel
from typing import List, Optional

class StudentBase(BaseModel):
    student_id: int

class Student(StudentBase):
    student_id: Optional[int]
    phone_number: str
    first_name: str
    last_name: str
    nationality: str
    gender: str

class StudentClassLookup(StudentBase):
    student_id: Optional[int]
    phone_number: str
    first_name: str
    last_name: str
    nationality: str
    gender: str
    term: str
    year: int
    course_list: str

class PartTimeLookup(BaseModel):
    term: str
    year: int
    first_name_filter: Optional[str]
    last_name_filter: Optional[str]
    nationality_filter: Optional[str]
    gender_filter: Optional[str]

class StudentCreate(Student):
    pass

class StudentUpdate(Student):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    nationality: Optional[str]
    gender: Optional[str]

class Semester(BaseModel):
    sem_id: Optional[int]
    year: int
    term: str

class Enrollment(BaseModel):
    student_id: int
    course_id: int
    term: str
    year: int

class ClassBase(BaseModel):
    course_id: Optional[int]
    credits: int

class Class(ClassBase):
    term: str
    year: int
