import React from 'react';
import { User, Calendar, Stethoscope, Building, Hash, Award } from 'lucide-react';

const PatientInformationCard = ({ patient }) => {
  if (!patient) return null;

  const infoFields = [
    { label: 'Patient Name', value: patient.patient_name || 'Not Specified', icon: User },
    { label: 'Age / Gender', value: `${patient.age || '—'} · ${patient.gender || '—'}`, icon: User },
    { label: 'Lab / Facility', value: patient.lab_name || 'General Diagnostics', icon: Building },
    { label: 'Referring Doctor', value: patient.doctor_name || 'Self / Direct', icon: Stethoscope },
    { label: 'Report Date', value: patient.report_date || '—', icon: Calendar },
    { label: 'Accession / Sample ID', value: patient.accession_number || '—', icon: Hash },
  ];

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-sky-50 border border-sky-100 flex items-center justify-center">
            <User className="w-5 h-5 text-sky-600" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Patient Demographics &amp; Metadata</h3>
            <p className="text-xs text-slate-500">Header metadata extracted in Phase 4</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold">
          <Award className="w-3.5 h-3.5 text-emerald-600" />
          <span>{(patient.confidence * 100).toFixed(0)}% Confidence</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {infoFields.map((field, idx) => {
          const IconComp = field.icon;
          return (
            <div key={idx} className="bg-slate-50/70 border border-slate-200/80 rounded-xl p-3 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-white text-sky-600 border border-slate-200/80 shrink-0 mt-0.5 shadow-2xs">
                <IconComp className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{field.label}</p>
                <p className="text-xs font-extrabold text-slate-900 truncate mt-0.5" title={field.value}>
                  {field.value}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PatientInformationCard;

