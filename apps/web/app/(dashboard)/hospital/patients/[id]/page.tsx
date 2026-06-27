"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, ApiError, type Appointment, type Doctor, type MedicalCase, type Patient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { JourneyTimeline, type Stage } from "@/components/workflow/journey-timeline";

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [cases, setCases] = useState<MedicalCase[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [doctorId, setDoctorId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginCredentials, setLoginCredentials] = useState<{ email: string; password: string } | null>(null);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [creatingLogin, setCreatingLogin] = useState(false);

  const activeCase = cases[0];

  function load() {
    api.getPatient(id).then(setPatient).catch(() => {});
    api.listCases(id).then(setCases).catch(() => {});
    api.listDoctors().then(setDoctors).catch(() => {});
  }

  useEffect(load, [id]);

  useEffect(() => {
    if (activeCase) {
      api.listAppointmentsForCase(activeCase.id).then(setAppointments).catch(() => {});
    }
  }, [activeCase]);

  async function onCreateCase() {
    setBusy(true);
    setError(null);
    try {
      await api.createCase(id);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create case");
    } finally {
      setBusy(false);
    }
  }

  async function onBookAppointment(e: React.FormEvent) {
    e.preventDefault();
    if (!activeCase) return;
    setBusy(true);
    setError(null);
    try {
      await api.bookAppointment({ medical_case_id: activeCase.id, doctor_id: doctorId, scheduled_at: scheduledAt });
      setDoctorId("");
      setScheduledAt("");
      const updated = await api.listAppointmentsForCase(activeCase.id);
      setAppointments(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to book appointment");
    } finally {
      setBusy(false);
    }
  }

  const doctorName = (id: string) => doctors.find((d) => d.id === id)?.full_name ?? id;

  async function onCreateLogin(e: React.FormEvent) {
    e.preventDefault();
    setCreatingLogin(true);
    setLoginError(null);
    try {
      await api.createPatientLogin(id, { email: loginEmail, password: loginPassword });
      setLoginCredentials({ email: loginEmail, password: loginPassword });
    } catch (err) {
      setLoginError(err instanceof ApiError ? err.message : "Failed to create login");
    } finally {
      setCreatingLogin(false);
    }
  }

  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <Card>
        <CardHeader>
          <CardTitle>{patient?.full_name ?? "Patient"}</CardTitle>
        </CardHeader>
        <CardContent>{patient?.email}</CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Portal login</CardTitle>
        </CardHeader>
        <CardContent>
          {loginCredentials ? (
            <p className="text-[var(--text-sm)]">
              Created. Hand these to the patient: <strong>{loginCredentials.email}</strong> / <strong>{loginCredentials.password}</strong>
            </p>
          ) : (
            <form onSubmit={onCreateLogin} className="flex flex-wrap items-end gap-[var(--space-3)]">
              <input required type="email" placeholder="Patient's email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
              <input required type="password" placeholder="Set a password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
              <Button type="submit" disabled={creatingLogin}>{creatingLogin ? "Creating..." : "Create portal login"}</Button>
            </form>
          )}
          {loginError && <p className="mt-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-emergency)]">{loginError}</p>}
        </CardContent>
      </Card>

      {!activeCase ? (
        <Card>
          <CardContent>
            <EmptyState
              title="No medical case yet"
              description="Create one to start tracking this patient's journey and book appointments."
              action={<Button onClick={onCreateCase} disabled={busy}>{busy ? "Creating..." : "Create case"}</Button>}
            />
          </CardContent>
        </Card>
      ) : (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Journey</CardTitle>
            </CardHeader>
            <CardContent>
              <JourneyTimeline currentStage={activeCase.stage as Stage} variant="staff" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Book appointment</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={onBookAppointment} className="flex flex-wrap items-end gap-[var(--space-3)]">
                <select required value={doctorId} onChange={(e) => setDoctorId(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]">
                  <option value="">Select doctor</option>
                  {doctors.map((d) => (
                    <option key={d.id} value={d.id}>{d.full_name}</option>
                  ))}
                </select>
                <input required type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
                <Button type="submit" disabled={busy}>{busy ? "Booking..." : "Book"}</Button>
              </form>
              {error && <p className="mt-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-emergency)]">{error}</p>}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Appointments</CardTitle>
            </CardHeader>
            <CardContent>
              {appointments.length === 0 ? (
                <EmptyState title="No appointments yet" />
              ) : (
                <ul className="flex flex-col gap-[var(--space-2)]">
                  {appointments.map((a) => (
                    <li key={a.id} className="flex items-center justify-between rounded-[var(--radius-sm)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)]">
                      <span className="text-[var(--text-sm)]">{doctorName(a.doctor_id)} -- {new Date(a.scheduled_at).toLocaleString()}</span>
                      <Badge variant={a.status === "scheduled" ? "accent" : "neutral"}>{a.status}</Badge>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
