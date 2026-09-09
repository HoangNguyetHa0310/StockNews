# -*- coding: utf-8 -*-
"""
Module Machine Learning Engine
Huấn luyện mô hình Gradient Boosted Trees (LightGBM / RandomForest)
dự đoán xác suất tăng giá T+3 và T+5 cho thị trường và cổ phiếu VN30.
Áp dụng TimeSeriesSplit (Walk-forward Validation) bảo đảm không rò rỉ dữ liệu tương lai.
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score
from config import MODELS_DIR, ML_CONFIG
from feature_engineering import ML_FEATURE_COLUMNS

# Thử nạp LightGBM, nếu có vấn đề fallback sang HistGradientBoosting / RandomForest
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier


class StockPredictor:
    def __init__(self, model_name: str = "vn30_predictor"):
        self.model_name = model_name
        self.model_path = MODELS_DIR / f"{model_name}.pkl"
        self.model = None
        self.feature_columns = ML_FEATURE_COLUMNS
        self.metrics = {}
        self.feature_importances = {}

    def _create_base_model(self):
        """Khởi tạo mô hình học máy tối ưu cho dữ liệu chuỗi thời gian tài chính."""
        if HAS_LIGHTGBM and ML_CONFIG["model_type"] == "lightgbm":
            return lgb.LGBMClassifier(
                n_estimators=120,
                learning_rate=0.04,
                num_leaves=24,
                max_depth=5,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=ML_CONFIG["random_state"],
                verbose=-1,
                min_child_samples=15
            )
        else:
            return HistGradientBoostingClassifier(
                max_iter=120,
                learning_rate=0.04,
                max_leaf_nodes=24,
                max_depth=5,
                random_state=ML_CONFIG["random_state"],
                min_samples_leaf=15
            )

    def prepare_dataset(self, stock_dfs: dict[str, pd.DataFrame], target_col: str = "target_up_t3") -> pd.DataFrame:
        """
        Gộp dữ liệu từ toàn bộ rổ VN30 để tạo bộ dữ liệu Cross-Sectional mạnh mẽ,
        loại bỏ NaN và các hàng cuối chưa có nhãn tương lai.
        """
        all_rows = []
        for ticker, df in stock_dfs.items():
            if df is None or len(df) < 50:
                continue
            
            # Chọn các cột cần thiết
            cols_to_use = ['time', 'close'] + self.feature_columns + [target_col]
            avail_cols = [c for c in cols_to_use if c in df.columns]
            
            sub = df[avail_cols].copy()
            sub['ticker'] = ticker
            all_rows.append(sub)

        if not all_rows:
            return pd.DataFrame()

        full_df = pd.concat(all_rows, ignore_index=True)
        # Sắp xếp theo thời gian để TimeSeriesSplit chuẩn xác
        full_df['time'] = pd.to_datetime(full_df['time'])
        full_df = full_df.sort_values('time').reset_index(drop=True)
        return full_df

    def train_model(self, stock_dfs: dict[str, pd.DataFrame], target_col: str = "target_up_t3") -> dict:
        """
        Huấn luyện mô hình với Walk-forward Validation (TimeSeriesSplit).
        """
        full_df = self.prepare_dataset(stock_dfs, target_col=target_col)
        if full_df.empty:
            print("  [!] Không có đủ dữ liệu để huấn luyện mô hình ML.")
            return {}

        # Dữ liệu huấn luyện: chỉ lấy những hàng đã có nhãn tương lai (loại bỏ N phiên gần nhất bị NaN)
        labeled_df = full_df.dropna(subset=[target_col] + self.feature_columns).reset_index(drop=True)
        
        X = labeled_df[self.feature_columns]
        y = labeled_df[target_col].astype(int)

        print(f"\n[Machine Learning] Tổng số mẫu huấn luyện gộp (Cross-Sectional): {len(X)} quan sát.")
        print(f"[Machine Learning] Tỷ lệ nhãn TĂNG (Class 1): {y.mean()*100:.1f}%, GIẢM/ĐI NGANG: {(1-y.mean())*100:.1f}%.")

        # Đánh giá bằng TimeSeriesSplit
        n_splits = ML_CONFIG["cv_splits"]
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        auc_scores = []
        acc_scores = []
        prec_scores = []

        for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            fold_model = self._create_base_model()
            fold_model.fit(X_train, y_train)

            val_preds_prob = fold_model.predict_proba(X_val)[:, 1]
            val_preds_binary = (val_preds_prob >= 0.5).astype(int)

            try:
                auc = roc_auc_score(y_val, val_preds_prob)
            except Exception:
                auc = 0.5
            acc = accuracy_score(y_val, val_preds_binary)
            prec = precision_score(y_val, val_preds_binary, zero_division=0)

            auc_scores.append(auc)
            acc_scores.append(acc)
            prec_scores.append(prec)

        mean_auc = np.mean(auc_scores)
        mean_acc = np.mean(acc_scores)
        mean_prec = np.mean(prec_scores)

        print(f"[Walk-Forward CV] ROC-AUC TB: {mean_auc:.3f} | Accuracy TB: {mean_acc:.3f} | Precision TB: {mean_prec:.3f}")

        # Huấn luyện mô hình cuối cùng trên toàn bộ dữ liệu đã có nhãn
        final_model = self._create_base_model()
        final_model.fit(X, y)
        self.model = final_model

        # Tính Feature Importance
        if hasattr(final_model, 'feature_importances_'):
            imps = final_model.feature_importances_
            feat_imp = pd.Series(imps, index=self.feature_columns).sort_values(ascending=False)
            self.feature_importances = feat_imp.to_dict()
            print("[Top 5 Yếu tố quan trọng nhất đối với AI]:")
            for feat, imp in list(feat_imp.items())[:5]:
                print(f"   - {feat}: {imp:.4f}")

        self.metrics = {
            "mean_auc": mean_auc,
            "mean_accuracy": mean_acc,
            "mean_precision": mean_prec,
            "total_samples": len(X)
        }

        # Lưu mô hình vào đĩa
        self.save_model()
        return self.metrics

    def predict_latest(self, ticker: str, df: pd.DataFrame) -> dict:
        """
        Dự đoán xác suất tăng giá cho phiên gần nhất của một mã.
        Trả về dict: { 'prob_up': float, 'prob_down': float, 'confidence': str }
        """
        if self.model is None:
            if not self.load_model():
                return {"prob_up": 0.5, "prob_down": 0.5, "confidence": "Chưa có mô hình"}

        if df is None or df.empty:
            return {"prob_up": 0.5, "prob_down": 0.5, "confidence": "Không có dữ liệu"}

        # Lấy dòng cuối cùng
        last_row = df.iloc[[-1]].copy()
        missing_cols = [c for c in self.feature_columns if c not in last_row.columns]
        for mc in missing_cols:
            last_row[mc] = 0.0

        X_latest = last_row[self.feature_columns].fillna(0)

        try:
            probs = self.model.predict_proba(X_latest)[0]
            prob_up = float(probs[1])
            prob_down = float(probs[0])
        except Exception as e:
            print(f"  [Lỗi dự đoán {ticker}]: {e}")
            prob_up = 0.5
            prob_down = 0.5

        if prob_up >= 0.65:
            conf = "Cao (Tăng mạnh)"
        elif prob_up >= 0.55:
            conf = "Khá (Nghiêng về Tăng)"
        elif prob_up <= 0.35:
            conf = "Cao (Giảm mạnh)"
        elif prob_up <= 0.45:
            conf = "Khá (Nghiêng về Giảm)"
        else:
            conf = "Trung tính / Giằng co"

        return {
            "prob_up": round(prob_up, 4),
            "prob_down": round(prob_down, 4),
            "confidence": conf
        }

    def save_model(self):
        """Lưu model và metadata vào file."""
        data = {
            "model": self.model,
            "metrics": self.metrics,
            "feature_importances": self.feature_importances,
            "feature_columns": self.feature_columns
        }
        joblib.dump(data, self.model_path)
        print(f"[Machine Learning] Đã lưu mô hình vào: {self.model_path}")

    def load_model(self) -> bool:
        """Nạp model đã lưu từ trước."""
        if self.model_path.exists():
            try:
                data = joblib.load(self.model_path)
                self.model = data.get("model")
                self.metrics = data.get("metrics", {})
                self.feature_importances = data.get("feature_importances", {})
                self.feature_columns = data.get("feature_columns", self.feature_columns)
                return True
            except Exception as e:
                print(f"  [Lỗi nạp model]: {e}")
                return False
        return False
