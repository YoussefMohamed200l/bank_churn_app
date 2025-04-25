import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import smtplib
from email.message import EmailMessage
from datetime import datetime

# تحميل الموديل والبيانات
model = joblib.load('GBCModel_17features.pkl')
data = pd.read_csv('mydata.xls')  # استخدم read_excel

Df = data.copy()

st.set_page_config(page_title='Bank churn', page_icon='C:\\Users\\Yousef\\Downloads\\bank churn icon.jpg',
                   layout='wide', initial_sidebar_state='auto')

users = {
    "yousef@bankchurn.com": {"password": "01153475029", "name": "Yousef Mohamed"},
    "ziad@bankchurn.com": {"password": "456", "name": "Ziad Abdallah"},
    "radwa@bankchurn.com": {"password": "789", "name": "Radwa Haggag"}
}

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

def send_email_notification(CustomerId, username, geography, Age, CreditScore, Balance,
                            NumOfProducts, EstimatedSalary, Tenure, IsActiveMember, HasCrCard):
    msg = EmailMessage()
    msg['Subject'] = '⚠️ Customer is likely to churn!'
    msg['From'] = st.secrets["email"]["address"]
    msg['To'] = 'youssefmohamedarqam@gmail.com'

    recommendations = f'⚠️ Alert!\n\nCustomer with ID {CustomerId} is likely to churn.\n'
    recommendations += f'Predicted by: {username}\n'
    recommendations += f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'

    # إضافة بيانات العميل
    recommendations += f"--- Customer Info ---\n"
    recommendations += f"Geography: {geography}\n"
    recommendations += f"Age: {Age}\n"
    recommendations += f"CreditScore: {CreditScore}\n"
    recommendations += f"Balance: {Balance}\n"
    recommendations += f"NumOfProducts: {NumOfProducts}\n"
    recommendations += f"EstimatedSalary: {EstimatedSalary}\n"
    recommendations += f"Tenure: {Tenure}\n"
    recommendations += f"IsActiveMember: {IsActiveMember}\n"
    recommendations += f"HasCrCard: {HasCrCard}\n\n"

    # حسب الدولة
    if geography == "Germany":
        recommendations += "🇩🇪 Localized Experience for Germany: Launch a regional loyalty program tailored to German customers’ preferences.\n"
    elif geography == "France":
        recommendations += "🇫🇷 Bonjour Bonus! French clients love premium service — offer exclusive concierge features.\n"
    elif geography == "Spain":
        recommendations += "🇪🇸 Viva Offers: Promote family plans or entertainment bundles that resonate with Spanish households.\n"

    # حسب العمر
    if Age < 30:
        recommendations += "🎓 Youth Bundles: Engage them with discounts on digital services, streaming, or student-friendly plans.\n"
    elif Age > 55:
        recommendations += "👴 Senior Care Pack: Highlight simplified plans with dedicated customer service and health-related perks.\n"

    # حسب الكريدت سكور
    if CreditScore < 500:
        recommendations += "🔐 Financial Boost Plan: Introduce credit-building tools or flexible payment options.\n"
    elif CreditScore > 750:
        recommendations += "🌟 Elite Credit Rewards: Target with high-end plans and cashback incentives.\n"

    # حسب الرصيد
    if Balance > 100000:
        recommendations += "💼 Investment Opportunities: Suggest financial advisory services or wealth management perks.\n"
    elif Balance < 1000:
        recommendations += "📉 Supportive Plans: Offer 'no balance' digital accounts or light service bundles.\n"

    # حسب عدد المنتجات
    if NumOfProducts == 1:
        recommendations += "🧩 Bundle Builder: Recommend adding more products with a discount to increase stickiness.\n"
    elif NumOfProducts >= 3:
        recommendations += "🎁 Thank You Pack: They use multiple services — offer a surprise gift or extended features.\n"

    # حسب الراتب المتوقع
    if EstimatedSalary < 3000:
        recommendations += "💸 Affordable Options: Promote low-cost essential plans with flexible billing.\n"
    elif EstimatedSalary > 15000:
        recommendations += "💎 Premium Lifestyle Package: Include luxury add-ons like 24/7 support or priority access.\n"

    # حسب مدة الاشتراك
    if Tenure > 24:
        recommendations += "🎖️ Loyalty Appreciation: They've been with us for over 2 years — time for a personalized 'thank you' reward!\n"
    elif Tenure < 6:
        recommendations += "🌱 Welcome Journey Offer: Boost their early experience with onboarding bonuses.\n"

    # حسب النشاط
    if IsActiveMember == 'no':
        recommendations += "🧠 Reactivation Drive: Invite them to a free trial of premium features or send a call from a retention team.\n"
    else:
        recommendations += "👍 Keep the Momentum: Offer exclusive content or early access to new features.\n"

    # عنده كريدت كارد؟
    if HasCrCard == 'no':
        recommendations += "💳 Smart Card Promo: Introduce your credit card with cashback and no annual fee for the first year.\n"

    msg.set_content(recommendations)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(st.secrets["email"]["address"], st.secrets["email"]["password"])
            smtp.send_message(msg)
        print("✅ Email sent")
    except Exception as e:
        print("❌ Email error", e)


def main_app():
    st.title("📊 Bank Churn Dashboard")
    st.write(f"👋 Welcome, {users[st.session_state['username']]['name']}!")

    tab1, tab2 = st.tabs(["prediction", "statistic"])

    with tab1:
        st.title("Customer Information Input")

        CustomerId = st.number_input("CustomerId", 0, 1100000000)
        geography = st.selectbox("Geography", ["France", "Germany", "Spain"])
        Gender = st.radio("Gender", ["Female", "Male"])
        CreditScore = st.number_input("CreditScore", 300, 850)
        Age = st.number_input("Age", 18, 100)
        Tenure = st.number_input("Tenure", 0, 70)
        Balance = st.number_input("Balance", 0.0, 1e12)
        NumOfProducts = st.number_input("NumOfProducts", 0, 10)
        HasCrCard = st.radio("HasCrCard", ["yes", "no"])
        IsActiveMember = st.radio("IsActiveMember", ["yes", "no"])
        EstimatedSalary = st.number_input("EstimatedSalary", 0.0, 1e10)

        geography_map = {"France": 0, "Germany": 1, "Spain": 2}
        gender_map = {"Female": 0, "Male": 1}
        has_crcard_map = {"no": 0, "yes": 1}
        is_active_member_map = {"no": 0, "yes": 1}
        credit_score_category_map = {'Excellent': 0, 'Fair': 1, 'Good': 2, 'Poor': 3, 'Very Good': 4}
        age_category_map = {'Elderly': 0, 'Mid Young': 1, 'Middle': 2, 'Senior': 3, 'Young': 4}

        geo_encoded = geography_map[geography]
        gender_encoded = gender_map[Gender]
        has_crcard_encoded = has_crcard_map[HasCrCard]
        is_active_member_encoded = is_active_member_map[IsActiveMember]

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
            
            AgeToTenureRatio = Age / (Tenure + 1)

            return {
                'Year_Joined': Year_Joined,
                'CreditScoreCategory': CreditScoreCategory,
                'age_category': age_category,
                'ActiveMemberScore': ActiveMemberScore,
                
                'AgeToTenureRatio': AgeToTenureRatio,
            }
        def process_input_data():
            calculated = calculate_features()
            credit_score_category_encoded = credit_score_category_map[calculated['CreditScoreCategory']]
            age_category_encoded = age_category_map[calculated['age_category']]

            data_dict = {
            'CustomerId': [CustomerId],
            'CreditScore': [CreditScore],
            'Geography': [geo_encoded],
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
            'AgeToTenureRatio': [calculated['AgeToTenureRatio']],
        }

            df = pd.DataFrame(data_dict)
            return df, CustomerId, users[st.session_state["username"]]["name"]


        if st.button('Predict'):
            processed_data, customer_id_input, username = process_input_data()
            result = model.predict(processed_data)[0]
            result_label = 1 if result == 1 else 0

            st.write("### 📝 Prediction Result:")
            if result == 1:
                st.warning('⚠️ Customer is likely to churn!')
                st.markdown("🔔 Try offering special deals or consultation...")
                if geography == "Germany":
                 st.markdown("🇩🇪 **Localized Experience for Germany:** Launch a regional loyalty program tailored to German customers’ preferences.")
                elif geography == "France":
                    st.markdown("🇫🇷 **Bonjour Bonus!** French clients love premium service — offer exclusive concierge features.")
                elif geography == "Spain":
                    st.markdown("🇪🇸 **Viva Offers:** Promote family plans or entertainment bundles that resonate with Spanish households.")

                # 👤 توصيات حسب السن
                if Age < 30:
                    st.markdown("🎓 **Youth Bundles:** Engage them with discounts on digital services, streaming, or student-friendly plans.")
                elif Age > 55:
                    st.markdown("👴 **Senior Care Pack:** Highlight simplified plans with dedicated customer service and health-related perks.")

                # 💳 حسب الكريدت سكور
                if CreditScore < 500:
                    st.markdown("🔐 **Financial Boost Plan:** Introduce credit-building tools or flexible payment options.")
                elif CreditScore > 750:
                    st.markdown("🌟 **Elite Credit Rewards:** Target with high-end plans and cashback incentives.")

                # 💰 حسب الرصيد
                if Balance > 100000:
                    st.markdown("💼 **Investment Opportunities:** Suggest financial advisory services or wealth management perks.")
                elif Balance < 1000:
                    st.markdown("📉 **Supportive Plans:** Offer 'no balance' digital accounts or light service bundles.")

                # 📦 حسب عدد المنتجات
                if NumOfProducts == 1:
                    st.markdown("🧩 **Bundle Builder:** Recommend adding more products with a discount to increase stickiness.")
                elif NumOfProducts >= 3:
                    st.markdown("🎁 **Thank You Pack:** They use multiple services — offer a surprise gift or extended features.")

                # 🧾 حسب الراتب المتوقع
                if EstimatedSalary < 3000:
                    st.markdown("💸 **Affordable Options:** Promote low-cost essential plans with flexible billing.")
                elif EstimatedSalary > 15000:
                    st.markdown("💎 **Premium Lifestyle Package:** Include luxury add-ons like 24/7 support or priority access.")

                # 🕐 حسب مدة الاشتراك
                if Tenure > 24:
                    st.markdown("🎖️ **Loyalty Appreciation:** They've been with us for over 2 years — time for a personalized 'thank you' reward!")
                elif Tenure < 6:
                    st.markdown("🌱 **Welcome Journey Offer:** Boost their early experience with onboarding bonuses.")

                # 🔄 حسب النشاط
                if IsActiveMember == 'no':
                    st.markdown("🧠 **Reactivation Drive:** Invite them to a free trial of premium features or send a call from a retention team.")
                else:
                    st.markdown("👍 **Keep the Momentum:** Offer exclusive content or early access to new features.")

                # 💳 عنده كريدت كارد؟
                if HasCrCard == 'no':
                    st.markdown("💳 **Smart Card Promo:** Introduce your credit card with cashback and no annual fee for the first year.")

                send_email_notification(
                    CustomerId=customer_id_input,
                    username=username,
                    geography=geography,
                    Age=Age,
                    CreditScore=CreditScore,
                    Balance=Balance,
                    NumOfProducts=NumOfProducts,
                    EstimatedSalary=EstimatedSalary,
                    Tenure=Tenure,
                    IsActiveMember=IsActiveMember,
                    HasCrCard=HasCrCard
                )

            else:
                st.success("✅ Customer is likely to stay.")

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

    with tab2:
      # Geography
        geography_rev_map = {0: "France", 1: "Germany", 2: "Spain"}
        # CreditScoreCategory (High/Low Loyalty)
        
        # age_category
        
        # Gender
        gender_rev_map = {0: "Female", 1: "Male"}
        # HasCrCard
      

        # 🔁 تطبيق الديكود على Df قبل أي رسم أو جدول
        Df['Geography'] = Df['Geography'].map(geography_rev_map)
      
        Df['Gender'] = Df['Gender'].map(gender_rev_map)
        
        
        st.sidebar.header("Bank churn")
        st.sidebar.image("C:\\Users\\Yousef\\Downloads\\bank churn icon.jpg")
        st.sidebar.subheader('Filter')

        categorical_filter = st.sidebar.selectbox("categorical filter", [None, "Geography", "CreditScoreCategory", "Gender", "IsActiveMember", "Exited", "Year_Joined"])
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

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    main_app()
