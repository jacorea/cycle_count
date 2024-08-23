import streamlit as st
import pandas as pd
from datetime import datetime

def process_data(uploaded_file, column_names, new_column_names):
    """
    Reads CSV file, selects specific columns, renames them, and returns a DataFrame.

    Args:
        uploaded_file: The uploaded CSV file.
        column_names: A list of column indices.
        new_column_names: A list of new column names.

    Returns:
        A Pandas DataFrame with the processed data and renamed columns.
    """

    df = pd.read_csv(uploaded_file, header=None)
    df = df[column_names]
    df.columns = new_column_names

    # Separate customer id and customer name into their own columns
    df[['cus_id', 'cus_name']] = df['cusid_name'].str.split('-', expand=True)
    df['cus_id'] = df['cus_id'].str.split(':').str[1]

    # Remove Product Description label
    df['product_description'] = df['product_description'].str.split(': ').str[-1]

    # Separate unit_location to zone - aisle - rack - level
    df[['zone', 'aisle', 'rack', 'level']] = df['unit_location'].str.split('*', expand=True)

    # Drop unwanted columns
    drop_columns = ['cusid_name', 'unit_location','num_of_containers','loose_pieces', 'container_type']
    df.drop(columns=drop_columns, inplace=True)

    #Reorder
    column_order = ['cus_id', 'cus_name', 'product_id','product_description', 'unit_id','zone','aisle','rack','level','on_hand','marked','available']
    df = df[column_order]

     # Sort the DataFrame
    df = df.sort_values(by=['product_id', 'zone', 'aisle', 'rack', 'level'])

    return df

def process_for_report(df):
# Processing logic for report
# For example:
    df_report = df.copy().reset_index(drop=True)
# Add specific calculations or transformations for report
    return df_report

def process_for_warehouse(df):
    # Processing logic for warehouse
    # For example:
    df_warehouse = df.copy()
    df_warehouse.drop(columns=['unit_id'], inplace=True)
    # Add specific calculations or transformations for warehouse
    return df_warehouse

def main():
    st.title("CSV Processor")

    uploaded_file = st.file_uploader("Upload your CSV file")
    if uploaded_file is not None:
        columns_to_keep = [14, 17, 18, 21, 22, 23, 24, 25, 26, 27, 28]
        new_column_names = ['cusid_name', 'product_id', 'product_description', 'unit_id', 'unit_location', 'container_type',
                           'num_of_containers', 'loose_pieces', 'on_hand', 'marked', 'available']

        df = process_data(uploaded_file, columns_to_keep, new_column_names)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Process for Report"):
                df_report = process_for_report(df)
                st.write("Report Data:")
                st.dataframe(df_report.head())
        with col2:
            if st.button("Process for Warehouse"):
                df_warehouse = process_for_warehouse(df)
                st.write("Warehouse Data:")
                st.dataframe(df_warehouse.head())
                
                today = datetime.now().strftime("%Y%m%d")
                file_name = f"warehouse_processed_{today}.csv"
                st.download_button(
                    label="Download Warehouse Data",
                    data=df_warehouse.to_csv(index=False),
                    file_name=file_name,
                    mime='text/csv'
                )

        st.write(df)

if __name__ == '__main__':
    main()