import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Data Cleaning", layout="wide", page_icon="🧹")
                    


# ------------------- HEADER -------------------
st.markdown(
    "<h1 style='text-align:center; margin-bottom:5px;'>🧹 Data Cleaning App</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:gray;'>Upload → Inspect → Clean → Download</p>",
    unsafe_allow_html=True
)

st.write("---")

# ---------------- SIDEBAR ----------------------
st.sidebar.header("📂 Upload Your File")
uploaded_file = st.sidebar.file_uploader(
    "Choose CSV, Excel, or JSON",
    type=["csv", "xlsx", "xls", "json"]
)

st.sidebar.write("👆 File must be one of the supported formats.")

# ---------------- MAIN PAGE MESSAGE -------------
if uploaded_file is None:
    st.markdown(
        """
        <div style='text-align:center; padding:40px; color:#555;'>
            <h3>⬅ Please upload a dataset from the sidebar</h3>
            <p>The cleaning tools will appear here once you upload a file.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def load_data(file):
    filename = file.name.lower()  # get file name

    if filename.endswith(".csv"):
        df = pd.read_csv(file)

    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file)

    elif filename.endswith(".json"):
        df = pd.read_json(file)

    else:
        st.error("❌ Unsupported File Format. Please upload again")
        return None
    
    return df

if uploaded_file:
    df = load_data(uploaded_file)

    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:15px;
            margin-top:10px;
            background-color:#002455;
            color:white;
            border-radius:10px;
            font-size:20px;">
            📁 <b>{uploaded_file.name}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

     #---- Column Type Detection ----
    numeric_columns = df.select_dtypes(include=['int', 'float']).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=['int', 'float']).columns.tolist()


    if df is None:
        st.stop()

    if "df" not in st.session_state:
        st.session_state.df = df

    # -------- Dataset Preview --------
    st.subheader("📊 Dataset Preview")
    preview_rows = st.number_input(
        "How many rows do you want to preview?",
        min_value=1,
        max_value=len(df),
        value=5,
        step=1
    )
    st.dataframe(df.head(preview_rows))

    #SIMPLE DATASET SUMMARY
    st.subheader("📊 Dataset Summary")

    # Count missing values and duplicates
    total_missing = df.isnull().sum().sum()
    duplicate_count = df.duplicated().sum()

    # Build simple readable messages
    missing_msg = "No missing values" if total_missing == 0 else f"{total_missing} missing values found"
    dup_msg = "No duplicate rows" if duplicate_count == 0 else f"{duplicate_count} duplicate rows found"

    # Display summary
    st.write("**Missing Values:**", missing_msg)
    st.write("**Duplicate Values:**", dup_msg)

    # CLEAN DATASET DETECTION
    is_clean_dataset = (total_missing == 0) and (duplicate_count ==0)

    if is_clean_dataset:
        st.success("🎉 Your dataset is already clean! No missing values or duplicate rows found.")
        st.stop()
        
    # Dataset has duplicates but no missing values
    if total_missing == 0 and duplicate_count > 0:
        st.warning("⚠ No missing values found - but duplicate rows detected")

    # -------- Missing Values Check --------
    #st.subheader("🔍 Missing Values Check")
    #missing_table = df.isnull().sum().reset_index()
    #missing_table.columns = ["Column", "Missing Values"]
    #st.dataframe(missing_table)

    # ---- Column Type Detection ----
    #numeric_columns = df.select_dtypes(include=['int', 'float']).columns.tolist()
    #categorical_columns = df.select_dtypes(exclude=['int', 'float']).columns.tolist()

    #st.markdown("### 📘 Column Type Summary")
    #st.markdown(
    #    f"""
    #    <div style="padding:15px; border-radius:10px; background-color:#002455; color:white;">
    #         <b>🔢 Numerical Columns:</b> {numeric_columns}<br>
    #         <b>🔠 Categorical Columns:</b> {categorical_columns}
    #    </div>
    #    """,
    #    unsafe_allow_html=True
    #)

    # -------- Handle Numerical Missing Values --------
    st.subheader("🔢 Handle Numerical Missing Values")

    num_method = st.selectbox(
        "Choose a method for numerical missing values:",
        [
            "Fill with Mean",
            "Fill with Median",
            "Interpolate",
            "Forward Fill",
            "Backward Fill",
            "Fill with Custom Number",
            "Fill with Custom Text",
            "Remove rows containing ANY missing value"
            ]
            )
    if num_method == "Fill with Custom Number":
        custom_num = st.number_input(
            "Enter the number to fill missing values:",
            value=0.00,
            format="%.2f"
        )

    if num_method == "Fill with Custom Text":
        custom_text = st.text_input(
            "Enter text to fill missing values:",
            value="Unknown"
        )
        st.warning("⚠ Not recommended for Machine Learning or numeric analysis.")

    if st.button("Apply Numerical Handling"):
        cleaned_df = st.session_state.df.copy()

        if num_method == "Fill with Mean":
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(
                cleaned_df[numeric_columns].mean()
                )

        elif num_method == "Fill with Median":
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(
                cleaned_df[numeric_columns].median()
                )

        elif num_method == "Interpolate":
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].interpolate()

        elif num_method == "Forward Fill":
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(method="ffill")

        elif num_method == "Backward Fill":
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(method="bfill")

        elif num_method == "Fill with Custom Number":
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(custom_num)

        elif num_method == "Fill with Custom Text":
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(custom_text)

        elif num_method == "Remove rows containing ANY missing value":
            cleaned_df = cleaned_df.dropna()

        # Round numeric columns to 2 decimal places
        if num_method != "Fill with Custom Text":
            cleaned_df = cleaned_df.round(2)

        st.session_state.df = cleaned_df
        st.success("Numerical missing values handled!")


    # -------- Handle Categorical Missing Values --------
    st.subheader("🔠 Handle Categorical Missing Values")

    cat_method = st.selectbox(
        "Choose a method for categorical missing values:",
        [
            "Fill with Mode",
            "Fill with Custom Text"
            ]
            )

    if cat_method == "Fill with Custom Text":
        custom_word = st.text_input("Enter custom text:", "Unknown")

    if st.button("Apply Categorical Handling"):
        cleaned_df = st.session_state.df.copy()

        if cat_method == "Fill with Mode":
            cleaned_df[categorical_columns] = cleaned_df[categorical_columns].fillna(
                cleaned_df[categorical_columns].mode().iloc[0]
                )

        elif cat_method == "Fill with Custom Text":
            cleaned_df[categorical_columns] = cleaned_df[categorical_columns].fillna(custom_word)

        st.session_state.df = cleaned_df
        st.success("Categorical missing values handled!")


# -------- Cleaned Data Preview --------
    if "df" in st.session_state and st.session_state.df is not None:
        st.subheader("📄 Cleaned Data Preview")

        cleaned_df = st.session_state.df

        preview_clean_rows = st.number_input(
            "How many cleaned rows do you want to preview?",
            min_value=1,
            max_value=len(cleaned_df),
            value=5,
            step=1
            )

        st.dataframe(cleaned_df.head(preview_clean_rows))



     # -------- Duplicate Summary --------
    st.subheader("🧩 Duplicate Records Check")

     # Count duplicates
    duplicate_count = st.session_state.df.duplicated().sum()

     # Show UI message
    st.markdown(
        f"""
        <div style="padding:15px; border-radius:10px; background-color:#002455; color:white;">
            <b>🔁 Total Duplicate Rows:</b> {duplicate_count}
        </div>
        """,
        unsafe_allow_html=True
        )

    if duplicate_count > 0:

        st.subheader("Preview Duplicate Rows")

        preview_dup = st.number_input(
            "How many duplicate rows do you want to preview?",
            min_value=1,
            max_value=duplicate_count,
            value=min(5,duplicate_count),
            step=1
        )

        duplicate_rows = st.session_state.df[
            st.session_state.df.duplicated(keep=False)
            ]
        
        st.dataframe(duplicate_rows.head(preview_dup))

    else:
        st.success("🎉No duplicate rows found! Your dataset is clean")


    st.subheader("🧹 Remove Duplicate Rows")

    if st.button("Remove All Duplicates"):
        cleaned_df = st.session_state.df.copy()
        cleaned_df = cleaned_df.drop_duplicates(keep="first")
        st.session_state.df = cleaned_df
        st.success("All duplicate rows have been removed!")

    # DUPLICATE REMOVAL : BY SELECTED COLUMNS

    st.subheader("🧠 Remove Duplicates by Selected Columns")

    selected_cols = st.multiselect(
        "Select columns to check duplicates against:",
        st.session_state.df.columns
    )

    if st.button("🧽Remove Duplicates Based on Selected Columns"):
        if len(selected_cols) == 0:
            st.warning("Please select at least one column")

        else:
            cleaned_df = st.session_state.df.copy()
            cleaned_df = cleaned_df.drop_duplicates(subset=selected_cols, keep="first")
            st.session_state.df = cleaned_df
            st.success(f"Duplicates removal based on: {selected_cols}")

    # CHANGE COLUMN DATA TYPE
    st.subheader("🔧 Change Column Data Type")
    df = st.session_state.df
    col_to_convert = st.selectbox(
        "Select a column to change its data type:",
        df.columns
    )
    new_dtype = st.selectbox(
        "Convert selected column to:",
        ["string", "integer", "float", "datetime"]
    )

    if st.button("Apply Data Type Conversion"):
        cleaned_df = df.copy()

        try:
            if new_dtype == "string":
                cleaned_df[col_to_convert] = cleaned_df[col_to_convert].astype(str)

            elif new_dtype == "integer":
                cleaned_df[col_to_convert] = pd.to_numeric(
                    cleaned_df[col_to_convert], errors='coerce'
                ).astype("Int64")

            elif new_dtype == "float":
                cleaned_df[col_to_convert] = pd.to_numeric(
                    cleaned_df[col_to_convert], errors='coerce'
                )

            st.session_state.df = cleaned_df
            st.success(f"Column '{col_to_convert}' successfully converted to {new_dtype}!")
    
        except Exception as e:
            st.error(f"Conversion failed: {e}")

    # DOWNLOAD CLEANED DATASET

    st.subheader("📥 Download Cleaned Dataset")

    cleaned_df = st.session_state.df

    # CSV DOWNLOAD
    csv_data = cleaned_df.to_csv(index=False).encode("utf-8")
    
    # EXCEL DOWNLOAD
    excel_buffer = io.BytesIO()
    cleaned_df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0) #rewinds the buffer to the start so it can be read from the beginning when download

    # JSON DOWNLOAD
    json_data = cleaned_df.to_json(orient="records",indent=4)
    
    # BUTTON IN ONE ROW
    col1, col2, col3 = st.columns(3)

    col1.download_button(
        label="⬇ Download CSV",
        data=csv_data,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )

    col2.download_button(
        label="⬇ Download Excel",
        data=excel_buffer,
        file_name="cleaned_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    col3.download_button(
        label="⬇ Download JSON",
        data=json_data,
        file_name="cleaned_data.json",
        mime="application/json"
    )

    st.stop()

