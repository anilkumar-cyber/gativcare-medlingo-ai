"use client";

import { getToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

const json = (body: unknown) => JSON.stringify(body);

// -- auth / organizations --------------------------------------------------
export const api = {
  login: (email: string, password: string) =>
    apiFetch<{ access_token: string; token_type: string }>("/api/v1/auth/login", {
      method: "POST",
      body: new URLSearchParams({ username: email, password }),
    }),
  me: () =>
    apiFetch<{ id: string; org_id: string; email: string; full_name: string | null; role_name: string | null; permissions: string[] }>(
      "/api/v1/auth/me",
    ),

  orgSignup: (payload: { org_name: string; owner_email: string; owner_password: string; owner_full_name?: string }) =>
    apiFetch<{ organization: { id: string; name: string }; access_token: string }>("/api/v1/organizations/signup", {
      method: "POST",
      body: json(payload),
    }),
  myOrganization: () => apiFetch<{ id: string; name: string; domain: string | null; subscription_tier: string }>("/api/v1/organizations/me"),

  // -- hospitals --
  listHospitals: () => apiFetch<Hospital[]>("/api/v1/hospitals/"),
  createHospital: (payload: { name: string; city?: string; country?: string }) =>
    apiFetch<Hospital>("/api/v1/hospitals/", { method: "POST", body: json(payload) }),

  // -- doctors --
  listDoctors: () => apiFetch<Doctor[]>("/api/v1/doctors/"),
  createDoctor: (payload: { full_name: string; specialty?: string; languages?: string[]; hospital_id?: string }) =>
    apiFetch<Doctor>("/api/v1/doctors/", { method: "POST", body: json(payload) }),

  // -- patients --
  listPatients: () => apiFetch<Patient[]>("/api/v1/patients/"),
  createPatient: (payload: { full_name: string; email?: string; phone?: string; preferred_language?: string }) =>
    apiFetch<Patient>("/api/v1/patients/", { method: "POST", body: json(payload) }),
  getPatient: (patientId: string) => apiFetch<Patient>(`/api/v1/patients/${patientId}`),
  createCase: (patientId: string) => apiFetch<MedicalCase>(`/api/v1/patients/${patientId}/cases`, { method: "POST" }),
  getCase: (caseId: string) => apiFetch<MedicalCase>(`/api/v1/patients/cases/${caseId}`),
  listCases: (patientId: string) => apiFetch<MedicalCase[]>(`/api/v1/patients/${patientId}/cases`),
  createPatientLogin: (patientId: string, payload: { email: string; password: string }) =>
    apiFetch<{ access_token: string; email: string }>(`/api/v1/patients/${patientId}/login`, { method: "POST", body: json(payload) }),

  // -- appointments --
  bookAppointment: (payload: { medical_case_id: string; doctor_id: string; scheduled_at: string }) =>
    apiFetch<Appointment>("/api/v1/appointments/", { method: "POST", body: json(payload) }),
  listAppointmentsForCase: (caseId: string) => apiFetch<Appointment[]>(`/api/v1/appointments/case/${caseId}`),

  // -- conversations / AI chat --
  startSession: (payload: { medical_case_id?: string; mode?: string } = {}) =>
    apiFetch<ConversationSession>("/api/v1/conversations/", { method: "POST", body: json(payload) }),
  sendMessage: (sessionId: string, payload: { text: string; patient_id?: string; medical_case_id?: string; target_lang?: string; task?: string }) =>
    apiFetch<MessageOut>(`/api/v1/conversations/${sessionId}/messages`, { method: "POST", body: json(payload) }),
  listTurns: (sessionId: string) => apiFetch<ConversationTurn[]>(`/api/v1/conversations/${sessionId}/turns`),
};

export type Hospital = { id: string; name: string; city: string | null; country: string | null };
export type Doctor = { id: string; full_name: string; specialty: string | null; languages: string[]; hospital_id: string | null };
export type Patient = { id: string; full_name: string; email: string | null; phone: string | null; preferred_language: string | null };
export type MedicalCase = { id: string; patient_id: string; stage: string; assigned_doctor_id: string | null };
export type Appointment = { id: string; medical_case_id: string; doctor_id: string; scheduled_at: string; status: string };
export type ConversationSession = { id: string; medical_case_id: string | null; mode: string; started_at: string; ended_at: string | null };
export type ConversationTurn = { id: string; session_id: string; content: string; confidence: number; flags: string[]; created_at: string };
export type MessageOut = { content: string; confidence: number; flags: string[]; emergency: boolean; intent: string };
