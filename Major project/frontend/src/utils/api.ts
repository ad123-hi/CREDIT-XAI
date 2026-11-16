export interface FeatureMeta {
  name: string;
  datatype: string;
  group: string;
  description: string;
  tooltip: string;
  required: boolean;
  example: number | string;
  min?: number;
  max?: number;
  allowed_values?: (string | number)[];
  default: number | string;
}

export interface FeaturesResponse {
  [key: string]: FeatureMeta;
}

export interface ModelInfo {
  model_name: string;
  algorithm: string;
  training_accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  version: string;
  num_features: number;
  feature_names: string[];
  confusion_matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
  };
}

export interface ShapContribution {
  feature: string;
  feature_label: string;
  value: number;
  shap_value: number;
  importance: number;
  effect: "increase_risk" | "decrease_risk";
}

export interface ExplainResponse {
  prediction: string;
  prediction_code: number;
  default_probability: number;
  confidence: number;
  risk_category: "Low Risk" | "Moderate Risk" | "High Risk" | "Very High Risk";
  processing_time_ms: number;
  shap_attributions: ShapContribution[];
  explanation: string;
  timestamp: string;
}
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchFeatures(): Promise<FeaturesResponse> {
  const response = await fetch(`${API_BASE_URL}/features`);
  if (!response.ok) {
    throw new Error(`Failed to fetch features: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchModelInfo(): Promise<ModelInfo> {
  const response = await fetch(`${API_BASE_URL}/model-info`);
  if (!response.ok) {
    throw new Error(`Failed to fetch model info: ${response.statusText}`);
  }
  return response.json();
}

export async function checkApiHealth(): Promise<{ status: string; model_loaded: boolean; version: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    if (!response.ok) {
      return { status: "offline", model_loaded: false, version: "0.0.0" };
    }
    return response.json();
  } catch (error) {
    return { status: "offline", model_loaded: false, version: "0.0.0" };
  }
}

export async function explainPrediction(inputs: Record<string, any>): Promise<ExplainResponse> {
  const response = await fetch(`${API_BASE_URL}/explain`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(inputs),
  });
  if (!response.ok) {
    const errorDetails = await response.json().catch(() => ({}));
    throw new Error(errorDetails.detail || `Prediction failed: ${response.statusText}`);
  }
  return response.json();
}

// Pre-defined Example Applicants matching different risk profiles
export const EXAMPLE_APPLICANTS = [
  {
    name: "John Doe (Low Risk Refinance)",
    description: "High credit score, low DTI, high payment amount, substantial income.",
    inputs: {
      loan_amnt: 10000,
      funded_amnt: 10000,
      term: 36,
      int_rate: 7.5,
      installment: 311.11,
      grade: "A",
      sub_grade: "A3",
      home_ownership: "MORTGAGE",
      annual_inc: 120000,
      verification_status: "Verified",
      purpose: "credit_card",
      addr_state: "CA",
      dti: 10.5,
      earliest_cr_line: 2000,
      revol_util: 20.5,
      last_pymnt_amnt: 5000,
      application_type: "Individual",
      acc_open_past_24mths: 1,
      avg_cur_bal: 180000,
      bc_open_to_buy: 25000,
      bc_util: 15.2,
      mo_sin_old_rev_tl_op: 240,
      mo_sin_rcnt_rev_tl_op: 18,
      mort_acc: 3,
      num_actv_rev_tl: 2,
      initial_list_status: "w",
      fico_score: 780,
      emp_length: "10+ years"
    }
  },
  {
    name: "Ayesha Patel (Very Low Risk Home Loan)",
    description: "Excellent credit, stable income, low loan amount and very low DTI.",
    inputs: {
      loan_amnt: 6000,
      funded_amnt: 6000,
      term: 36,
      int_rate: 5.9,
      installment: 183.46,
      grade: "A",
      sub_grade: "A1",
      home_ownership: "MORTGAGE",
      annual_inc: 185000,
      verification_status: "Verified",
      purpose: "home_improvement",
      addr_state: "CA",
      dti: 7.0,
      earliest_cr_line: 1999,
      revol_util: 9.5,
      last_pymnt_amnt: 6000,
      application_type: "Individual",
      acc_open_past_24mths: 6,
      avg_cur_bal: 210000,
      bc_open_to_buy: 45000,
      bc_util: 8.2,
      mo_sin_old_rev_tl_op: 300,
      mo_sin_rcnt_rev_tl_op: 12,
      mort_acc: 4,
      num_actv_rev_tl: 3,
      initial_list_status: "w",
      fico_score: 820,
      emp_length: "10+ years"
    }
  },
  {
    name: "Sarah Jenkins (Moderate Risk Consolidation)",
    description: "Good income, average credit score, moderate debt-to-income ratio.",
    inputs: {
      loan_amnt: 15000,
      funded_amnt: 15000,
      term: 36,
      int_rate: 13.99,
      installment: 512.63,
      grade: "C",
      sub_grade: "C4",
      home_ownership: "RENT",
      annual_inc: 65000,
      verification_status: "Source Verified",
      purpose: "debt_consolidation",
      addr_state: "TX",
      dti: 19.8,
      earliest_cr_line: 2008,
      revol_util: 55.4,
      last_pymnt_amnt: 512.63,
      application_type: "Individual",
      acc_open_past_24mths: 4,
      avg_cur_bal: 24000,
      bc_open_to_buy: 8500,
      bc_util: 52.3,
      mo_sin_old_rev_tl_op: 140,
      mo_sin_rcnt_rev_tl_op: 6,
      mort_acc: 0,
      num_actv_rev_tl: 5,
      initial_list_status: "w",
      fico_score: 695,
      emp_length: "5 years"
    }
  },
  {
    name: "Marcus Vance (High Risk Small Business)",
    description: "High debt-to-income, high interest rate, low FICO score, low payment.",
    inputs: {
      loan_amnt: 25000,
      funded_amnt: 25000,
      term: 60,
      int_rate: 22.99,
      installment: 704.12,
      grade: "E",
      sub_grade: "E5",
      home_ownership: "RENT",
      annual_inc: 45000,
      verification_status: "Verified",
      purpose: "small_business",
      addr_state: "FL",
      dti: 32.5,
      earliest_cr_line: 2012,
      revol_util: 88.2,
      last_pymnt_amnt: 704.12,
      application_type: "Individual",
      acc_open_past_24mths: 7,
      avg_cur_bal: 12000,
      bc_open_to_buy: 1200,
      bc_util: 91.5,
      mo_sin_old_rev_tl_op: 80,
      mo_sin_rcnt_rev_tl_op: 2,
      mort_acc: 0,
      num_actv_rev_tl: 8,
      initial_list_status: "f",
      fico_score: 620,
      emp_length: "1 year"
    }
  }
];
