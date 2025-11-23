import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, StackingClassifier, StackingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class SmartCitySystem:
    def __init__(self):
        self.datasets = {}
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.results = {}
        
    def load_datasets(self):
        """Load all datasets"""
        dataset_names = ['accident_risk', 'air_quality', 'citizen_activity', 'smart_parking']
        for name in dataset_names:
            self.datasets[name] = pd.read_csv(f"{name}.csv")
            print(f"{name}.csv loaded: {self.datasets[name].shape}")
            
    def inspect_data(self):
        """Inspect datasets for structure and missing values"""
        for name, df in self.datasets.items():
            print(f"\n=== {name.upper()} DATASET ===")
            print(f"Shape: {df.shape}")
            print(f"Missing values: {df.isnull().sum().sum()}")
            print(f"Target distribution:\n{df.iloc[:, -1].value_counts()}")
            
    def preprocess_data(self):
        """Clean and preprocess all datasets"""
        for name, df in self.datasets.items():
            # Remove duplicates
            df.drop_duplicates(inplace=True)
            
            # Handle missing values
            df.fillna(df.mean(numeric_only=True), inplace=True)
            
            # Encode categorical targets
            if name != 'air_quality':  # AQI is already numeric
                target_col = df.columns[-1]
                if df[target_col].dtype == 'object':
                    le = LabelEncoder()
                    df[target_col] = le.fit_transform(df[target_col])
                    self.encoders[name] = le
                
            self.datasets[name] = df
            
    def prepare_features(self, name):
        """Prepare features for modeling"""
        df = self.datasets[name]
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers[name] = scaler
        
        # Optional PCA (keep 95% variance)
        if X_scaled.shape[1] > 2:
            pca = PCA(n_components=0.95)
            X_pca = pca.fit_transform(X_scaled)
        else:
            X_pca = X_scaled
        
        return train_test_split(X_pca, y, test_size=0.2, random_state=42)
        
    def train_models(self):
        """Train models for each dataset"""
        for name in self.datasets.keys():
            print(f"\nTraining models for {name}...")
            X_train, X_test, y_train, y_test = self.prepare_features(name)
            
            # Choose model type based on task
            if name == 'air_quality':  # Regression
                models = {
                    'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
                    'LinearRegression': LinearRegression(),
                    'SVR': SVR(kernel='rbf')
                }
                
                # Train individual models
                trained_models = {}
                for model_name, model in models.items():
                    model.fit(X_train, y_train)
                    trained_models[model_name] = model
                    
                # Stacking ensemble
                stacking = StackingRegressor(
                    estimators=[('rf', models['RandomForest']), ('lr', models['LinearRegression'])],
                    final_estimator=SVR(),
                    cv=5
                )
                stacking.fit(X_train, y_train)
                trained_models['Stacking'] = stacking
                
                # Evaluate
                results = {}
                for model_name, model in trained_models.items():
                    y_pred = model.predict(X_test)
                    results[model_name] = {
                        'MSE': mean_squared_error(y_test, y_pred),
                        'R2': r2_score(y_test, y_pred)
                    }
                    
            else:  # Classification
                models = {
                    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
                    'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
                    'SVM': SVC(random_state=42, probability=True)
                }
                
                # Train individual models
                trained_models = {}
                for model_name, model in models.items():
                    model.fit(X_train, y_train)
                    trained_models[model_name] = model
                    
                # Stacking ensemble
                stacking = StackingClassifier(
                    estimators=[('rf', models['RandomForest']), ('lr', models['LogisticRegression'])],
                    final_estimator=SVC(probability=True),
                    cv=5
                )
                stacking.fit(X_train, y_train)
                trained_models['Stacking'] = stacking
                
                # Evaluate
                results = {}
                for model_name, model in trained_models.items():
                    y_pred = model.predict(X_test)
                    results[model_name] = {
                        'Accuracy': accuracy_score(y_test, y_pred),
                        'Precision': precision_score(y_test, y_pred, average='weighted'),
                        'Recall': recall_score(y_test, y_pred, average='weighted'),
                        'F1': f1_score(y_test, y_pred, average='weighted')
                    }
                    
            self.models[name] = trained_models
            self.results[name] = results
            
    def visualize_results(self):
        """Visualize model performance"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.ravel()
        
        for idx, (name, results) in enumerate(self.results.items()):
            ax = axes[idx]
            
            if name == 'air_quality':
                # Plot R2 scores for regression
                models = list(results.keys())
                r2_scores = [results[model]['R2'] for model in models]
                bars = ax.bar(models, r2_scores, color=['skyblue', 'lightgreen', 'salmon', 'gold'])
                ax.set_title(f'{name.replace("_", " ").title()} - R² Scores')
                ax.set_ylabel('R² Score')
                ax.set_ylim(0, 1)
                
                # Add value labels on bars
                for bar, score in zip(bars, r2_scores):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{score:.3f}', ha='center', va='bottom')
            else:
                # Plot accuracy for classification
                models = list(results.keys())
                accuracies = [results[model]['Accuracy'] for model in models]
                bars = ax.bar(models, accuracies, color=['skyblue', 'lightgreen', 'salmon', 'gold'])
                ax.set_title(f'{name.replace("_", " ").title()} - Accuracy')
                ax.set_ylabel('Accuracy')
                ax.set_ylim(0, 1)
                
                # Add value labels on bars
                for bar, acc in zip(bars, accuracies):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{acc:.3f}', ha='center', va='bottom')
                           
            ax.tick_params(axis='x', rotation=45)
            
        plt.tight_layout()
        plt.savefig('smart_city_results.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def print_summary(self):
        """Print comprehensive results summary"""
        print("\n" + "="*60)
        print("SMART CITY PREDICTION SYSTEM - RESULTS SUMMARY")
        print("="*60)
        
        for name, results in self.results.items():
            print(f"\n{name.replace('_', ' ').upper()} MODULE:")
            print("-" * 40)
            
            if name == 'air_quality':
                for model, metrics in results.items():
                    print(f"{model:15} | MSE: {metrics['MSE']:.3f} | R²: {metrics['R2']:.3f}")
            else:
                for model, metrics in results.items():
                    print(f"{model:15} | Acc: {metrics['Accuracy']:.3f} | F1: {metrics['F1']:.3f}")
                    
        # Find best models
        print(f"\n{'BEST PERFORMING MODELS':^60}")
        print("-" * 60)
        
        for name, results in self.results.items():
            if name == 'air_quality':
                best_model = max(results.items(), key=lambda x: x[1]['R2'])
                print(f"{name.replace('_', ' ').title():20} | {best_model[0]:15} | R²: {best_model[1]['R2']:.3f}")
            else:
                best_model = max(results.items(), key=lambda x: x[1]['Accuracy'])
                print(f"{name.replace('_', ' ').title():20} | {best_model[0]:15} | Acc: {best_model[1]['Accuracy']:.3f}")

def main():
    # Initialize system
    system = SmartCitySystem()
    
    # Load and inspect data
    system.load_datasets()
    system.inspect_data()
    
    # Preprocess data
    system.preprocess_data()
    
    # Train models
    system.train_models()
    
    # Visualize results
    system.visualize_results()
    
    # Print summary
    system.print_summary()
    
    print(f"\n{'SYSTEM READY FOR URBAN MOBILITY PREDICTIONS':^60}")
    print("="*60)

if __name__ == "__main__":
    main()