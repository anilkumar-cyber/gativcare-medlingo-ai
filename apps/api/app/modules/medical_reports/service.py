"""Phase 3: implement against medical_reports table. attach_report() is the PRD's exposed
interface (docs/MODULES.md); get_reports_for_patient() backs medical_twin.service."""


async def attach_report(medical_case_id, file_ref):
    raise NotImplementedError


async def get_reports_for_patient(patient_id):
    raise NotImplementedError
