from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.images import ImageFile
from django.contrib.auth.decorators import user_passes_test, login_required
from login_system.models import User, Doctor, Nurse
from login_system.login_checks import *
from django.contrib import messages
from .models import *
from .forms import *
from .filters import *
from .xrayML import *
import datetime

from .xrayML import *

## This file deals with nurse/doctor facing pages

## Main homepage, landing page when doctor/nurse logs in
@user_passes_test(check_doctor_nurse)
def home(request):
    # patients assigned to the doctor only
    if request.user.role == User.Role.DOCTOR:
        all_patients = PatientModel.objects.filter(assigned_user=request.user)
    else:
        all_patients = PatientModel.objects.all()
    # get latest consultation dates
    for p in all_patients:
        if latest := ConsultationModel.objects.filter(patient=p).first():
            p.latest_consultation = latest # type:ignore assignging new class variables is fine

    context = {"patients": all_patients}
    return render(request, "home.html", context)

## Page listing all patients, with filter
@user_passes_test(check_doctor_nurse)
def patientRecords(request):
    all_patients = PatientModel.objects.all()

    myFilter = PatientFilter(request.GET, queryset=all_patients)
    patients = myFilter.qs

    page = request.GET.get("page", 1)

    paginator = Paginator(patients, 5)

    try:
        patients = paginator.page(page)
    except PageNotAnInteger:
        patients = paginator.page(1)
    except EmptyPage:
        patients = paginator.page(paginator.num_pages)

    context = {"patients": patients, "myFilter": myFilter}
    return render(request, "patientRecords.html", context)

## Page for adding a new patient
@user_passes_test(check_nurse)
def addPatient(request):
    if request.method == "POST":
        form = PatientEditForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Saved patient {patient.firstName}.")
            form = PatientEditForm()
            return redirect("patientProfile", patient.id)
        else:
            messages.error(request, f"Could not create patient!")
    else:
        form = PatientEditForm()
    return render(request, "addPatient.html", {"form": form})

## Quick-access page for adding a new empty consultation
@user_passes_test(check_nurse)
def patientProfileAdd(request, patient_id):
    patient = get_object_or_404(PatientModel, id=patient_id)
    f = ConsultationNewForm()
    f.save(patient)
    return redirect("patientProfile", patient_id)


## Page for viewing a specific patient, the main page doctors will be working with
@user_passes_test(check_doctor_nurse)
def patientProfile(request, patient_id):
    patient = get_object_or_404(PatientModel, id=patient_id)

    ## get all the patient's images
    patient.images = ImageModel.objects.filter(patient=patient) # type:ignore assignging new class variables is fine
    consultations = ConsultationModel.objects.filter(patient=patient)
    ## get images of each consultation
    for c in consultations:
        images = patient.images.filter(consultation=c) # type:ignore assignging new class variables is fine
        c.images = images # type:ignore assignging new class variables is fine

    d_now = datetime.date.today()
    ## calculate age: subtract years, then reduce by 1 if current day of year is before birthday
    patient_age = d_now.year - patient.dateofbirth.year
    if d_now.replace(year=patient.dateofbirth.year) < patient.dateofbirth:
        patient_age -= 1

    ## nurse assigning patient to a doctor
    if request.method == "POST":
        assign_form = PatientAssignForm(request.POST, instance=patient)
        assign_form.save()
        messages.success(request, f"Patient {patient} assigned!")
    else:
        assign_form = PatientAssignForm(instance=patient)

    context = {
        "patient": patient,
        "consultations": consultations,
        "patient_age": patient_age,
        "assigned_user": patient.assigned_user,
        "assign_form": assign_form,
    }
    return render(request, "patientProfile.html", context)

## Page for adding consultation details
@user_passes_test(check_doctor)
def editConsultation(request, consultation_id):
    cons = get_object_or_404(ConsultationModel, id=consultation_id)
    if request.method == "POST":
        form = ConsultationEditForm(request.POST, instance=cons)
        if form.is_valid():
            form.save(cons.patient)
            messages.success(
                request, f"Saved consultation for patient {cons.patient.firstName}."
            )
            ## unassign doctor after having edited consultation (remove from the doctor's homepage queue)
            if cons.patient.assigned_user:
                messages.success(
                    request,
                    f"{cons.patient.firstName} has been unassigned from {cons.patient.assigned_user.username}",
                )
                cons.patient.assigned_user = None
            cons.patient.save()
            return redirect("patientProfile", cons.patient.id) # type:ignore django adds id field automatically
        else:
            messages.error(request, f"Could not create consultation!")
    else:
        form = ConsultationEditForm(instance=cons)
    return render(
        request,
        "addConsultation.html",
        {"form": form, "patient": cons.patient},
    )

## Page for uploading images and running the ML model
@user_passes_test(check_nurse)
def addImage(request, consultation_id):
    consultation = get_object_or_404(ConsultationModel, id=consultation_id)
    patient = consultation.patient
    if request.method == "POST":
        form = ImageEditForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(patient, consultation)
            prediction, cam = predictXray(img.image.url)
            ## not every prediction generates a class activation map
            if cam:
                img.cam.save("image_cam", ImageFile(cam))
            img.result = prediction
            img.save()
            messages.success(request, f"Saved image for patient {patient.firstName}.")
            return redirect("patientProfile", patient.id) # type:ignore django adds id field automatically
        else:
            messages.error(request, f"Could not save image!")
    else:
        form = ImageEditForm()
    return render(
        request,
        "addImage.html",
        {
            "form": form,
            "consultation": consultation,
            "patient": patient,
        },
    )
