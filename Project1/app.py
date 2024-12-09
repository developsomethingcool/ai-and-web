# Importing required modules
import streamlit as st  # For building the web application interface
from openai import OpenAI  # To interact with OpenAI API
import os  # For handling environment variables
from dotenv import load_dotenv  # To load environment variables from a .env file
import openai  # OpenAI library (redundant, can use just 'OpenAI')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

# Load API key and other environment variables from "key.env"
load_dotenv(dotenv_path="key.env")

# Initialize OpenAI client using the API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def init_session_state():
    """
    Initialize default values in Streamlit's session state.
    Ensures variables are set up and available throughout the app.
    """
    defaults = {
        "game": None,
        "stats": {
            "games_played": 0,
            "games_won": 0,
            "total_guesses": 0,
            "guesses_per_game": [],
            "all_relevance_scores": []  # Track relevance scores for all games
        },
        "guess_attempts": 0,
        "win": False,
        "loading": False,
        "game_over": False,
        "relevance_scores": [],  # Track relevance scores for the current game
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def fetch_animal_and_clues():
    """
    Fetches a random animal and three clues using the OpenAI API.
    Returns the animal name and a list of clues.
    """
    try:
        # API request to generate an animal and its clues
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Model specification
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a random animal and three unique, easy-to-understand clues about it. "
                        "Respond in this format exactly:\n"
                        "Animal: <animal_name>, Clues: <clue_1>, <clue_2>, <clue_3>"
                    ),
                },
                {"role": "user", "content": "Respond only in format: Animal: <name>, Clues: <clue1>, <clue2>, <clue3>"},
            ],
            temperature=0.7,  # Adds randomness to the output
        )

        # Extract the content from the API response
        result = response.choices[0].message.content.strip()

        # Validate response format to ensure it contains the required fields
        if "Animal:" not in result or "Clues:" not in result:
            raise ValueError("Invalid API response format")

        # Parse animal name and clues
        animal, clues = result.split("Animal:")[1].strip().split(", Clues:")
        return animal.strip().lower(), [clue.strip() for clue in clues.split(",")]

    except ValueError as ve:
        # Handle invalid response format
        st.warning("We couldn't fetch a new animal for you right now. Please try again in a few moments.")
        st.error(f"Error details: {str(ve)}")
        return None, None

    except Exception as e:
        # Handle other errors (e.g., API failures)
        st.error(f"Error: {str(e)}")
        return None, None

def start_new_game():
    st.session_state.loading = True
    animal, clues = fetch_animal_and_clues()
    st.session_state.loading = False

    if animal and clues:
        st.session_state.game = {"target": animal, "clues": clues, "attempts": 1}
        st.session_state.guess_attempts = 0
        st.session_state.win = False
        st.session_state.relevance_scores = []  # Reset relevance scores
        st.session_state.game_over = False
    else:
        st.error("Failed to start game. Please try again.")

def handle_guess(guess):
    """
    Handles the user's guess, checks if it matches the target animal,
    fetches relevance score for every guess (correct or incorrect),
    and updates session state accordingly.
    """
    if not guess.strip():
        st.warning("Please enter a guess.")
        return

    game = st.session_state.game
    guess = guess.lower().strip()

    # Increment stats for total guesses
    st.session_state.stats["total_guesses"] += 1
    st.session_state.guess_attempts += 1

    # Fetch relevance score for every guess
    relevance_score = get_relevance_score(guess)
    st.session_state.relevance_scores.append(relevance_score)

    # Update cumulative relevance scores immediately
    st.session_state.stats["all_relevance_scores"].append(relevance_score)

    if guess == game["target"]:
        st.balloons()
        st.success(f"🎉 Correct! The animal is *{game['target']}*.")

        # Update cumulative stats
        st.session_state.stats["games_played"] += 1
        st.session_state.stats["games_won"] += 1
        st.session_state.stats["guesses_per_game"].append(st.session_state.guess_attempts)

        # End the game
        st.session_state.game = None
        st.session_state.relevance_scores = []  # Reset relevance scores for the next game
    else:
        # Handle incorrect guesses and game over logic
        if game["attempts"] >= 5 and st.session_state.guess_attempts >= 5:
            st.error(f"Game Over! The animal was *{game['target']}*.")

            # Update cumulative stats
            st.session_state.stats["games_played"] += 1
            st.session_state.stats["guesses_per_game"].append(st.session_state.guess_attempts)

            # End the game
            st.session_state.win = False
            st.session_state.game = None
            st.session_state.relevance_scores = []  # Reset relevance scores for the next game
        else:
            st.info(f"Relevance Score: {relevance_score}/10")
            st.warning("Not quite! Try again or request another hint.")


def play_page():
    """
    Displays the game interface, including clues, input fields, and control buttons.
    """
    # Custom CSS styling for the game interface
    st.markdown(
        """
        <style>
            .header {
                background-color: #ffa500;
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5em;
                margin: 0;
            }
            .header p {
                margin: 5px 0 0 0;
                font-size: 1.2em;
                font-style: italic;
            }
            .stButton > button {
                background-color: #ffa500 !important;
                color: white !important;
                width: 200px;
                height: 50px;
                font-size: 1.1em;
                border-radius: 10px;
                margin: 10px 0;
            }
            .custom-clue {
                width: 90%;
                max-width: 800px;
                padding: 15px;
                font-size: 1em;
                margin: 10px auto;
                background-color: #003366;
                color: white;
                border-radius: 10px;
                text-align: left;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display header section
    st.markdown(
        """
        <div class="header">
            <h1>🐾 Animal Guessing Game 🐾</h1>
            <p>Try to guess the animal based on the clues!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Play the game!")
    st.markdown("Try to guess the animal based on the clues below!")
    st.markdown("When the game is over, press any button to get to Menu!")


    game = st.session_state.game  # Access the current game state

    if game is None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🐾 Start New Game"):
                start_new_game()
        return

    # Display available clues based on the number of attempts
    st.write("### Clues:")
    for i in range(game["attempts"]):
        st.markdown(f"<div class='custom-clue'>Clue {i + 1}: {game['clues'][i]}</div>", unsafe_allow_html=True)

    if not st.session_state.win:
        # Show input fields and buttons for guessing and game control
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.session_state.game is not None:
                # "Give up" button functionality
                if st.button("Give up?", key="give_up_button"):
                    st.error(f"❌ You lose! The correct answer was *{st.session_state.game['target']}*.")
                    st.session_state.stats["games_played"] += 1
                    st.session_state.stats["guesses_per_game"].append(st.session_state.guess_attempts)
                    st.session_state.win = False
                    st.session_state.game_over = True
                    st.session_state.game = None
                    #st.rerun()
            else:
                # Restart option after game over
                if st.button("🐾 Start New Game", key="start_new_game_after_game_over"):
                    start_new_game()

            with st.form(key="guess_form"):
                # Input form for guesses
                guess = st.text_input("Your guess:", key="guess_input")
                submit = st.form_submit_button("Guess")
                if submit:
                    handle_guess(guess)

            if not st.session_state.win and game["attempts"] < 3:
                # Option to show another hint
                if st.button("🔄 Show Another Hint", key="hint_button"):
                    game["attempts"] += 1
    else:
        # Restart button after winning
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🐾 Start New Game", key="start_new_game_after_win"):
                start_new_game()

def stats_page():
    """
    Displays game statistics, including games played, games won, average guesses,
    guesses per game, and cumulative relevance score statistics.
    """
    st.title("📊 Game Statistics")
    stats = st.session_state.stats

    # Display overall metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Games Played", stats["games_played"])
    with col2:
        st.metric("Games Won", stats["games_won"])
    with col3:
        avg_guesses = stats["total_guesses"] / max(stats["games_played"], 1)
        st.metric("Avg Guesses/Game", f"{avg_guesses:.1f}")

    # Guesses Per Game Chart
    if stats["games_played"] > 0 and stats["guesses_per_game"]:
        st.subheader("📈 Guesses Per Game")
        
        # Prepare data for bar chart
        data = pd.DataFrame({
            'Game Number': range(1, stats["games_played"] + 1),
            'Guesses': stats["guesses_per_game"]
        })

        # Use matplotlib for a customizable bar chart
        plt.figure(figsize=(8, 5))
        colors = ['red', 'green', 'blue', 'purple', 'orange'] * (len(data) // 5 + 1)
        plt.bar(data['Game Number'], data['Guesses'], color=colors[:len(data)])
        plt.title('Guesses Per Game')
        plt.xlabel('Game Number')
        plt.ylabel('Number of Guesses')
        plt.xticks(range(1, stats["games_played"] + 1))
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Show the guesses plot in Streamlit
        st.pyplot(plt)
    else:
        st.info("No games played yet! Play a game to see guesses statistics.")

    # Cumulative Relevance Scores Chart
    all_scores = stats["all_relevance_scores"]
    if all_scores:
        st.subheader("🔍 Cumulative Relevance Scores")
        avg_relevance = sum(all_scores) / len(all_scores)
        st.metric("Avg Relevance Score (All Games)", f"{avg_relevance:.1f}")

        relevance_data = pd.DataFrame({
            "Guess Number": range(1, len(all_scores) + 1),
            "Relevance Score": all_scores,
        })

        # Plot relevance scores with varying colors based on score
        colors = ['green' if score == 10 else 'orange' if score >= 5 else 'red' for score in all_scores]

        plt.figure(figsize=(10, 6))
        plt.bar(relevance_data["Guess Number"], relevance_data["Relevance Score"], color=colors)
        plt.title("Cumulative Relevance Scores Across All Games")
        plt.xlabel("Guess Number")
        plt.ylabel("Relevance Score")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(plt)
    else:
        st.info("No relevance scores available. Start guessing to see statistics.")

def get_relevance_score(guess):
    """
    Fetch relevance score for the user's guess using OpenAI's API.
    Returns a score between 1 (irrelevant) and 10 (highly relevant).
    """
    try:
        # API request to evaluate relevance
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the correct model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that evaluates the relevance of guesses in an animal guessing game."},
                {"role": "user", "content": f"Rate the relevance of this guess: '{guess}' in the context of guessing an animal. Provide a score between 1 (irrelevant) and 10 (highly relevant). Only provide the score."}
            ],
            temperature=0.7,
        )
        # Extract the score from the response
        score = int(response.choices[0].message.content.strip())
        return max(1, min(10, score))  # Ensure the score is within 1-10
    except Exception as e:
        st.error(f"Failed to fetch relevance score: {e}")
        return 0  # Default score for errors

def main():
    """
    Main function to initialize session state and handle page navigation.
    """
    init_session_state()  # Ensure session state is initialized
    page = st.sidebar.selectbox("Navigate", ["Play", "Stats"])  # Sidebar navigation

    if page == "Play":
        play_page()  # Render the play page
    else:
        stats_page()  # Render the statistics page

# Entry point for the Streamlit app
if __name__ == "__main__":
    main()
