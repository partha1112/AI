import streamlit as st
import pandas as pd
from main import get_vector, get_similar_words

st.
(page_title="Word2Vec Explorer", page_icon="🔍", layout="centered")

st.title("🔍 Word2Vec Explorer")
st.write("Explore word vectors and similarities using our custom trained Word2Vec model.")

# Sidebar for inputs
st.sidebar.header("Input")
word_input = st.sidebar.text_input("Enter a word:", "king")

if word_input:
    try:
        # Display Vector
        st.subheader(f"Vector representation for '{word_input}'")
        vector = get_vector(word_input)
        
        # Display the vector array in a clean format
        with st.expander("Show Vector Array"):
            st.write(vector)
            
        # Display Similar Words
        st.subheader(f"Words similar to '{word_input}'")
        similar_words = get_similar_words(word_input)
        
        # Format similar words into a DataFrame for a nice table view
        df = pd.DataFrame(similar_words, columns=["Word", "Similarity Score"])
        st.dataframe(df, use_container_width=True)

        # Plotly chart (optional visualization if we want)
        st.bar_chart(data=df, x="Word", y="Similarity Score")

    except KeyError:
        st.error(f"The word '{word_input}' is not in the vocabulary. Please try another word.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
