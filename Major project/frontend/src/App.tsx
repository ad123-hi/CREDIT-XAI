import { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { InputForm } from "./components/InputForm";
import { Results } from "./components/Results";
import { Metrics } from "./components/Metrics";
import { 
  fetchFeatures, 
  fetchModelInfo, 
  checkApiHealth, 
  explainPrediction 
} from "./utils/api";
import type { 
  FeaturesResponse, 
  ModelInfo, 
  ExplainResponse 
} from "./utils/api";
import { ShieldAlert, AlertCircle, RefreshCw } from "lucide-react";

function App() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "metrics">("dashboard");
  const [apiStatus, setApiStatus] = useState<"online" | "offline" | "checking">("checking");
  const [features, setFeatures] = useState<FeaturesResponse | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [predictionResult, setPredictionResult] = useState<ExplainResponse | null>(null);
  const [submittedInputs, setSubmittedInputs] = useState<Record<string, any> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const initData = async () => {
    setApiStatus("checking");
    setErrorMsg(null);
    try {
      const health = await checkApiHealth();
      if (health.model_loaded) {
        setApiStatus("online");
        const feats = await fetchFeatures();
        setFeatures(feats);
        const info = await fetchModelInfo();
        setModelInfo(info);
      } else {
        setApiStatus("offline");
        setErrorMsg("API is active but machine learning model fails to initialize.");
      }
    } catch (error) {
      setApiStatus("offline");
      setErrorMsg("Failed to connect to the backend server. Make sure FastAPI is running on http://localhost:8000.");
    }
  };

  useEffect(() => {
    initData();
  }, []);

  const handlePredictSubmit = async (formData: Record<string, any>) => {
    setIsLoading(true);
    setErrorMsg(null);
    setSubmittedInputs(formData);
    try {
      const res = await explainPrediction(formData);
      setPredictionResult(res);
    } catch (err: any) {
      setErrorMsg(err.message || "An unexpected error occurred during analysis.");
      setPredictionResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
      {/* Header */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} apiStatus={apiStatus} />

      {/* Main Error Banner */}
      {errorMsg && (
        <div className="mx-6 mb-6 p-4 bg-rose-500/10 border border-rose-500/25 rounded-2xl flex items-center justify-between gap-3 text-rose-400 text-sm font-semibold animate-shake">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button
            onClick={initData}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 hover:text-white text-xs font-bold rounded-xl transition-all duration-300"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Connection
          </button>
        </div>
      )}

      {/* Tab Switch Router */}
      <main className="flex-1 px-6">
        {apiStatus === "offline" && !features ? (
          /* Offline Fallback State */
          <div className="glass-panel rounded-3xl p-12 flex flex-col items-center justify-center text-center max-w-xl mx-auto my-12">
            <div className="bg-rose-500/10 p-5 rounded-full border border-rose-500/20 mb-6">
              <ShieldAlert className="w-12 h-12 text-rose-400" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Connection Required</h2>
            <p className="text-sm text-slate-400 leading-relaxed mb-6">
              Credit Based Loan Default Prediction requires the FastAPI backend to load feature metadata and model checkpoints. Please start the server and click retry.
            </p>
            <button
              onClick={initData}
              className="flex items-center gap-2 px-6 py-3 bg-brand-accent hover:bg-indigo-700 text-white rounded-2xl font-bold text-sm shadow-lg shadow-brand-accent/20 transition-all duration-300"
            >
              <RefreshCw className="w-4 h-4 animate-spin-slow" />
              Reconnect to Server
            </button>
          </div>
        ) : !features ? (
          /* Loading Skeletons */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            <div className="glass-panel rounded-3xl p-6 h-96 animate-pulse bg-slate-900/10 border border-white/5"></div>
            <div className="glass-panel rounded-3xl p-6 h-96 animate-pulse bg-slate-900/10 border border-white/5"></div>
          </div>
        ) : activeTab === "dashboard" ? (
          /* Assessment View */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            <InputForm 
              features={features} 
              onSubmit={handlePredictSubmit} 
              isLoading={isLoading} 
            />
            <Results 
              result={predictionResult} 
              inputs={submittedInputs} 
            />
          </div>
        ) : (
          /* Diagnostics View */
          <Metrics modelInfo={modelInfo} />
        )}
      </main>
    </div>
  );
}

export default App;
