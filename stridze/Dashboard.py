import asyncio

import streamlit as st
from sqlmodel import Session, select

from stridze.db import engine
from stridze.db.models import Activity, Lap, Record, User

st.set_page_config(
    page_title="Hello",
    page_icon=":running_shirt_with_sash:",
)


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
asyncio.set_event_loop(st.session_state.loop)

system = st.sidebar.radio("Unit System", ("Metric", "Imperial"), index=0)
if system is not None:
    st.session_state["system"] = system

# session = Session(engine)
# query = select(User).where(User.email == "ju.roulle@gmail.com")
# user = session.exec(query).first()
# query = select(Activity).where(Activity.user_id == user.id)
# result = session.exec(query).all()

# st.write(f"Found {len(result)} activities")
