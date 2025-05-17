import pandas as pd
import joblib
import numpy as np

df=pd.read_csv('samples.csv')

print(df)

df= df.drop(columns=df.columns[0],axis=1)
print(df)
X = df.drop('loss', axis=1)  # Features (all numerical columns)
y = df['loss'] 

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

from sklearn.metrics import accuracy_score, classification_report

y_pred = clf.predict(X)
print("Accuracy:", accuracy_score(y, y_pred))
print(classification_report(y, y_pred))

X_temp=X[y==1]

print(X_temp)

print(np.array(X_temp.iloc[0]).reshape(1,-1))

print("prob ",clf.predict_proba(np.array(X_temp.iloc[0]).reshape(1,-1))[0][1])
print(clf.predict(X_temp))


joblib.dump(clf, "trained_random_forest.joblib")
