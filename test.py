import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import smtplib
from email.message import EmailMessage
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
model = joblib.load('C:\\Users\\Yousef\\Downloads\\GBCModel_new.pkl')
data = pd.read_csv('C:\\Users\\Yousef\\Downloads\\Bank Churn_Data.xls')  # رغم إن اسمه .xls هو CSV
Df = data.copy()
# إعداد الصفحة
st.set_page_config(page_title='Bank churn', page_icon='C:\\Users\\Yousef\\Downloads\\bank churn icon.jpg',
                   layout='wide', initial_sidebar_state='auto')

# بيانات المستخدمين

users = {
    "yousef": {"password": "123", "name": "Yousef Mohamed"},
    "ziad": {"password": "456", "name": "Ziad Abdallah"},
    "radwa": {"password": "789", "name": "Radwa Haggag"}
}

# تسجيل الدخول
def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome {users[username]['name']}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

# دالة إرسال الإشعار
def send_email_notification(customer_name):
    msg = EmailMessage()
    msg['Subject'] ='⚠️ Customer is likely to churn!'
    msg['From'] = st.secrets["email"]["address"]
    msg['To'] = 'bank_churn@gmail.com'
    msg.set_content(f'العميل {customer_name} غادر البنك في {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(st.secrets["email"]["address"], st.secrets["email"]["password"])  # استبدلها بباسوردك
            smtp.send_message(msg)
        print("✅ Done")
    except Exception as e:
        print("❌ error", e)

# محتوى التطبيق
def main_app():
    st.title("📊 Bank Churn Dashboard")
    st.write(f"👋 Welcome, {users[st.session_state['username']]['name']}!")

    

    tab1, tab2 = st.tabs(["prediction", "statistic"])

    with tab1:
        st.title("Customer Information Input")

        # إدخال البيانات
        CustomerId = st.number_input("CustomerId", 0, 1100000000)
        geography = st.selectbox("Geography", ["Spain", "France", "Germany"])
        Gender = st.radio("Gender", ["Female", "Male"])
        CreditScore = st.number_input("CreditScore", 300, 850)
        Age = st.number_input("Age", 18, 100)
        Tenure = st.number_input("Tenure", 0, 70)
        Balance = st.number_input("Balance", 0, 1000000000000000)
        NumOfProducts = st.number_input("NumOfProducts", 0, 10)
        HasCrCard = st.radio("HasCrCard", ["yes", "no"])
        IsActiveMember = st.radio("IsActiveMember", ["yes", "no"])
        EstimatedSalary = st.number_input("EstimatedSalary", 0, 10000000000)

        # تحويل القيم
        label_encoder = LabelEncoder()
        has_crcard_encoded=label_encoder.fit_transform(data['HasCrCard'])
        is_active_member_encoded = label_encoder.fit_transform(data['IsActiveMember'])
        gender_encoded =label_encoder.fit_transform(data['Gender'])
        geography_map = label_encoder.fit_transform(data['Geography'])
        

        def classify_credit_score(score):
            if score <= 579:
                return 'Poor'
            elif 580 <= score <= 669:
                return 'Fair'
            elif 670 <= score <= 739:
                return 'Good'
            elif 740 <= score <= 799:
                return 'Very Good'
            else:
                return 'Excellent'

        def categorize_age(age):
            if 18 <= age <= 25:
                return 'Young'
            elif 26 <= age <= 35:
                return 'Mid Young'
            elif 36 <= age <= 50:
                return 'Middle'
            elif 51 <= age <= 65:
                return 'Senior'
            else:
                return 'Elderly'

        def calculate_features():
            current_year = datetime.now().year
            Year_Joined = current_year - Tenure
            CreditScoreCategory = classify_credit_score(CreditScore)
            age_category = categorize_age(Age)
            ActiveMemberScore = (
                (1 if is_active_member_encoded == 1 else 0) +
                (1 if NumOfProducts > 1 else 0) +
                (1 if 25 <= Age <= 45 else 0)
            )
            Exited = 0
            NonActiveMemberExited = 1 if is_active_member_encoded == 0 and Exited == 1 else 0
            AgeToTenureRatio = Age / (Tenure + 1)
            

            return {
                'Year_Joined': Year_Joined,
                'CreditScoreCategory': CreditScoreCategory,
                'age_category': age_category,
                'ActiveMemberScore': ActiveMemberScore,
                'NonActiveMemberExited': NonActiveMemberExited,
                'AgeToTenureRatio': AgeToTenureRatio,
                
            }

        def process_input_data():
            calculated = calculate_features()
            encoder = LabelEncoder()
            credit_score_category_encoded =  label_encoder.fit_transform(data['CreditScoreCategory'])
            age_category_encoded = label_encoder.fit_transform(data['age_category'])


            data_dict = {
                'CustomerId': [CustomerId],
                'CreditScore': [CreditScore],
                'Geography': [geography_map],
                'Gender': [gender_encoded],
                'Age': [Age],
                'Tenure': [Tenure],
                'Balance': [Balance],
                'NumOfProducts': [NumOfProducts],
                'HasCrCard': [has_crcard_encoded],
                'IsActiveMember': [is_active_member_encoded],
                'EstimatedSalary': [EstimatedSalary],
                'Year_Joined': [calculated['Year_Joined']],
                'CreditScoreCategory': [credit_score_category_encoded],
                'age_category': [age_category_encoded],
                'ActiveMemberScore': [calculated['ActiveMemberScore']],
                'NonActiveMemberExited': [calculated['NonActiveMemberExited']],
                'AgeToTenureRatio': [calculated['AgeToTenureRatio']],
                
            }

            df = pd.DataFrame(data_dict)
            return df, users[st.session_state["username"]]["name"]

        if st.button('Predict'):
            processed_data, customer_name = process_input_data()
            result = model.predict(processed_data)[0]
            result_label = 1 if result == 1 else 0

            st.write("### 📝 Prediction Result:")
            if result == 1:
                st.error('⚠️ Customer is likely to churn!')
                st.markdown("🔔 Try offering special deals or consultation...")
            else:
                st.success("✅ Customer is likely to stay.")

            # حفظ البيانات
            processed_data['Prediction'] = result_label
            processed_data['Date_Predicted'] = datetime.now()

            csv_path = "customer_predictions.csv"
            try:
                old_data = pd.read_csv(csv_path)
                new_data = pd.concat([old_data, processed_data], ignore_index=True)
            except FileNotFoundError:
                new_data = processed_data

            new_data.to_csv(csv_path, index=False)
            st.success("✅ Customer data saved successfully.")

            if result_label == 1:
                send_email_notification(customer_name)

    # تبويب الإحصائيات
    with tab2:
        st.sidebar.header("Bank churn")
        st.sidebar.image("C:\\Users\\Yousef\\Downloads\\bank churn icon.jpg")
        st.sidebar.subheader('Filter')
        

        categorical_filter = st.sidebar.selectbox("categorical filter", [None, "Geography", "ActiveMemberScore", "CreditScoreCategory", "Gender", "IsActiveMember", "Exited", "Year_Joined"])
        row_filter = st.sidebar.selectbox("Row filter", [None, "Geography", "Gender", "IsActiveMember", "Exited"])
        col_filter = st.sidebar.selectbox("colunm filter", [None, "Geography", "Gender", "IsActiveMember", "Exited"])
        numercal_filter = st.sidebar.selectbox("numerical filter", [None, "NumOfProducts", "HasCrCard", "Tenure"])

        st.sidebar.write("Feel free to contact us (yussefmohamed469@gmail.com)")
        st.sidebar.subheader('designed by')
        st.sidebar.markdown('yousef mohamed')
        st.sidebar.markdown('ziad abdallh')
        st.sidebar.markdown('radwa haggag')

        

        c1, c2, c3, c4 = st.columns(4)
        c1.metric('max.balance', Df['Balance'].max())
        c2.metric('avg Age', Df['Age'].mean().round(2))
        c3.metric('sales', Df['NumOfProducts'].sum())
        c4.metric('num of Exited', Df['Exited'].sum())
        Df['Geography']=Df['Geography'].map({0:"Spain", 1:"France", 2:"Germany"})
        Df['Gender']=Df['Gender'].map({1:"Male",0:"Female"})
        
        st.subheader('Balance vs Age')
        fig = px.scatter(Df, x='Balance', y='Age', color=categorical_filter,
                         size=numercal_filter, facet_col=col_filter, facet_row=row_filter)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns((4, 3, 3))
        with c1:
            st.subheader('Gender vs Age')
            fig = px.bar(Df, x='Gender', y='Age', color=categorical_filter)
            st.plotly_chart(fig)
        with c2:
            st.subheader('age_category')
            fig = px.pie(Df, names='age_category', values='NumOfProducts', color=categorical_filter)
            st.plotly_chart(fig)
        with c3:
            st.subheader('Geography vs Age')
            fig = px.pie(Df, names='Geography', values='NumOfProducts', color=categorical_filter, hole=0.4)
            st.plotly_chart(fig)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader('NumOfProducts in age_category by CreditScoreCat ')
            pivot_table = Df.pivot_table(values="NumOfProducts", index='CreditScoreCategory',
                                           columns='age_category', aggfunc='sum')
            st.dataframe(pivot_table)
        with c2:
            st.subheader('Number of person who HasCrCard')
            pivot_table = Df.pivot_table(values="HasCrCard", index='Geography',
                                           columns='Year_Joined', aggfunc='sum')
            st.dataframe(pivot_table)

        st.markdown("---")
        st.subheader("🔒 Logout")
        confirm_logout = st.checkbox("Are you sure you want to logout?")
        logout_btn = st.button("Logout", key="logout_button")

        if logout_btn:
            if confirm_logout:
                st.session_state["logged_in"] = False
                st.rerun()
            else:
                st.warning("Please confirm before logging out.")

# تشغيل التطبيق
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    main_app()