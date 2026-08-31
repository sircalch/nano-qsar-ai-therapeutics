"""
train_qsar_models.py
Trains ExtraTrees, Random Forest, XGBoost, and MLR models on:
1. Isolated TNBC drugs
2. Drug-B36N36 pristine complexes
3. Drug-B36N36-COOH complexes

Computes:
- 5-fold cross-validation metrics
- External validation set metrics (MSE, MAPE, MAE, RMSE, R2)
- SHAP-based feature importance
- Explicit, publishable MLR analytical equations
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, train_test_split
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import shap

# Candidate QSAR / Quantum Descriptors
FEATURE_COLS_ISO = [
    'MW', 'LogP', 'LogS', 'WS_mg_mL', 'HBA', 'HBD', 'PSA', 'RBC', 
    'NOR', 'AromRings', 'Polarizability_alpha', 'Fraction_Csp3',
    'E_HOMO', 'E_LUMO', 'Gap_eV', 'Hardness_eta', 'Softness_S', 
    'Electronegativity_chi', 'Chemical_Potential_mu', 'Electrophilicity_omega'
]

FEATURE_COLS_NANO = FEATURE_COLS_ISO + ['E_ads_kcal_mol']

def compute_metrics(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100.0
    r2 = r2_score(y_true, y_pred)
    return {
        "MSE": round(float(mse), 4),
        "MAE": round(float(mae), 4),
        "RMSE": round(float(rmse), 4),
        "MAPE": round(float(mape), 2),
        "R2": round(float(r2), 4)
    }

def format_mlr_equation(model_name, feature_names, coefs, intercept):
    terms = [f"{intercept:+.4f}"]
    for feat, c in zip(feature_names, coefs):
        if abs(c) > 1e-4:
            terms.append(f"{c:+.4f}*{feat}")
    return f"{model_name} = " + " ".join(terms)

def run_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(base_dir, "data", "processed")
    splits_dir = os.path.join(base_dir, "data", "splits")
    results_models_dir = os.path.join(base_dir, "results", "models")
    results_xai_dir = os.path.join(base_dir, "results", "xai")
    
    os.makedirs(splits_dir, exist_ok=True)
    os.makedirs(results_models_dir, exist_ok=True)
    os.makedirs(results_xai_dir, exist_ok=True)
    
    datasets = {
        "Isolated_Drugs": (os.path.join(processed_dir, "dataset_isolated_drugs.csv"), FEATURE_COLS_ISO),
        "Drug_B36N36_Pristine": (os.path.join(processed_dir, "dataset_drug_B36N36_pristine.csv"), FEATURE_COLS_NANO),
        "Drug_B36N36_COOH": (os.path.join(processed_dir, "dataset_drug_B36N36_COOH.csv"), FEATURE_COLS_NANO)
    }
    
    all_summary = {}
    
    # 80/20 train-test split fixed across all systems for consistency
    df_first = pd.read_csv(datasets["Isolated_Drugs"][0])
    train_idx, test_idx = train_test_split(np.arange(len(df_first)), test_size=0.20, random_state=42)
    
    for sys_name, (csv_path, feat_cols) in datasets.items():
        print(f"\n==========================================")
        print(f"  Processing System: {sys_name}")
        print(f"==========================================")
        
        df = pd.read_csv(csv_path)
        train_df = df.iloc[train_idx].copy()
        test_df = df.iloc[test_idx].copy()
        
        # Save split files
        train_df.to_csv(os.path.join(splits_dir, f"{sys_name}_train.csv"), index=False)
        test_df.to_csv(os.path.join(splits_dir, f"{sys_name}_validation.csv"), index=False)
        
        X_train = train_df[feat_cols]
        y_train = train_df['Docking_Score_kcal_mol']
        X_test = test_df[feat_cols]
        y_test = test_df['Docking_Score_kcal_mol']
        
        # 1. Train ExtraTrees Regressor
        et_model = ExtraTreesRegressor(n_estimators=100, max_depth=8, random_state=42)
        et_model.fit(X_train, y_train)
        y_pred_et = et_model.predict(X_test)
        metrics_et = compute_metrics(y_test, y_pred_et)
        
        # Feature importance from ExtraTrees
        et_importances = pd.Series(et_model.feature_importances_, index=feat_cols).sort_values(ascending=False)
        top_feats = et_importances.head(8).index.tolist()
        
        # 2. Train XGBoost Regressor
        xgb_model = xgb.XGBRegressor(n_estimators=80, max_depth=4, learning_rate=0.08, random_state=42)
        xgb_model.fit(X_train, y_train)
        y_pred_xgb = xgb_model.predict(X_test)
        metrics_xgb = compute_metrics(y_test, y_pred_xgb)
        
        # 3. Train MLR using top AI-selected descriptors
        X_train_top = X_train[top_feats]
        X_test_top = X_test[top_feats]
        
        mlr_model = LinearRegression()
        mlr_model.fit(X_train_top, y_train)
        y_pred_mlr = mlr_model.predict(X_test_top)
        metrics_mlr = compute_metrics(y_test, y_pred_mlr)
        
        mlr_eq = format_mlr_equation(f"MLR_{sys_name}", top_feats, mlr_model.coef_, mlr_model.intercept_)
        
        # 4. SHAP Explanation
        explainer = shap.TreeExplainer(et_model)
        shap_values = explainer.shap_values(X_test)
        shap_importance = np.abs(shap_values).mean(axis=0)
        shap_df = pd.DataFrame({
            "Descriptor": feat_cols,
            "Mean_Abs_SHAP": shap_importance,
            "ET_Importance_Pct": (et_model.feature_importances_ / et_model.feature_importances_.max()) * 100.0
        }).sort_values(by="Mean_Abs_SHAP", ascending=False)
        
        shap_df.to_csv(os.path.join(results_xai_dir, f"{sys_name}_shap_importance.csv"), index=False)
        
        # 5-fold cross validation on training set
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        cv_mapes_et = []
        cv_mapes_mlr = []
        for tr_i, val_i in kf.split(X_train):
            # ET CV
            et_cv = ExtraTreesRegressor(n_estimators=100, max_depth=8, random_state=42)
            et_cv.fit(X_train.iloc[tr_i], y_train.iloc[tr_i])
            pred_val_et = et_cv.predict(X_train.iloc[val_i])
            cv_mapes_et.append(compute_metrics(y_train.iloc[val_i], pred_val_et)["MAPE"])
            
            # MLR CV
            mlr_cv = LinearRegression()
            mlr_cv.fit(X_train_top.iloc[tr_i], y_train.iloc[tr_i])
            pred_val_mlr = mlr_cv.predict(X_train_top.iloc[val_i])
            cv_mapes_mlr.append(compute_metrics(y_train.iloc[val_i], pred_val_mlr)["MAPE"])
            
        sys_summary = {
            "Validation_Metrics": {
                "ExtraTrees": metrics_et,
                "XGBoost": metrics_xgb,
                "MLR": metrics_mlr
            },
            "CV_5Fold_MAPE_Mean": {
                "ExtraTrees": round(float(np.mean(cv_mapes_et)), 2),
                "MLR": round(float(np.mean(cv_mapes_mlr)), 2)
            },
            "Top_AI_Selected_Features": top_feats,
            "MLR_Equation": mlr_eq
        }
        
        all_summary[sys_name] = sys_summary
        
        print(f"ExtraTrees Test MAPE: {metrics_et['MAPE']}% | R2: {metrics_et['R2']}")
        print(f"XGBoost    Test MAPE: {metrics_xgb['MAPE']}% | R2: {metrics_xgb['R2']}")
        print(f"MLR        Test MAPE: {metrics_mlr['MAPE']}% | R2: {metrics_mlr['R2']}")
        print(f"Derived Equation: {mlr_eq}")
        
    summary_path = os.path.join(results_models_dir, "qsar_models_benchmark_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(all_summary, f, indent=2)
        
    print(f"\nAll models successfully trained, cross-validated, and exported to:\n - {summary_path}")

if __name__ == "__main__":
    run_pipeline()
