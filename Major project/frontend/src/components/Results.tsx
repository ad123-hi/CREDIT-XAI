import React, { useRef } from "react";
import type { ExplainResponse } from "../utils/api";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip } from "recharts";
import { jsPDF } from "jspdf";
import { Clipboard, Download, ShieldAlert, ShieldCheck, HelpCircle } from "lucide-react";

interface ResultsProps {
  result: ExplainResponse | null;
  inputs: Record<string, any> | null;
}

export const Results: React.FC<ResultsProps> = ({ result, inputs }) => {
  const resultRef = useRef<HTMLDivElement>(null);

  if (!result) {
    return (
      <div className="glass-panel rounded-3xl p-8 flex flex-col items-center justify-center text-center min-h-[500px] border border-dashed border-white/10 relative overflow-hidden">
        {/* Subtle decorative background circles */}
        <div className="absolute -top-10 -left-10 w-40 h-40 bg-brand-accent/5 rounded-full blur-2xl pointer-events-none"></div>
        <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-brand-highlight/5 rounded-full blur-2xl pointer-events-none"></div>

        <div className="bg-slate-900/60 p-5 rounded-full border border-white/5 mb-5 animate-pulse">
          <HelpCircle className="w-10 h-10 text-slate-500" />
        </div>
        <h3 className="text-lg font-bold text-white mb-2">Awaiting Assessment</h3>
        <p className="text-sm text-slate-400 max-w-sm">
          Please complete the applicant profile form and click <strong>Analyze Risk Profile</strong> to run prediction and attribution models.
        </p>
      </div>
    );
  }

  const {
    prediction,
    default_probability: prob,
    confidence,
    risk_category: riskCat,
    processing_time_ms: procTime,
    shap_attributions: attributions,
    explanation,
    timestamp
  } = result;

  // Define colors based on risk levels
  const getRiskStyles = (cat: string) => {
    switch (cat) {
      case "Low Risk":
        return { text: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", glow: "shadow-emerald-500/10" };
      case "Moderate Risk":
        return { text: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", glow: "shadow-amber-500/10" };
      case "High Risk":
        return { text: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/20", glow: "shadow-orange-500/10" };
      case "Very High Risk":
        return { text: "text-rose-400", bg: "bg-rose-500/10", border: "border-rose-500/20", glow: "shadow-rose-500/10" };
      default:
        return { text: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20", glow: "shadow-blue-500/10" };
    }
  };

  const riskStyles = getRiskStyles(riskCat);

  // Recharts data format for SHAP contributions
  const shapData = attributions.slice(0, 10).map((a) => ({
    name: a.feature_label.replace("_", " "),
    value: a.shap_value,
    abs: a.importance,
    effect: a.effect
  }));

  const copyToClipboard = () => {
    const reportText = `
=== Credit Based Loan Default Prediction ===
Timestamp: ${timestamp}
Risk Category: ${riskCat}
Prediction: ${prediction}
Default Probability: ${(prob * 100).toFixed(2)}%
Confidence Score: ${(confidence * 100).toFixed(2)}%
Processing Time: ${procTime} ms

Explanation:
${explanation}
    `.trim();
    
    navigator.clipboard.writeText(reportText);
    alert("Report text copied to clipboard!");
  };

  const generatePdf = () => {
    if (!inputs) return;
    const doc = new jsPDF();

    // Header Background
    doc.setFillColor(15, 23, 42); // slate-900
    doc.rect(0, 0, 210, 40, "F");

    // Title
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.text("Credit Based Loan Default Prediction", 15, 25);
    
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text("Fintech Loan Default Prediction Report", 15, 32);

    // Metadata
    doc.setTextColor(100, 116, 139);
    doc.text(`Generated: ${timestamp}`, 145, 20);
    doc.text("Model Version: v1.0.0", 145, 26);
    doc.text(`Latency: ${procTime} ms`, 145, 32);

    // Section 1: Summary Card
    doc.setFillColor(248, 250, 252); // slate-50
    doc.rect(15, 48, 180, 48, "F");
    doc.setDrawColor(226, 232, 240); // slate-200
    doc.rect(15, 48, 180, 48, "D");

    doc.setTextColor(30, 41, 59);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.text("CREDIT ASSESSMENT SUMMARY", 22, 58);

    doc.setFontSize(10);
    doc.setTextColor(100, 116, 139);
    doc.text("Status Decision:", 22, 68);
    doc.text("Default Probability:", 22, 74);
    doc.text("Confidence Score:", 22, 80);
    doc.text("Risk Classification:", 22, 86);

    // Summary Values
    doc.setFont("helvetica", "bold");
    doc.setTextColor(prediction === "Fully Paid" ? 16 : 225, prediction === "Fully Paid" ? 185 : 29, prediction === "Fully Paid" ? 129 : 72); // Emerald vs Rose
    doc.text(prediction.toUpperCase(), 65, 68);

    doc.setTextColor(30, 41, 59);
    doc.text(`${(prob * 100).toFixed(2)}%`, 65, 74);
    doc.text(`${(confidence * 100).toFixed(2)}%`, 65, 80);

    const riskColor = riskCat === "Low Risk" ? [16, 185, 129] : riskCat === "Moderate Risk" ? [245, 158, 11] : [239, 68, 68];
    doc.setTextColor(riskColor[0], riskColor[1], riskColor[2]);
    doc.text(riskCat.toUpperCase(), 65, 86);

    // Section 2: Applicant Profiles
    doc.setTextColor(15, 23, 42);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.text("SUBMITTED APPLICANT CRITERIA", 15, 110);

    doc.setDrawColor(226, 232, 240);
    doc.line(15, 113, 195, 113);

    // Grid of parameters
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(71, 85, 105);

    const leftCol = [
      `Loan Amount: $${inputs.loan_amnt.toLocaleString()}`,
      `Funded Amount: $${inputs.funded_amnt.toLocaleString()}`,
      `Interest Rate: ${inputs.int_rate}%`,
      `Monthly Installment: $${inputs.installment}`,
      `Loan Term: ${inputs.term} Months`,
      `Sub-Grade Rating: ${inputs.sub_grade}`
    ];

    const middleCol = [
      `Annual Income: $${inputs.annual_inc.toLocaleString()}`,
      `FICO Credit Score: ${inputs.fico_score}`,
      `Debt-to-Income (DTI): ${inputs.dti}%`,
      `Revolving Util: ${inputs.revol_util}%`,
      `Last Payment Amount: $${inputs.last_pymnt_amnt}`,
      `Home Ownership: ${inputs.home_ownership}`
    ];

    const rightCol = [
      `Employment Length: ${inputs.emp_length || "N/A"}`,
      `Purpose Category: ${inputs.purpose.replace("_", " ")}`,
      `Residence State: ${inputs.addr_state}`,
      `Listing Status: ${inputs.initial_list_status.toUpperCase()}`,
      `Application Type: ${inputs.application_type}`,
      `Mortgage Accounts: ${inputs.mort_acc}`
    ];

    let yOffset = 122;
    for (let i = 0; i < 6; i++) {
      doc.text(leftCol[i], 18, yOffset);
      doc.text(middleCol[i], 85, yOffset);
      doc.text(rightCol[i], 145, yOffset);
      yOffset += 7;
    }

    // Section 3: Natural Language Explanation
    doc.setTextColor(15, 23, 42);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.text("EXPLAINABLE AI ATTRIBUTIONS (SHAP)", 15, 175);
    
    doc.setDrawColor(226, 232, 240);
    doc.line(15, 178, 195, 178);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9.5);
    doc.setTextColor(51, 65, 85);
    
    // Auto-wrap text paragraph
    const splitExplanation = doc.splitTextToSize(explanation, 176);
    doc.text(splitExplanation, 15, 186);

    // Section 4: Top Contributing Features
    doc.setTextColor(15, 23, 42);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.text("Top Local Risk Drivers", 15, 220);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(100, 116, 139);

    let driverY = 228;
    // Get top 4 drivers
    attributions.slice(0, 4).forEach((attr, idx) => {
      const effectSign = attr.effect === "increase_risk" ? "(+) Increases Risk" : "(-) Reduces Risk";
      doc.setTextColor(attr.effect === "increase_risk" ? 220 : 16, attr.effect === "increase_risk" ? 38 : 124, attr.effect === "increase_risk" ? 38 : 65);
      doc.text(`${idx + 1}. ${attr.feature_label.replace("_", " ").toUpperCase()}`, 18, driverY);
      doc.setTextColor(71, 85, 105);
      doc.text(`Attribution: ${attr.shap_value.toFixed(4)}`, 85, driverY);
      doc.text(effectSign, 145, driverY);
      driverY += 7;
    });

    // Page footer
    doc.setDrawColor(226, 232, 240);
    doc.line(15, 275, 195, 275);
    doc.setFontSize(8);
    doc.setTextColor(148, 163, 184);
    doc.text("Credit Based Loan Default Prediction is a statistical scoring system. Predictions are for underwriting guidance only.", 15, 282);
    doc.text("Page 1 of 1", 185, 282);

    doc.save(`Credit_Based_Loan_Default_Report_${Date.now()}.pdf`);
  };

  return (
    <div ref={resultRef} className="glass-panel rounded-3xl p-6 flex flex-col gap-6 relative overflow-hidden animate-fade-in">
      {/* Background glow matching the risk */}
      <div className={`absolute top-0 right-0 w-64 h-64 ${riskStyles.bg} rounded-full blur-3xl -z-10 pointer-events-none`}></div>

      {/* Header Info */}
      <div className="flex items-center justify-between border-b border-white/5 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white">Assessment Verdict</h2>
          <span className="text-2xs text-slate-400 font-semibold tracking-wider uppercase">
            Timestamp: {timestamp} • Latency: {procTime}ms
          </span>
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={copyToClipboard}
            title="Copy Report"
            className="p-2 border border-white/10 hover:border-brand-accent/50 hover:bg-slate-900 bg-slate-950/40 text-slate-400 hover:text-white rounded-xl transition-all duration-300"
          >
            <Clipboard className="w-4 h-4" />
          </button>
          
          <button
            onClick={generatePdf}
            title="Download PDF Report"
            className="p-2 border border-white/10 hover:border-brand-accent/50 hover:bg-slate-900 bg-slate-950/40 text-slate-400 hover:text-white rounded-xl transition-all duration-300"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Probability Dial & Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        {/* Left Column: Probability Gauge */}
        <div className="flex flex-col items-center justify-center p-4 bg-slate-950/40 border border-white/5 rounded-2xl">
          <div className="relative flex items-center justify-center w-36 h-36">
            {/* SVG Arc Gauge */}
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="72"
                cy="72"
                r="64"
                strokeWidth="8"
                stroke="rgba(255,255,255,0.03)"
                fill="transparent"
              />
              <circle
                cx="72"
                cy="72"
                r="64"
                strokeWidth="10"
                stroke={`url(#riskGradient-${riskCat.replace(" ", "")})`}
                strokeDasharray={`${2 * Math.PI * 64}`}
                strokeDashoffset={`${2 * Math.PI * 64 * (1 - prob)}`}
                strokeLinecap="round"
                fill="transparent"
              />
              <defs>
                <linearGradient id={`riskGradient-${riskCat.replace(" ", "")}`} x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#4f46e5" />
                  <stop offset="100%" stopColor={riskCat.includes("High") ? "#f43f5e" : "#10b981"} />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute text-center">
              <span className="text-3xl font-extrabold text-white">
                {(prob * 100).toFixed(1)}%
              </span>
              <p className="text-3xs text-slate-400 font-bold uppercase tracking-wider mt-0.5">
                Default Prob
              </p>
            </div>
          </div>
          <span className="text-xs text-slate-400 mt-3 flex items-center gap-1.5">
            Model Confidence: <strong>{(confidence * 100).toFixed(1)}%</strong>
          </span>
        </div>

        {/* Right Column: Status Badges */}
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <span className="text-2xs font-extrabold text-slate-400 uppercase tracking-widest">
              Risk Decision
            </span>
            <div className={`flex items-center gap-3 px-5 py-4 border rounded-2xl ${riskStyles.bg} ${riskStyles.border} ${riskStyles.glow} shadow-lg transition-all duration-300`}>
              {prediction === "Fully Paid" ? (
                <ShieldCheck className="w-8 h-8 text-emerald-400" />
              ) : (
                <ShieldAlert className="w-8 h-8 text-rose-400" />
              )}
              <div>
                <span className={`text-lg font-black tracking-wide ${riskStyles.text}`}>
                  {prediction === "Fully Paid" ? "Approved (Pass)" : "Declined (Fail)"}
                </span>
                <p className="text-xs text-slate-300 mt-0.5 font-medium">
                  Assigned Tiers: <strong>{riskCat}</strong>
                </p>
              </div>
            </div>
          </div>

          {/* Simple Linear Risk Meter */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between text-2xs font-extrabold text-slate-400 uppercase tracking-wider">
              <span>Risk Severity</span>
              <span className={riskStyles.text}>{riskCat}</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-3 border border-white/5 overflow-hidden flex">
              <div className={`h-full bg-emerald-500 transition-all duration-500`} style={{ width: `${Math.min(prob * 100, 20)}%` }} />
              <div className={`h-full bg-amber-500 transition-all duration-500`} style={{ width: `${Math.min(Math.max(prob * 100 - 20, 0), 25)}%` }} />
              <div className={`h-full bg-orange-500 transition-all duration-500`} style={{ width: `${Math.min(Math.max(prob * 100 - 45, 0), 25)}%` }} />
              <div className={`h-full bg-rose-500 transition-all duration-500`} style={{ width: `${Math.max(prob * 100 - 70, 0)}%` }} />
            </div>
            <div className="flex justify-between text-3xs font-extrabold text-slate-500 uppercase tracking-widest px-1">
              <span>Low</span>
              <span>Mod</span>
              <span>High</span>
              <span>Crit</span>
            </div>
          </div>
        </div>
      </div>

      {/* Plain English Explainability */}
      <div className="bg-slate-950/40 border border-white/5 rounded-2xl p-4 leading-relaxed">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
          Plain-English Explanation
        </h4>
        <p className="text-xs text-slate-300 font-medium">
          {explanation}
        </p>
      </div>

      {/* SHAP Feature Contributions Chart */}
      <div className="flex flex-col gap-3">
        <div>
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Local Explainability: Top Feature Contributions
          </h4>
          <p className="text-3xs text-slate-500 mt-1">
            Red bars increase risk of default; green bars reduce risk. Feature values are shown in parentheses.
          </p>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={shapData}
              layout="vertical"
              margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
            >
              <XAxis type="number" stroke="#475569" fontSize={10} domain={['auto', 'auto']} />
              <YAxis
                dataKey="name"
                type="category"
                stroke="#475569"
                fontSize={9}
                width={110}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{ backgroundColor: "#020617", borderColor: "rgba(255,255,255,0.08)", borderRadius: 12 }}
                labelClassName="text-slate-400 text-xs font-bold"
                itemStyle={{ color: "#fff", fontSize: 10 }}
              />
              <Bar dataKey="value">
                {shapData.map((entry, index) => {
                  const barColor = entry.effect === "increase_risk" ? "#f43f5e" : "#10b981";
                  return <Cell key={`cell-${index}`} fill={barColor} opacity={0.8} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
