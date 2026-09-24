from django.contrib import admin

from hospital.models import (
    Appointment,
    Department,
    Doctor,
    Feedback,
    HospitalInfo,
    Leadership,
    News,
    PatientInfo,
    Schedule,
    Service,
    UploadedFile,
)

admin.site.register(Department)
admin.site.register(Leadership)
admin.site.register(Doctor)
admin.site.register(Schedule)
admin.site.register(Service)
admin.site.register(News)
admin.site.register(Feedback)
admin.site.register(UploadedFile)
admin.site.register(Appointment)
admin.site.register(PatientInfo)
admin.site.register(HospitalInfo)
