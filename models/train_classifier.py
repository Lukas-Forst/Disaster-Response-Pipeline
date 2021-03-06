import sys
from sqlalchemy import create_engine
import sqlite3
import re
import numpy as np
import pandas as pd
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download(['punkt', 'wordnet','stopwords', 'averaged_perceptron_tagger'])
from nltk.corpus import stopwords
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.datasets import make_multilabel_classification
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

def load_data(database_filepath):
    """
    :param database_filepath: string of path to database
    :return: dataframe of the database,
    - X -> column of messages
    - Y -> all columns with the 36 categories for prediction
    """
    engine = create_engine('sqlite:///{}'.format(database_filepath))

    df = pd.read_sql_table('datatable', engine)
    X= df['message']
    Y= df.iloc[:, 4:]


    return X, Y, df




def tokenize(text):
    """
    :param text: input is uncleaned text
    :return: cleaned text
    """
    text = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words("english")
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return tokens


    
def build_model():
    """
    call to build_model will create a pipeline for predictionn
    :return: Gridsearchmodel
    """
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
          ('tfidf', TfidfTransformer()),
         ('clf', MultiOutputClassifier(AdaBoostClassifier()))
    ])
    parameters = parameters = {
        'vect__ngram_range': ((1, 1), (1, 2)),
        
        'vect__max_features': (None, 5000),
        
        'clf__estimator__n_estimators':  [50,100],
    
        
    }

    cv = GridSearchCV(pipeline, param_grid=parameters,  n_jobs=-1,verbose=2)
    return cv
    


def evaluate_model(model, X_test, Y_test, category_names):
    """
    :param model: model we want to evaluate
    :param X_test: test column with messages used for evaluation
    :param Y_test: column with classes wanted to predict
    :param category_names: name of categories
    :return: print statement with 36 classes
    """
    modpred = model.predict(X_test)
    for row,col in enumerate(Y_test):
        
        target = str(Y_test[col].unique())
        target = re.sub(r"[\[\]']", "",target).replace(" ", "")
    
        print(classification_report(Y_test[col],modpred[ : , row],target_names=target))


def save_model(model, model_filepath):
    """
    save model as pickle file
    :param model: input of model wanted to save as pickle
    :param model_filepath: path were we want to save the pickle file
    :return:
    """
    with open(model_filepath, 'wb') as file:
        pickle.dump(model, file)
    


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()