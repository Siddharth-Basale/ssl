import ssl
import socket
from datetime import datetime
import streamlit as st

def get_certificate_expiry_date(hostname):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            certificate = ssock.getpeercert()
            expiry_date_str = certificate['notAfter']
            expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
            return expiry_date

def check_certificate_expiry(hostnames):
    results = []
    for hostname in hostnames:
        try:
            expiry_date = get_certificate_expiry_date(hostname)
            current_date = datetime.now()
            days_until_expiry = (expiry_date - current_date).days
            
            if days_until_expiry < 30:
                results.append((hostname, days_until_expiry, True))
            else:
                results.append((hostname, days_until_expiry, False))
        except Exception as e:
            results.append((hostname, str(e), None))
    return results

# Streamlit application
def main():
    st.set_page_config(page_title="SSL Checker", page_icon="🔒")
    st.title("🔒 SSL Certificate Expiry Checker")
    st.markdown("Check if your website's SSL certificate is about to expire. Stay secure by renewing certificates on time!")

    with st.expander("ℹ️ Instructions"):
        st.write("Enter the hostnames of the websites you want to check, one per line. Click 'Check Expiry' to see the results.")

    hostnames_input = st.text_area("Enter hostnames (one per line):", "google.com\nredbus.com\nfacebook.com")

    if st.button("Check Expiry"):
        hostnames = hostnames_input.strip().split("\n")
        results = check_certificate_expiry(hostnames)

        st.subheader("Results")
        for hostname, days_until_expiry, is_expiring_soon in results:
            if is_expiring_soon is None:
                st.error(f"❌ Error checking {hostname}: {days_until_expiry}")
            elif is_expiring_soon:
                st.warning(f"⚠️ Alert: The SSL certificate for {hostname} is going to expire in {days_until_expiry} days.")
            else:
                st.success(f"✅ The SSL certificate for {hostname} is valid for {days_until_expiry} more days.")

if __name__ == "__main__":
    main()
