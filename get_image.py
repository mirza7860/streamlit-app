import streamlit as st
import urllib.parse
import requests


def generate_image_url(query, model='flux', width=1598, height=1198, seed=35193):
    base_url = 'https://image.pollinations.ai/prompt/'
    encoded_query = urllib.parse.quote(query)
    full_url = f"{base_url}{encoded_query}?width={width}&height={height}&seed={seed}&nologo=poll&model={model}"
    return full_url


def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content
    return None


def main():
    st.title("Image Generator")

    query = st.text_input("Enter your search query:")
    model = st.selectbox("Select model type:", ['flux', 'turbo'], index=0)

    if st.button("Generate Image"):
        if query:
            image_url = generate_image_url(query, model)
            st.image(
                image_url, caption=f"Generated Image for '{query}'", use_column_width=True)

            # Download option
            image_data = download_image(image_url)
            if image_data:
                st.download_button(
                    label="Download Image",
                    data=image_data,
                    file_name=f"{query.replace(' ', '_')}.jpg",
                    mime="image/jpeg"
                )
            else:
                st.error("Failed to download the image.")
        else:
            st.error("Please enter a query.")


if __name__ == '__main__':
    main()