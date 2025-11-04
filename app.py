# app.py
import streamlit as st
import requests

st.set_page_config(page_title="Explore Artworks with MET Museum API", page_icon="🎨", layout="centered")
st.title("🎨 Explore Artworks with MET Museum API")

st.write("Search the MET Collection API and display artworks (images, title, artist, year).")

@st.cache_data(show_spinner=False)
def met_search(query, has_images=True):
    search_url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {"q": query}
    if has_images:
        params["hasImages"] = "true"
    r = requests.get(search_url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

@st.cache_data(show_spinner=False)
def get_object(object_id):
    object_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    r = requests.get(object_url, timeout=10)
    r.raise_for_status()
    return r.json()

# Sidebar controls
with st.sidebar:
    st.header("Search options")
    query = st.text_input("Search for Artworks:", placeholder="e.g. flower, Monet, sculpture")
    max_results = st.slider("How many results to show", min_value=1, max_value=12, value=6)
    use_images_only = st.checkbox("Only with images", value=True)
    st.markdown("---")
    st.markdown("Built with the MET Collection API: https://collectionapi.metmuseum.org")

if not query:
    st.info("Type a search term in the sidebar to start (e.g., 'flower', 'van gogh').")
else:
    with st.spinner("Searching the MET..."):
        try:
            search_data = met_search(query, has_images=use_images_only)
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.stop()

    total = search_data.get("total", 0)
    st.write(f"Found **{total}** results for **{query}** (showing up to {max_results})")

    object_ids = search_data.get("objectIDs") or []
    if not object_ids:
        st.warning("No object IDs returned for this search.")
        st.stop()

    # Limit results
    object_ids = object_ids[:max_results]

    # Display grid
    cols = st.columns(3)
    for i, obj_id in enumerate(object_ids):
        try:
            art = get_object(obj_id)
        except Exception as e:
            # skip problematic item
            continue

        # Choose image url (small first, fallback to primaryImage)
        image_url = art.get("primaryImageSmall") or art.get("primaryImage") or None

        col = cols[i % 3]
        with col:
            if image_url:
                st.image(image_url, use_column_width=True, caption=art.get("title", "Untitled"))
            else:
                st.write("No image available")

            st.markdown(f"**Title:** {art.get('title','Untitled')}")
            artist = art.get("artistDisplayName") or "Unknown"
            st.markdown(f"**Artist:** {artist}")
            st.markdown(f"**Date:** {art.get('objectDate','N/A')}")
            if art.get("objectURL"):
                st.markdown(f"[View on MET]({art['objectURL']})")
            st.markdown("---")

    # Optional: a selectbox to inspect single item in detail
    st.subheader("Inspect an artwork")
    inspect_id = st.selectbox("Choose objectID to inspect", options=object_ids)
    if inspect_id:
        details = get_object(inspect_id)
        st.markdown(f"### {details.get('title','Untitled')}")
        img_full = details.get("primaryImage") or details.get("primaryImageSmall")
        if img_full:
            st.image(img_full, width=500)
        st.markdown(f"**Artist:** {details.get('artistDisplayName','Unknown')}")
        st.markdown(f"**Date:** {details.get('objectDate','N/A')}")
        st.markdown(f"**Medium:** {details.get('medium','N/A')}")
        st.markdown(f"**Dimensions:** {details.get('dimensions','N/A')}")
        if details.get("objectURL"):
            st.markdown(f"[Open on MET Museum website]({details['objectURL']})")
