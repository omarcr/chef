import streamlit as st 

# st.set_page_config(
#     page_title="Hello",
#     page_icon="👋",
# )

# pg = st.navigation([st.Page(), st.Page("pages/2_urop_projects.py")])
# pg.run()

me_page = st.Page("pages/1_about_me.py", title="About Me", icon=":material/person:")
class_page = st.Page("pages/2_class_projects.py", title="Class Projects", icon=":material/school:")
urop_page = st.Page("pages/3_urop_projects.py", title="Research Projects", icon=":material/devices:")
club_page = st.Page("pages/4_club_projects.py", title="Club Projects", icon=":material/groups:")
resume_page = st.Page("pages/5_resume.py", title="Resume", icon=":material/article:")
parser_page = st.Page("pages/6_parser.py", title="Parser", icon=":material/article:")
pg = st.navigation([me_page, class_page, urop_page, club_page, resume_page, parser_page])
st.set_page_config(page_title="Projects", page_icon=":material/edit:")
pg.run()

# st.sidebar.success("Select a demo above.")

# st.title("Projects")

# Add a selectbox to the sidebar:
# add_selectbox = st.sidebar.selectbox(
#     'Project Type',
#     ('Class', 'Club', 'Research (UROP)')
# )

# if add_selectbox == 'Class':
#     st.subheader('6.104 - Software Design')
