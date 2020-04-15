import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    :param messages_filepath: filepath to the messages.csv file
    :param categories_filepath: filepath to the categories.csv file
    :return:
    """
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = pd.merge(messages,categories)
    return df

def clean_data(df):
    """
    :param df: input dataframe which needs to be cleaned
    :return: cleaned df
    """
    categories = df['categories'].str.split(";",expand=True)
    row = categories.iloc[0]
    row = row.apply(lambda x: x[:-2])
    category_colnames = row
    categories.columns = category_colnames
    for column in categories:

        # set each value to be the last character of the string
        categories[column] = categories[column].str.slice().str[-1]

        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
    df = df.drop(['categories'],axis=1)
    df = pd.concat([df,categories],axis=1)
    # related column has 2 as an entry
    df = df[df['related'] != 2]
    #remove duplicates
    df = df.drop_duplicates()
    return df


def save_data(df, database_filename):
    """
    :param df: input Dataframe which will get written to database
    :param database_filename: the name of the database
    :return: . print statement indicating succesfull saving
    """
    engine = create_engine('sqlite:///'+database_filename)
    df.to_sql('datatable', engine, index=False)
    print('success')  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()