"use client";

import React from "react";

export type WorkflowStep = {
  id?: string;
  title?: string;
  description?: string;
  note?: string;
  documents?: string[];
  expected_time?: string;
};

export type WorkflowChartData = {
  id?: string;
  title?: string;
  description?: string;
  steps?: WorkflowStep[];
  image_url?: string;
};

interface WorkflowDiagramProps {
  data: WorkflowChartData;
}

const WorkflowDiagram: React.FC<WorkflowDiagramProps> = ({ data }) => {
  if (!data?.steps || data.steps.length === 0) {
    return null;
  }

  return (
    <div className="mt-8 bg-white border border-slate-200 rounded-3xl shadow-inner p-6">
      <div className="flex flex-col gap-2">
        {data.title && (
          <h2 className="text-3xl font-extrabold text-[#053345]">
            {data.title}
          </h2>
        )}
        {data.description && (
          <p className="text-2xl text-slate-600">{data.description}</p>
        )}
      </div>

      {data.image_url && (
        <div className="mt-6 rounded-3xl overflow-hidden border border-slate-200 shadow">
          <img
            src={data.image_url}
            alt={data.title || "Sơ đồ quy trình"}
            className="w-full object-cover"
          />
        </div>
      )}

      <div className="mt-6 flex flex-col gap-6">
        {data.steps.map((step, index) => {
          const order = index + 1;
          return (
            <div className="flex gap-4" key={step.id || `step-${order}`}>
              <div className="flex flex-col items-center">
                <div className="w-14 h-14 rounded-full bg-[#1A7595] text-white flex items-center justify-center text-2xl font-bold shadow-lg">
                  {order}
                </div>
                {order < data.steps!.length && (
                  <div className="flex-1 w-px bg-slate-300 my-2"></div>
                )}
              </div>

              <div className="flex-1 bg-slate-50 rounded-2xl border border-slate-200 p-5 shadow-sm">
                <div className="flex flex-col gap-2">
                  <p className="text-2xl font-semibold text-slate-900">
                    {step.title || `Bước ${order}`}
                  </p>
                  {step.description && (
                    <p className="text-xl text-slate-600">{step.description}</p>
                  )}
                  {(step.note || step.expected_time) && (
                    <div className="text-lg text-slate-500">
                      {step.expected_time && (
                        <div>
                          <span className="font-semibold">Thời gian dự kiến:</span>
                          <span className="ml-2">{step.expected_time}</span>
                        </div>
                      )}
                      {step.note && (
                        <div>
                          <span className="font-semibold">Lưu ý:</span>
                          <span className="ml-2">{step.note}</span>
                        </div>
                      )}
                    </div>
                  )}
                  {step.documents && step.documents.length > 0 && (
                    <div className="text-lg text-slate-600">
                      <p className="font-semibold">Giấy tờ cần mang:</p>
                      <ul className="list-disc list-inside">
                        {step.documents.map((doc) => (
                          <li key={doc}>{doc}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WorkflowDiagram;
