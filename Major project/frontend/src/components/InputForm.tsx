import React, { useState } from "react";
import { EXAMPLE_APPLICANTS } from "../utils/api";
import type { FeatureMeta, FeaturesResponse } from "../utils/api";
import { User, DollarSign, CreditCard, RotateCcw, Play, HelpCircle, FileText } from "lucide-react";

interface InputFormProps {
  features: FeaturesResponse;
  onSubmit: (formData: Record<string, any>) => void;
  isLoading: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({ features, onSubmit, isLoading }) => {
  // Local state for the inputs
  const [inputs, setInputs] = useState<Record<string, any>>(() => {
    const initial: Record<string, any> = {};
    Object.entries(features).forEach(([key, meta]) => {
      initial[key] = meta.default;
    });
    return initial;
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<"applicant" | "loan" | "credit">("applicant");
  const [hoveredFeature, setHoveredFeature] = useState<string | null>(null);

  const handleInputChange = (name: string, value: any, meta: FeatureMeta) => {
    let parsedValue = value;
    
    // Type conversion
    if (meta.datatype === "float") {
      parsedValue = value === "" ? "" : parseFloat(value);
    } else if (meta.datatype === "int") {
      parsedValue = value === "" ? "" : parseInt(value, 10);
    }

    setInputs((prev) => ({ ...prev, [name]: parsedValue }));

    // Real-time Range Validation
    let errorMsg = "";
    if (parsedValue !== "") {
      if (meta.min !== undefined && parsedValue < meta.min) {
        errorMsg = `Minimum value is ${meta.min}`;
      } else if (meta.max !== undefined && parsedValue > meta.max) {
        errorMsg = `Maximum value is ${meta.max}`;
      }
    } else if (meta.required) {
      errorMsg = "This field is required";
    }

    setErrors((prev) => ({ ...prev, [name]: errorMsg }));
  };

  const handleAutofill = (index: number) => {
    const example = EXAMPLE_APPLICANTS[index].inputs;
    setInputs({ ...example });
    setErrors({});
  };

  const handleReset = () => {
    const initial: Record<string, any> = {};
    Object.entries(features).forEach(([key, meta]) => {
      initial[key] = meta.default;
    });
    setInputs(initial);
    setErrors({});
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Final Validation Check
    const newErrors: Record<string, string> = {};
    Object.entries(features).forEach(([key, meta]) => {
      const val = inputs[key];
      if (val === undefined || val === "") {
        if (meta.required) newErrors[key] = "This field is required";
      } else {
        if (meta.min !== undefined && val < meta.min) {
          newErrors[key] = `Must be at least ${meta.min}`;
        }
        if (meta.max !== undefined && val > meta.max) {
          newErrors[key] = `Must not exceed ${meta.max}`;
        }
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      // Determine which tab has the first error to guide user
      const errorKeys = Object.keys(newErrors);
      for (const key of errorKeys) {
        const group = features[key]?.group;
        if (group === "Applicant Information") {
          setActiveTab("applicant");
          break;
        } else if (group === "Loan Information") {
          setActiveTab("loan");
          break;
        } else if (group === "Credit Profile") {
          setActiveTab("credit");
          break;
        }
      }
      return;
    }

    onSubmit(inputs);
  };

  // Group features by metadata group
  const groupedFeatures = {
    applicant: Object.entries(features).filter(([_, m]) => m.group === "Applicant Information"),
    loan: Object.entries(features).filter(([_, m]) => m.group === "Loan Information"),
    credit: Object.entries(features).filter(([_, m]) => m.group === "Credit Profile"),
  };

  const renderField = (name: string, meta: FeatureMeta) => {
    const value = inputs[name] ?? "";
    const hasError = !!errors[name];

    // Determine custom controls based on data types and metadata
    if (meta.allowed_values) {
      return (
        <select
          id={name}
          value={value}
          onChange={(e) => handleInputChange(name, e.target.value, meta)}
          className={`w-full bg-slate-900/60 border rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-accent transition-all duration-300 ${
            hasError ? "border-rose-500/50" : "border-white/10"
          }`}
        >
          {meta.allowed_values.map((val) => (
            <option key={val} value={val} className="bg-slate-950">
              {val}
            </option>
          ))}
        </select>
      );
    }

    // FICO score and select continuous properties can use numeric inputs + sliders
    const isSliderEnabled = ["fico_score", "dti", "int_rate", "revol_util"].includes(name);

    return (
      <div className="flex flex-col gap-2">
        <input
          id={name}
          type="number"
          step={meta.datatype === "float" ? "0.01" : "1"}
          value={value}
          onChange={(e) => handleInputChange(name, e.target.value, meta)}
          className={`w-full bg-slate-900/60 border rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-accent transition-all duration-300 ${
            hasError ? "border-rose-500/50 focus:ring-rose-500/40" : "border-white/10"
          }`}
          placeholder={String(meta.default)}
        />
        {isSliderEnabled && meta.min !== undefined && meta.max !== undefined && (
          <input
            type="range"
            min={meta.min}
            max={meta.max}
            step={meta.datatype === "float" ? "0.1" : "1"}
            value={value || meta.default}
            onChange={(e) => handleInputChange(name, e.target.value, meta)}
            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-accent"
          />
        )}
      </div>
    );
  };

  return (
    <div className="glass-panel rounded-3xl p-6 flex flex-col gap-6 relative overflow-hidden">
      {/* Background radial highlight */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-brand-accent/5 rounded-full blur-3xl -z-10 pointer-events-none"></div>

      {/* Title */}
      <div>
        <h2 className="text-xl font-bold flex items-center gap-2 text-white">
          <FileText className="w-5 h-5 text-brand-highlight" />
          Applicant Profiler
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Specify core criteria or load one of our preset risk profiles.
        </p>
      </div>

      {/* Quick Autofill Presets */}
      <div className="flex flex-col gap-2.5">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Risk Presets
        </span>
        <div className="grid grid-cols-3 gap-2">
          {EXAMPLE_APPLICANTS.map((preset, idx) => (
            <button
              key={preset.name}
              type="button"
              onClick={() => handleAutofill(idx)}
              className="text-2xs font-semibold px-3 py-2 border border-white/5 bg-slate-950/40 hover:bg-brand-accent/15 hover:border-brand-accent/30 text-slate-300 hover:text-white rounded-xl transition-all duration-300 text-left line-clamp-1 truncate"
              title={preset.description}
            >
              {preset.name.split(" ")[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Internal Navigation Tabs */}
      <div className="flex border-b border-white/5 text-sm">
        <button
          type="button"
          onClick={() => setActiveTab("applicant")}
          className={`flex-1 py-3 text-center border-b-2 font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
            activeTab === "applicant"
              ? "border-brand-accent text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <User className="w-4 h-4" />
          Applicant
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("loan")}
          className={`flex-1 py-3 text-center border-b-2 font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
            activeTab === "loan"
              ? "border-brand-accent text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <DollarSign className="w-4 h-4" />
          Loan Details
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("credit")}
          className={`flex-1 py-3 text-center border-b-2 font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
            activeTab === "credit"
              ? "border-brand-accent text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <CreditCard className="w-4 h-4" />
          Credit History
        </button>
      </div>

      {/* Form Content */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[460px] overflow-y-auto pr-1">
          {groupedFeatures[activeTab].map(([key, meta]) => {
            const hasError = !!errors[key];
            const isHovered = hoveredFeature === key;

            return (
              <div
                key={key}
                className="flex flex-col gap-1.5 relative"
                onMouseEnter={() => setHoveredFeature(key)}
                onMouseLeave={() => setHoveredFeature(null)}
              >
                <div className="flex items-center justify-between">
                  <label htmlFor={key} className="text-xs font-bold text-slate-300 tracking-wide flex items-center gap-1.5 cursor-pointer">
                    {meta.name.replace("_", " ")}
                    {meta.required && <span className="text-rose-500">*</span>}
                  </label>
                  <div className="relative group">
                    <HelpCircle className="w-3.5 h-3.5 text-slate-500 hover:text-slate-300 cursor-help transition-colors" />
                    {isHovered && (
                      <div className="absolute right-0 bottom-full mb-2 w-56 p-3 bg-slate-950 border border-white/10 rounded-xl shadow-2xl text-2xs leading-relaxed text-slate-300 z-50 pointer-events-none">
                        {meta.tooltip}
                      </div>
                    )}
                  </div>
                </div>

                {renderField(key, meta)}

                {hasError && (
                  <span className="text-2xs font-semibold text-rose-400 mt-0.5">
                    {errors[key]}
                  </span>
                )}
              </div>
            );
          })}
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3 mt-4">
          <button
            type="button"
            onClick={handleReset}
            className="flex items-center justify-center gap-2 px-5 py-3 border border-white/10 bg-slate-900/40 hover:bg-slate-800 text-slate-300 hover:text-white rounded-2xl font-bold text-sm transition-all duration-300"
          >
            <RotateCcw className="w-4.5 h-4.5" />
            Reset
          </button>
          
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-brand-accent to-brand-highlight hover:shadow-lg hover:shadow-brand-accent/25 disabled:opacity-50 text-white rounded-2xl font-bold text-sm transition-all duration-300"
          >
            {isLoading ? (
              <>
                <div className="w-4.5 h-4.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                Analyzing Profile...
              </>
            ) : (
              <>
                <Play className="w-4.5 h-4.5 fill-current" />
                Analyze Risk Profile
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
