import ssl
import socket
from datetime import datetime
import streamlit as st
import pandas as pd


def get_certificate_details(hostname):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            certificate = ssock.getpeercert()
            expiry_date_str = certificate['notAfter']
            expiry_date = datetime.strptime(
                expiry_date_str, '%b %d %H:%M:%S %Y %Z')
            issuer = dict(x[0] for x in certificate['issuer'])
            issuer_name = issuer.get('organizationName', 'Unknown Issuer')
            return expiry_date, issuer_name


def check_certificate_expiry(hostnames):
    results = []
    for hostname in hostnames:
        try:
            expiry_date, issuer_name = get_certificate_details(hostname)
            current_date = datetime.now()
            days_until_expiry = (expiry_date - current_date).days
            percentage_expired = max(0, 100 - days_until_expiry * 100 / 365)

            if days_until_expiry < 30:
                status = "⚠️ Expiring Soon"
            else:
                status = "✅ Valid"

            results.append({
                "Hostname": hostname,
                "Expiry Date": expiry_date.strftime('%Y-%m-%d'),
                "Issuer": issuer_name,
                "Days Until Expiry": days_until_expiry,
                "Status": status,
                "Progress": percentage_expired,
            })
        except Exception as e:
            results.append({
                "Hostname": hostname,
                "Expiry Date": "N/A",
                "Issuer": "N/A",
                "Days Until Expiry": "N/A",
                "Status": f"❌ Error: {str(e)}",
                "Progress": 0,
            })
    return results


def load_urls_from_file(filename):
    try:
        with open(filename, 'r') as file:
            urls = file.read().strip().split("\n")
        return urls
    except Exception as e:
        st.error(f"Error loading {filename}: {str(e)}")
        return []

# Streamlit application


def main():
    st.set_page_config(page_title="SSL Checker", page_icon="🔒")
    st.title("🔒 SSL Certificate Expiry Checker")
    st.markdown(
        "Check if your website's SSL certificate is about to expire. Stay secure by renewing certificates on time!"
    )

    with st.expander("ℹ️ Instructions"):
        st.write("Press the button for the desired pod to check the SSL certificate expiry dates of the URLs in the corresponding text file.")

    # Buttons for each pod
    if st.button("Check US1"):
        hostnames = load_urls_from_file("pod1.txt")
        results = check_certificate_expiry(hostnames)
        display_results(results)

    if st.button("Check US2"):
        hostnames = load_urls_from_file("pod2.txt")
        results = check_certificate_expiry(hostnames)
        display_results(results)

    if st.button("Check US3"):
        hostnames = load_urls_from_file("pod3.txt")
        results = check_certificate_expiry(hostnames)
        display_results(results)

    if st.button("Check US4"):
        hostnames = load_urls_from_file("pod4.txt")
        results = check_certificate_expiry(hostnames)
        display_results(results)


def display_results(results):
    st.subheader("Results")

    # Convert results to DataFrame
    df = pd.DataFrame(results)

    # Display as DataFrame with progress bars
    st.dataframe(df.style.applymap(
        lambda val: "color: red;" if val == "⚠️ Expiring Soon" else "color: green;",
        subset=["Status"]
    ).bar(subset=["Progress"], color=["#d65f5f", "#5fba7d"], vmin=0, vmax=100))

    # Interactive chart showing distribution of expiry dates
    if not df.empty:
        df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], errors='coerce')
        st.subheader("Expiry Date Distribution")
        st.line_chart(df.set_index('Expiry Date')['Days Until Expiry'])


if __name__ == "__main__":
    main()
