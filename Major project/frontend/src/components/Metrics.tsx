import React from "react";
import type { ModelInfo } from "../utils/api";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import { ShieldCheck, TrendingUp, Info } from "lucide-react";

interface MetricsProps {
  modelInfo: ModelInfo | null;
}

export const Metrics: React.FC<MetricsProps> = ({ modelInfo }) => {
  if (!modelInfo) {
    return (
      <div className="glass-panel rounded-3xl p-8 flex flex-col items-center justify-center text-center min-h-[400px]">
        <div className="w-8 h-8 border-2 border-brand-accent/20 border-t-brand-accent rounded-full animate-spin mb-4"></div>
        <span className="text-sm text-slate-400">Loading model diagnostics...</span>
      </div>
    );
  }

  const {
    algorithm,
    training_accuracy: accuracy,
    precision,
    recall,
    f1_score: f1,
    roc_auc: roc,
    confusion_matrix: cm
  } = modelInfo;

  // Global feature importances obtained from GBDT fit
  const importanceData = [
    { name: "last payment amount", importance: 0.8008 },
    { name: "subgrade", importance: 0.0538 },
    { name: "term", importance: 0.0443 },
    { name: "installment", importance: 0.0317 },
    { name: "interest rate", importance: 0.0141 },
    { name: "acc open past 24mths", importance: 0.0129 },
    { name: "oldest revolving line", importance: 0.0038 },
    { name: "funded amount", importance: 0.0034 },
    { name: "loan amount", importance: 0.0034 },
    { name: "log annual income", importance: 0.0033 }
  ];

  return (
    <div className="flex flex-col gap-8 animate-fade-in">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="glass-panel p-4 rounded-2xl text-center">
          <span className="text-3xs font-bold text-slate-400 uppercase tracking-widest">Accuracy</span>
          <p className="text-2xl font-black text-white mt-1">{(accuracy * 100).toFixed(2)}%</p>
        </div>
        <div className="glass-panel p-4 rounded-2xl text-center">
          <span className="text-3xs font-bold text-slate-400 uppercase tracking-widest">Precision</span>
          <p className="text-2xl font-black text-white mt-1">{(precision * 100).toFixed(2)}%</p>
        </div>
        <div className="glass-panel p-4 rounded-2xl text-center">
          <span className="text-3xs font-bold text-slate-400 uppercase tracking-widest">Recall</span>
          <p className="text-2xl font-black text-white mt-1">{(recall * 100).toFixed(2)}%</p>
        </div>
        <div className="glass-panel p-4 rounded-2xl text-center">
          <span className="text-3xs font-bold text-slate-400 uppercase tracking-widest">F1-Score</span>
          <p className="text-2xl font-black text-white mt-1">{(f1 * 100).toFixed(2)}%</p>
        </div>
        <div className="glass-panel p-4 rounded-2xl col-span-2 md:col-span-1 text-center">
          <span className="text-3xs font-bold text-slate-400 uppercase tracking-widest">ROC-AUC</span>
          <p className="text-2xl font-black text-brand-highlight mt-1">{(roc * 100).toFixed(2)}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Confusion Matrix & Model Info */}
        <div className="flex flex-col gap-8">
          {/* Confusion Matrix */}
          <div className="glass-panel rounded-3xl p-6 flex flex-col gap-5">
            <div>
              <h3 className="text-base font-bold text-white">Confusion Matrix (Validation)</h3>
              <p className="text-3xs text-slate-400 mt-1">
                Obtained from evaluating on 4,000 balanced validation records.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-2.5 items-center text-center">
              {/* Labels Row */}
              <div></div>
              <div className="text-2xs font-bold text-slate-400 uppercase tracking-wider">Predicted Fully Paid</div>
              <div className="text-2xs font-bold text-slate-400 uppercase tracking-wider">Predicted Defaulted</div>

              {/* Actual Fully Paid */}
              <div className="text-2xs font-bold text-slate-400 text-left uppercase tracking-wider leading-tight">
                Actual Fully Paid
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-2xl">
                <span className="text-lg font-black text-emerald-400">{cm.true_negatives.toLocaleString()}</span>
                <p className="text-3xs text-emerald-400/70 font-semibold mt-0.5">True Negative (TN)</p>
              </div>
              <div className="bg-slate-900 border border-white/5 p-4 rounded-2xl">
                <span className="text-lg font-black text-slate-400">{cm.false_positives.toLocaleString()}</span>
                <p className="text-3xs text-slate-400/70 font-semibold mt-0.5">False Positive (FP)</p>
              </div>

              {/* Actual Charged Off */}
              <div className="text-2xs font-bold text-slate-400 text-left uppercase tracking-wider leading-tight">
                Actual Defaulted
              </div>
              <div className="bg-slate-900 border border-white/5 p-4 rounded-2xl">
                <span className="text-lg font-black text-slate-400">{cm.false_negatives.toLocaleString()}</span>
                <p className="text-3xs text-slate-400/70 font-semibold mt-0.5">False Negative (FN)</p>
              </div>
              <div className="bg-rose-500/10 border border-rose-500/20 p-4 rounded-2xl">
                <span className="text-lg font-black text-rose-400">{cm.true_positives.toLocaleString()}</span>
                <p className="text-3xs text-rose-400/70 font-semibold mt-0.5">True Positive (TP)</p>
              </div>
            </div>
          </div>

          {/* Model Architecture Info */}
          <div className="glass-panel rounded-3xl p-6 flex flex-col gap-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-brand-accent" />
              Underwriting Model Characteristics
            </h3>
            <div className="flex flex-col gap-2.5 text-xs text-slate-300">
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-slate-400 font-medium">Underwriting Algorithm:</span>
                <strong className="text-white">{algorithm}</strong>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-slate-400 font-medium">Model Objective:</span>
                <strong className="text-white">Binary Classification (Charged Off / Fully Paid)</strong>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-slate-400 font-medium">Input Dimension:</span>
                <strong className="text-white">{modelInfo.num_features} Features</strong>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-slate-400 font-medium">Loss Function:</span>
                <strong className="text-white">Log-Loss (Binary Cross-Entropy)</strong>
              </div>
              <div className="flex justify-between pb-1">
                <span className="text-slate-400 font-medium">Validation Strategy:</span>
                <strong className="text-white">10-Fold Stratified Cross-Validation</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Feature Importance Chart */}
        <div className="glass-panel rounded-3xl p-6 flex flex-col gap-5">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-brand-highlight" />
              Global Feature Importance (Gini split)
            </h3>
            <p className="text-3xs text-slate-400 mt-1">
              Top 10 features ranked by their total contribution to split reduction.
            </p>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={importanceData}
                layout="vertical"
                margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
              >
                <XAxis type="number" stroke="#475569" fontSize={10} />
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
                  itemStyle={{ color: "#4f46e5", fontSize: 10 }}
                />
                <Bar dataKey="importance" fill="#8b5cf6" opacity={0.8} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Global SHAP beeswarm explanation box */}
      <div className="glass-panel rounded-3xl p-6 flex gap-4 items-start">
        <div className="bg-brand-highlight/10 p-2.5 rounded-xl border border-brand-highlight/20 shrink-0">
          <Info className="w-5 h-5 text-brand-highlight" />
        </div>
        <div className="flex flex-col gap-2">
          <h4 className="text-sm font-bold text-white">Global Explainability & SHAP Summary</h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            The global analysis indicates that the <strong>last payment amount (<code>last_pymnt_amnt</code>)</strong> has the single highest impact on risk evaluation. High values are strongly linked to low default probability, reflecting the borrower's immediate capacity to service debt. The borrower's <strong>assigned subgrade</strong> and <strong>loan term</strong> are secondary drivers: 60-month terms and higher grades (D-G) increase log-odds of default, reflecting long-term macro sensitivity.
          </p>
        </div>
      </div>
    </div>
  );
};
