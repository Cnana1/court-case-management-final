from backend import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Role = db.Column(db.Enum('Clerk', 'Judge', 'Attendee', name='user_role_enum'), nullable=False)
    Email = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)

    requests = db.relationship('Request', backref='user', lazy=True)
    user_court_dates = db.relationship('UserCourtDate', backref='user', lazy=True)


class Case(db.Model):
    __tablename__ = 'case'
    CaseID = db.Column(db.Integer, primary_key=True)
    Description = db.Column(db.Text, nullable=False)
    Status = db.Column(db.Enum('Open', 'Closed', 'Pending', name='case_status_enum'), default='Open')

    court_dates = db.relationship('CourtDate', backref='case', lazy=True)
    requests = db.relationship('Request', backref='case', lazy=True)

    assigned_attendees = db.relationship(
        "CaseAttendee",
        backref="case",
        cascade="all, delete-orphan",
        lazy="joined"
    )


class CaseAttendee(db.Model):
    __tablename__ = "case_attendee"

    ID = db.Column(db.Integer, primary_key=True)
    CaseID = db.Column(db.Integer, db.ForeignKey("case.CaseID"), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey("user.UserID"), nullable=False)

    user = db.relationship("User", lazy="joined")


class CourtDate(db.Model):
    __tablename__ = 'courtdate'
    CourtDateID = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.Date, nullable=False)
    Time = db.Column(db.Time, nullable=False)
    Location = db.Column(db.String(100), nullable=False)
    CaseID = db.Column(db.Integer, db.ForeignKey('case.CaseID', ondelete='CASCADE'))

    user_court_dates = db.relationship('UserCourtDate', backref='courtdate', lazy=True)


class UserCourtDate(db.Model):
    __tablename__ = 'usercourtdate'
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID', ondelete='CASCADE'), primary_key=True)
    CourtDateID = db.Column(db.Integer, db.ForeignKey('courtdate.CourtDateID', ondelete='CASCADE'), primary_key=True)


class Request(db.Model):
    __tablename__ = 'request'
    RequestID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID', ondelete='CASCADE'))
    CaseID = db.Column(db.Integer, db.ForeignKey('case.CaseID', ondelete='CASCADE'))
    Reason = db.Column(db.Text, nullable=False)
    Status = db.Column(db.Enum('Pending', 'Approved', 'Denied', name='request_status_enum'), default='Pending')
    FileUpload = db.Column(db.String(255))


class RescheduleRequest(db.Model):
    __tablename__ = "reschedule_requests"

    RequestID = db.Column(db.Integer, primary_key=True)
    CaseID = db.Column(db.Integer, db.ForeignKey("case.CaseID"), nullable=False)
    OldDateID = db.Column(db.Integer, db.ForeignKey("courtdate.CourtDateID"), nullable=True)  # now nullable
    NewDate = db.Column(db.Date, nullable=False)
    FileAttachment = db.Column(db.String(256), nullable=True)  # keep file optional
    Status = db.Column(db.String(50), default="Pending")
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    case = db.relationship("Case", backref="reschedule_requests")
    old_date = db.relationship("CourtDate", backref="reschedule_requests")
