import React from "react";
import { ShieldCheck, Database, Radio, ServerCrash } from "lucide-react";

interface HeaderProps {
  activeTab: "dashboard" | "metrics";
  setActiveTab: (tab: "dashboard" | "metrics") => void;
  apiStatus: "online" | "offline" | "checking";
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, apiStatus }) => {
  return (
    <header className="glass-panel sticky top-0 z-50 px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4 border-b border-white/10 mb-8">
      {/* Title / Brand */}
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-tr from-brand-accent to-brand-highlight p-2.5 rounded-xl shadow-lg shadow-brand-accent/25">
          <ShieldCheck className="w-8 h-8 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-white via-blue-100 to-indigo-300 bg-clip-text text-transparent">
            Credit Based Loan Default Prediction
          </h1>
          <p className="text-xs text-slate-400 font-medium tracking-wide uppercase">
            Fintech loan default prediction dashboard
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex bg-slate-950/60 p-1.5 rounded-xl border border-white/5">
        <button
          onClick={() => setActiveTab("dashboard")}
          className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-semibold transition-all duration-300 ${
            activeTab === "dashboard"
              ? "bg-brand-accent text-white shadow-lg shadow-brand-accent/20"
              : "text-slate-400 hover:text-white hover:bg-white/5"
          }`}
        >
          <ShieldCheck className="w-4.5 h-4.5" />
          Risk Assessment
        </button>
        <button
          onClick={() => setActiveTab("metrics")}
          className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-semibold transition-all duration-300 ${
            activeTab === "metrics"
              ? "bg-brand-accent text-white shadow-lg shadow-brand-accent/20"
              : "text-slate-400 hover:text-white hover:bg-white/5"
          }`}
        >
          <Database className="w-4.5 h-4.5" />
          Model Diagnostics
        </button>
      </div>

      {/* Health Status Indicator */}
      <div className="flex items-center gap-3 bg-slate-900/40 px-4 py-2 rounded-xl border border-white/5">
        <div className="relative flex h-3 w-3">
          {apiStatus === "online" ? (
            <>
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </>
          ) : apiStatus === "checking" ? (
            <>
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
            </>
          ) : (
            <>
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
            </>
          )}
        </div>
        <span className="text-xs font-bold tracking-wide uppercase flex items-center gap-1.5">
          {apiStatus === "online" ? (
            <>
              <Radio className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">API Active</span>
            </>
          ) : apiStatus === "checking" ? (
            <>
              <Radio className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
              <span className="text-amber-400">Connecting</span>
            </>
          ) : (
            <>
              <ServerCrash className="w-3.5 h-3.5 text-rose-400" />
              <span className="text-rose-400">API Offline</span>
            </>
          )}
        </span>
      </div>
    </header>
  );
};
