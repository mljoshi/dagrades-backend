from config import db
from sqlalchemy.dialects.sqlite import JSON


class Course(db.Model):
    courseId = db.Column(db.Integer, primary_key=True)
    sectionName = db.Column(db.String(80), unique=False, nullable=False)
    courseName = db.Column(db.String(120), unique=False, nullable=False)
    instructorName = db.Column(db.String(120), unique=False, nullable=False)
    secondaryInstructorName = db.Column(db.String(120), unique=False, nullable=True)
    gradeDist = db.Column(JSON, nullable=False)
    term = db.Column(db.String(20), unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    numStudents = db.Column(db.Integer, unique=False, nullable=False)
    termNum = db.Column(db.Integer, unique=False, nullable=False)

    def toJson(self):
        return {
                "courseId": self.courseId,
                "sectionName": self.sectionName,
                "courseName": self.courseName,
                "instructorName": self.instructorName,
                "secondaryInstructorName": self.secondaryInstructorName,
                "gradeDist": self.gradeDist,
                "term": self.term,
                "year": self.year,
                "numStudents": self.numStudents,
                "termNum": self.termNum
        }
    def toList(self):
        return [self.courseId, self.sectionName, self.courseName, self.instructorName, self.secondaryInstructorName] + [str(v) for (k,v) in self.gradeDist.items()] + [self.term, str(self.year), 0]