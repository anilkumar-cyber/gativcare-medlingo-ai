"""Phase 3: implement against doctors table."""


async def get_doctor(doctor_id):
    raise NotImplementedError


async def is_available(doctor_id, slot) -> bool:
    raise NotImplementedError


async def search(query: str):
    raise NotImplementedError  # called by app.ai.tools.builtin.DoctorSearchTool
