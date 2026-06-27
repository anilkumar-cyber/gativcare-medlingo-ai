"""Phase 3: implement against appointments table. book()/reschedule() are the PRD's exposed
interface (docs/MODULES.md); also called by app.ai.tools.builtin.AppointmentSchedulingTool."""


async def book(medical_case_id, doctor_id, slot):
    raise NotImplementedError


async def reschedule(appointment_id, new_slot):
    raise NotImplementedError
