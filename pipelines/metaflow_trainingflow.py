from metaflow import FlowSpec, Parameter, card, current, step
from metaflow.cards import Image, Markdown, Table


class TrainingFlow(FlowSpec):

    max_depth    = Parameter('max_depth',    default=2,   help='Max depth of the random forest')
    n_estimators = Parameter('n_estimators', default=100, help='Number of trees')
    random_state = Parameter('random_state', default=0,   help='Random seed')

    @card
    @step
    def start(self):
        print(f"max_depth={self.max_depth}  n_estimators={self.n_estimators}")
        self.next(self.ingest_data)

    @card
    @step
    def ingest_data(self):
        from sklearn.datasets import load_iris
        iris = load_iris()
        self.X             = iris.data
        self.y             = iris.target
        self.feature_names = list(iris.feature_names)
        self.target_names  = list(iris.target_names)
        print(f"Loaded {len(self.X)} samples, {self.X.shape[1]} features")
        self.next(self.split_data)

    @card
    @step
    def split_data(self):
        from sklearn.model_selection import train_test_split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=self.random_state
        )
        print(f"Train: {len(self.X_train)}  Test: {len(self.X_test)}")
        self.next(self.train)

    @card
    @step
    def train(self):
        from sklearn.ensemble import RandomForestClassifier
        self.clf = RandomForestClassifier(
            max_depth=self.max_depth,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
        )
        self.clf.fit(self.X_train, self.y_train)
        self.next(self.show_metrics)

    @card
    @step
    def show_metrics(self):
        import matplotlib.pyplot as plt
        from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay

        y_pred        = self.clf.predict(self.X_test)
        self.accuracy = accuracy_score(self.y_test, y_pred)
        report        = classification_report(
            self.y_test, y_pred, target_names=self.target_names, output_dict=True
        )

        current.card.append(Markdown(f"# Results — accuracy: {self.accuracy:.4f}"))

        rows = [
            [cls, f"{v['precision']:.3f}", f"{v['recall']:.3f}", f"{v['f1-score']:.3f}"]
            for cls, v in report.items() if cls in self.target_names
        ]
        current.card.append(Markdown("## Classification report"))
        current.card.append(Table([["Class", "Precision", "Recall", "F1"]] + rows))

        fig, ax = plt.subplots()
        ConfusionMatrixDisplay.from_predictions(
            self.y_test, y_pred, display_labels=self.target_names, ax=ax
        )
        current.card.append(Markdown("## Confusion matrix"))
        current.card.append(Image.from_matplotlib(fig))
        plt.close(fig)

        self.next(self.register_model)

    @card
    @step
    def register_model(self):
        import pickle
        with open('model.pkl', 'wb') as f:
            pickle.dump(self.clf, f)
        print("Model saved → model.pkl")
        self.next(self.end)

    @card
    @step
    def end(self):
        print(f"Done. Accuracy: {self.accuracy:.4f}")


if __name__ == '__main__':
    TrainingFlow()
