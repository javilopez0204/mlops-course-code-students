from metaflow import FlowSpec, Parameter, step

class TrainingFlow(FlowSpec):
    # Define the parameters for the flow
    max_depth = Parameter('max_depth', default=2, help='Max depth of the random forest classifier')
    n_estimators = Parameter('n_estimators', default=100, help='Number of estimators for the random forest classifier')
    random_state = Parameter('random_state', default=0, help='Random state for the random forest classifier')
    
    @step
    def start(self):
        # Start the flow
        self.next(self.ingest_data)
        
    @step
    def ingest_data(self):
        from sklearn.datasets import load_iris
    
        # Load the iris dataset
        iris = load_iris()
        
        #pylint: disable=no-member
        self.X = iris.data
        self.y = iris.target
        #pylint: enable=no-member
        
        self.next(self.split_data)

    @step
    def split_data(self):
        #Split the data into train and test
        from sklearn.model_selection import train_test_split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2)
        self.next(self.train)

    @step
    def train(self):
        from sklearn.ensemble import RandomForestClassifier
        # Train the model
        self.clf = RandomForestClassifier(max_depth=self.max_depth, n_estimators=self.n_estimators, random_state=self.random_state)
        self.clf.fit(self.X_train, self.y_train)
        self.next(self.show_metrics)

    @step
    def show_metrics(self):
        from sklearn.metrics import classification_report, confusion_matrix
        # Print some metrics
        y_pred = self.clf.predict(self.X_test)
        print(confusion_matrix(self.y_test, y_pred))
        print(classification_report(self.y_test, y_pred))
        self.next(self.register_model)
        
    @step
    def register_model(self):
        # Save the model
        import pickle
        with open('model.pkl', 'wb') as f:
            pickle.dump(self.clf, f)
                 
        self.next(self.end)
        
    @step
    def end(self):
        pass
    
if __name__ == '__main__':
    TrainingFlow()
