from decouple import config
# APIKEY = config('AIRTABLE_API_KEY')

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

    records = Table(st.secrets['AT_KEY'],base_id,'Fellows x Diagnostic 1.5')
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



big_df = get_data_to_df()

st.sidebar.header("Filter by College and Grad Date here")
college = st.sidebar.multiselect("Select the College:",options=big_df['College/University'].unique(),default=big_df['College/University'].unique())

grad_date = st.sidebar.multiselect("Select the College:",options=big_df['Graduation Date'].unique(),default=big_df['Graduation Date'].unique())

# filt = (big_df['College/University'] == college) & (big_df['Graduation Date'] == grad_date)
new_df = big_df.query("`College/University` == @college & `Graduation Date` == @grad_date")

st.title("A quick Fall 2022 Fellows Diagnostic Dashboard from Omar")

# filt = st.selectbox("Select the College", pd.unique(df_expected['College/University']))
# new_df = df_expected[df_expected['College/University'] == filt]

# filt = st.selectbox("Select the College", pd.unique(df_expected['Graduation Date']))
# new_df = df_expected[df_expected['Graduation Date'] == filt]

# milestone figures

milestone_order = ['Clarity','Alignment','Search Strategy','Interviewing & Advancing']

milestone_chart = new_df['Milestone Link'].value_counts().reset_index().rename(columns={'index':'Milestone Score','Milestone Link':'Number of Fellows'})

milestone_chart['Milestone Score']=pd.Categorical(milestone_chart['Milestone Score'],[x for x in milestone_order if x in milestone_chart['Milestone Score'].unique().tolist()],ordered=True)

# milestone_d = {
#     1: 2,
#     2: 3,
#     3: 1
# }
milestones = milestone_chart.sort_values(by='Milestone Score')
figure_1 = px.bar(milestones,y='Milestone Score',x='Number of Fellows', color='Milestone Score',color_discrete_map={'Clarity':"#00A3E1",'Alignment': "#85C540",'Search Strategy': "#D04D9D",'Interviewing & Advancing': "#FFC507"})

st.markdown("### Milestone Distribution")
st.plotly_chart(figure_1,use_container_width=True)

# industry interest figures

interests = new_df['Industry of Interest'].value_counts().sort_index().reset_index()
figure_2 = px.bar(interests,x='Industry of Interest',y='index',color='index')


st.markdown("### Industry Interest Distribution")
st.plotly_chart(figure_2,use_container_width=True)

# energy style figures

energy = new_df['Energy Style Summary'].value_counts().reset_index().rename(columns={'index':'Energy Label','Energy Style Summary':'Number of Fellows'})

energy_order = ['Strong Introvert','Slight Introvert','Ambivert','Slight Extrovert','Strong Extrovert']

energy['Energy Label']=pd.Categorical(energy['Energy Label'],[x for x in energy_order if x in energy['Energy Label'].unique().tolist()],ordered=True)

energy_df = energy.sort_values(by='Energy Label')

figure_3 = px.bar(energy_df,x='Energy Label',y='Number of Fellows',color='Energy Label')

# predictability figures

predict = new_df['Predictability Preference Summary'].value_counts().reset_index().rename(columns={'index':'Predictability Label','Predictability Preference Summary':'Number of Fellows'})

predict_order = ['Structured','Any Work Environment','Flexible']

predict['Predictability Label'] = pd.Categorical(predict['Predictability Label'],[x for x in predict_order if x in predict['Predictability Label'].unique().tolist()],ordered=True)

predict_df = predict.sort_values(by='Predictability Label')
figure_4 = px.bar(predict_df,x='Predictability Label',y='Number of Fellows',color='Predictability Label')


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

salary = new_df['Salary Expectations Summary'].value_counts().reset_index().sort_index().rename(columns={'index':'Salary Expectation','Salary Expectations Summary':'Number of Fellows'})
salary_order = ['Salary Unsure','40-60K','60-80K','80-100K','100K+']

salary['Salary Expectation'] = pd.Categorical(salary['Salary Expectation'],[x for x in salary_order if x in salary['Salary Expectation'].unique().tolist()],ordered=True)

salary_df = salary.sort_values(by='Salary Expectation')
figure_6 = px.bar(salary_df,x='Salary Expectation',y='Number of Fellows',color='Salary Expectation')

gpa = new_df['A21 GPA Link'].value_counts().reset_index().sort_index().rename(columns={'index':'GPA Range','A21 GPA Link':'Number of Fellows'})
gpa_order = ['Less than 2.00','Between 2.00 and 2.49','Between 2.50 and 2.79', 'Between 2.80 and 2.99','Between 3.00 and 3.49','Between 3.50 and 3.79','3.80 or higher']

gpa['GPA Range'] = pd.Categorical(gpa['GPA Range'],[x for x in gpa_order if x in gpa['GPA Range'].unique().tolist()],ordered=True)

gpa_df = gpa.sort_values(by='GPA Range')
figure_7 = px.bar(gpa_df,x='GPA Range',y='Number of Fellows',color='GPA Range')


cola,colb= st.columns(2)

with cola:
    st.markdown("#### Salary Expectations")
    st.plotly_chart(figure_6,use_container_width=True)
with colb:
    st.markdown("#### GPA Ranges")
    st.plotly_chart(figure_7,use_container_width=True)
