import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import json
import os

# File to store votes
VOTES_FILE = "votes.json"
POSITIONS_FILE = "positions.json"

# Initialize session state
if "voted" not in st.session_state:
    st.session_state.voted = False
    st.session_state.voter_id = str(uuid.uuid4())

# Function to load positions and candidates
def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default positions and candidates
        positions = {
            "President": ["Alex Smith", "Jamie Johnson", "Taylor Brown"],
            "Vice President": ["Morgan Lee", "Casey Wilson", "Jordan Miller"],
            "Secretary": ["Riley Davis", "Quinn Thomas", "Avery Martin"],
            "Treasurer": ["Sam Roberts", "Drew Anderson", "Sydney Clark"],
            "Academic Officer": ["Charlie Robinson", "Skyler Adams", "Harper White"],
            "Social Chair": ["Dakota Green", "Reese Murphy", "Parker Young"],
            "Sports Representative": ["Jordan Hall", "Cameron Evans", "Taylor King"],
            "Media Officer": ["Alex James", "Morgan Hayes", "Riley Carter"]
        }
        with open(POSITIONS_FILE, 'w') as f:
            json.dump(positions, f)
        return positions

# Function to save votes to file
def save_vote(voter_id, votes):
    vote_record = {
        "voter_id": voter_id,
        "timestamp": datetime.now().isoformat(),
        "votes": votes
    }
    
    # Load existing votes
    all_votes = []
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            try:
                all_votes = json.load(f)
            except json.JSONDecodeError:
                all_votes = []
    
    # Add new vote
    all_votes.append(vote_record)
    
    # Save all votes
    with open(VOTES_FILE, 'w') as f:
        json.dump(all_votes, f)

# Function to load votes
def load_votes():
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Function to count votes
def count_votes():
    votes_data = load_votes()
    positions = load_positions()
    
    results = {}
    for position, candidates in positions.items():
        results[position] = {candidate: 0 for candidate in candidates}
    
    for vote in votes_data:
        for position, candidate in vote["votes"].items():
            if position in results and candidate in results[position]:
                results[position][candidate] += 1
    
    return results

# Main app function
def main():
    st.title("Student Council Elections")
    
    # Admin mode toggle (simple password protection)
    admin_mode = False
    with st.sidebar:
        st.title("Options")
        if st.checkbox("Admin Mode"):
            password = st.text_input("Admin Password", type="password")
            if password == "admin123":  # Simple password - in a real app use more secure authentication
                admin_mode = True
                st.success("Admin mode activated")
            else:
                st.error("Incorrect password")
    
    # Admin view - results
    if admin_mode:
        show_results()
    # Voter view - voting form
    else:
        show_voting_form()

# Function to display voting form
def show_voting_form():
    positions = load_positions()
    
    if st.session_state.voted:
        st.success("Thank you for voting!")
        if st.button("Vote Again (Demo Only)"):
            st.session_state.voted = False
            st.session_state.voter_id = str(uuid.uuid4())
            st.rerun()
    else:
        st.write("Please select your candidate for each position:")
        
        with st.form("voting_form"):
            votes = {}
            for position, candidates in positions.items():
                votes[position] = st.radio(f"{position}:", candidates)
            
            submit = st.form_submit_button("Submit Vote")
            
            if submit:
                save_vote(st.session_state.voter_id, votes)
                st.session_state.voted = True
                st.rerun()

# Function to display results
def show_results():
    st.header("Election Results")
    
    results = count_votes()
    total_votes = len(load_votes())
    
    st.write(f"Total votes cast: {total_votes}")
    
    # Show results for each position
    for position, candidates in results.items():
        st.subheader(position)
        
        # Create a DataFrame for the chart
        data = pd.DataFrame({
            'Candidate': list(candidates.keys()),
            'Votes': list(candidates.values())
        })
        
        # Add percentage calculation
        if total_votes > 0:
            data['Percentage'] = (data['Votes'] / total_votes * 100).round(1)
            data['Display'] = data['Votes'].astype(str) + ' (' + data['Percentage'].astype(str) + '%)'
        else:
            data['Display'] = data['Votes'].astype(str)
        
        # Sort by votes (descending)
        data = data.sort_values('Votes', ascending=False)
        
        # Create the bar chart
        chart = st.bar_chart(data.set_index('Candidate')['Votes'])
        
        # Show the data table
        st.dataframe(data[['Candidate', 'Votes', 'Display']].set_index('Candidate'))

if __name__ == "__main__":
    main()
