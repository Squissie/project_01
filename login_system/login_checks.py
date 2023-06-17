from .models import User

## This file defines some login verification functions, used as decorators

def check_doctor(user):
    if user.is_anonymous:
        return False
    return user.role == User.Role.DOCTOR


def check_nurse(user):
    if user.is_anonymous:
        return False
    return user.role == User.Role.NURSE


def check_admin(user):
    if user.is_anonymous:
        return False
    return user.role == User.Role.ADMIN


def check_doctor_nurse(user):
    if user.is_anonymous:
        return False
    return user.role in (User.Role.DOCTOR, User.Role.NURSE)
