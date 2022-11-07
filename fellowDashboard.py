from decouple import config
APIKEY = config('AIRTABLE_API_KEY')

from pyairtable import Table
import pandas as pd
import plotly.express as px
import streamlit as st

# setting streamlit page configurations
st.set_page_config(
    page_title="Omar's Fall 2022 Fellowship Diagnostic Dashboard",
    page_icon="✅",
    layout="wide",
)

# defining function to remove list
# useful for transforming data later
def delist(x):
    return x[0]



# defining the whole operation to request and clean data from airtable into a workable dataframe

@st.experimental_memo(max_entries=2)
def get_data_to_df():
    # base ID for Diag for interfaces
    base_id = 'app1MKM5YW5GC6rww'

    # list of the fields I want to get out
    # this is important for reducing the size of the data request
    desired_fields = [
        'Name',
        'Milestone Link',
        'Industry of Interest',
        'A4',
        'Energy Style Score',
        'Energy Style Summary',
        'Predictability Score',
        'Predictability Preference Summary',
        'Salary Expectations Summary',
        'A26 Experience Link',
        'A21 GPA Link',
        'User Profile',
        'Graduation Date',
        'College/University'
        ]

    records = Table(APIKEY,base_id,'Fellows x Diagnostic 1.5')
    data = records.all(view='OMN StreamlitView', fields=desired_fields)

    # flattening the dataframe
    df = pd.DataFrame.from_records(data)
    df_expected = pd.concat([df, df['fields'].apply(pd.Series)], axis = 1).drop(['fields','createdTime'], axis = 1)

    # cleaning all the lookup fields from [x] to x
    df_expected['A21 GPA Link']=df_expected['A21 GPA Link'].map(lambda x: delist(x),na_action='ignore')
    df_expected['Milestone Link']=df_expected['Milestone Link'].map(lambda x: delist(x),na_action='ignore')
    df_expected['A4']=df_expected['A4'].map(lambda x: delist(x),na_action='ignore')
    df_expected['Industry of Interest']=df_expected['Industry of Interest'].map(lambda x: delist(x),na_action='ignore')
    df_expected['User Profile']=df_expected['User Profile'].map(lambda x: delist(x),na_action='ignore')
    df_expected['College/University']=df_expected['College/University'].map(lambda x: delist(x),na_action='ignore')
    df_expected['Graduation Date']=df_expected['Graduation Date'].map(lambda x: delist(x),na_action='ignore')
    
    return df_expected

new_df = get_data_to_df()


st.title("A quick Fall 2022 Fellows Diagnostic Dashboard from Omar")

# filt = st.selectbox("Select the College", pd.unique(df_expected['College/University']))
# new_df = df_expected[df_expected['College/University'] == filt]

# filt = st.selectbox("Select the College", pd.unique(df_expected['Graduation Date']))
# new_df = df_expected[df_expected['Graduation Date'] == filt]


# milestone figures

milestone_chart = new_df['Milestone Link'].value_counts().reset_index()
milestone_d = {
    1: 2,
    2: 3,
    3: 1
}
milestones = milestone_chart.rename(milestone_d).sort_index()
figure_1 = px.bar(milestones,y='index',x='Milestone Link', color='index',color_discrete_map={'Clarity':"#00A3E1",'Alignment': "#85C540",'Search Strategy': "#D04D9D",'Interviewing & Advancing': "#FFC507"})

st.markdown("### Milestone Distribution")
st.plotly_chart(figure_1,use_container_width=True)

# industry interest figures

interests = new_df['Industry of Interest'].value_counts().sort_index().reset_index()
figure_2 = px.bar(interests,x='Industry of Interest',y='index',color='index')


st.markdown("### Industry Interest Distribution")
st.plotly_chart(figure_2,use_container_width=True)

# energy style figures

energy = new_df['Energy Style Summary'].value_counts().reset_index()
energy_d = {
    0: 1,
    1: 2,
    2: 0,
}

energy_df = energy.rename(energy_d).sort_index()
figure_3 = px.bar(energy_df,x='index',y='Energy Style Summary',color='index')

# predictability figures

predict = new_df['Predictability Preference Summary'].value_counts().reset_index()
predict_d = {
    0:1,
    1:0
}
predict_df = predict.rename(predict_d).sort_index()
figure_4 = px.bar(predict_df,x='index',y='Predictability Preference Summary',color='index')


# putting energy and predictability figures into columns
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Energy Style Summary")
    st.plotly_chart(figure_3,use_container_width=True)

with col2:
    st.markdown("#### Predictability Preference Summary")
    st.plotly_chart(figure_4,use_container_width=True)


# User profile figures
profiles = new_df['User Profile'].value_counts().reset_index().sort_index()
figure_5 = px.bar(profiles,x='index',y='User Profile',color='index')
st.plotly_chart(figure_5,use_container_width=True)

salary = new_df['Salary Expectations Summary'].value_counts().reset_index().sort_index()
salary_d = {
    0:2,
    1:3,
    2:0,
    3:1
}
salary_df = salary.rename(salary_d).sort_index()
figure_6 = px.bar(salary_df,x='index',y='Salary Expectations Summary',color='index')

gpa = new_df['A21 GPA Link'].value_counts().reset_index().sort_index()
gpa_d ={
    6:0,
    5:1,
    4:2,
    3:3,
    0:4,
    1:5,
    2:6
}
gpa_df = gpa.rename(gpa_d).sort_index()
figure_7 = px.bar(gpa_df,x='index',y='A21 GPA Link',color='index')


cola,colb= st.columns(2)

with cola:
    st.markdown("#### Salary Expectations")
    st.plotly_chart(figure_6,use_container_width=True)
with colb:
    st.markdown("#### GPA Ranges")
    st.plotly_chart(figure_7,use_container_width=True)
