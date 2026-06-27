"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type Doctor, type Hospital } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function HospitalDoctorsPage() {
  const [doctors, setDoctors] = useState<Doctor[] | null>(null);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [fullName, setFullName] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [languages, setLanguages] = useState("");
  const [hospitalId, setHospitalId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function load() {
    api.listDoctors().then(setDoctors).catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load"));
    api.listHospitals().then(setHospitals).catch(() => {});
  }

  useEffect(load, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createDoctor({
        full_name: fullName,
        specialty: specialty || undefined,
        languages: languages ? languages.split(",").map((l) => l.trim()).filter(Boolean) : [],
        hospital_id: hospitalId || undefined,
      });
      setFullName("");
      setSpecialty("");
      setLanguages("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create doctor");
    } finally {
      setSubmitting(false);
    }
  }

  const hospitalName = (id: string | null) => hospitals.find((h) => h.id === id)?.name ?? "Unassigned";

  return (
    <div className="flex flex-col gap-[var(--space-6)]">
      <Card>
        <CardHeader>
          <CardTitle>Add a doctor</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onCreate} className="flex flex-wrap items-end gap-[var(--space-3)]">
            <input required placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <input placeholder="Specialty" value={specialty} onChange={(e) => setSpecialty(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <input placeholder="Languages (comma-separated)" value={languages} onChange={(e) => setLanguages(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]" />
            <select value={hospitalId} onChange={(e) => setHospitalId(e.target.value)} className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] outline-none focus-visible:border-[var(--color-accent)]">
              <option value="">No hospital</option>
              {hospitals.map((h) => (
                <option key={h.id} value={h.id}>{h.name}</option>
              ))}
            </select>
            <Button type="submit" disabled={submitting}>{submitting ? "Adding..." : "Add doctor"}</Button>
          </form>
          {error && <p className="mt-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-emergency)]">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Doctors</CardTitle>
        </CardHeader>
        <CardContent>
          {doctors === null ? (
            <div className="flex flex-col gap-[var(--space-2)]">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : doctors.length === 0 ? (
            <EmptyState title="No doctors yet" description="Add your first doctor above." />
          ) : (
            <ul className="flex flex-col gap-[var(--space-2)]">
              {doctors.map((d) => (
                <li key={d.id} className="flex items-center justify-between rounded-[var(--radius-sm)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)]">
                  <div>
                    <span className="text-[var(--text-sm)] text-[var(--color-fg)]">{d.full_name}</span>
                    {d.specialty && <Badge variant="accent" className="ml-[var(--space-2)]">{d.specialty}</Badge>}
                  </div>
                  <span className="text-[var(--text-xs)] text-[var(--color-fg-muted)]">{hospitalName(d.hospital_id)}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
