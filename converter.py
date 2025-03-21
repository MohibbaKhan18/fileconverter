import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set up Streamlit app
st.set_page_config(page_title="Data Sweeper", layout='wide')
st.title("DATA SWEEPER")
st.write("Transforms files between CSV and Excel formats with built-in cleaning and visualization!")

uploaded_files = st.file_uploader("Upload your files here:", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file based on extension
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Wrong file provided: {file.name} ({file_ext})")
            continue 

        # Display file details
        file_size = len(file.getvalue()) / 1024  
        st.markdown(f"**File Name:** {file.name}")
        st.markdown(f"**File Size:** {file_size:.2f} KB")

        # Show first 5 rows of DataFrame
        st.write("Preview of the dataframe:")
        st.dataframe(df, height= 800)

        # Data cleaning options
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("Duplicates Removed")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if not numeric_cols.empty:
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("Missing values have been filled")
                    else:
                        st.warning("No numeric columns found to fill missing values.")

        # Choose specific columns to keep or convert
        st.subheader("Select columns to convert")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        
        if columns:  
            df = df[columns]

        # Create some visuals
        st.subheader("Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            df[columns] = df[columns].apply(pd.to_numeric, errors='coerce')
            numeric_df = df.select_dtypes(include='number')
            if not numeric_df.empty:
                st.bar_chart(numeric_df.iloc[:, :min(2, numeric_df.shape[1])])
            else:
                st.warning("No numeric columns available for visualization.")

        # Convert the file into CSV or Excel
        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            file_name = file.name.replace(file_ext, ".csv" if conversion_type == "CSV" else ".xlsx")
            mime_type = "text/csv" if conversion_type == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
            else:
                df.to_excel(buffer, index=False) 
            
            buffer.seek(0)

            # Download Button
            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                mime=mime_type
            )

st.success("All things done!")
