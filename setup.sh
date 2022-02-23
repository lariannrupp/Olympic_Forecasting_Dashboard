mkdir -p ~/.streamlit/
printf "[server]\nheadless=true\nenableCORS=false\nport=%s\n" "${PORT}" > ~/.streamlit/config.toml
