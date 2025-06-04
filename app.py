import streamlit as st
import pandas as pd
import altair as alt

# --- CONFIG ---
main_color = "#3FAFEA"
st.set_page_config(page_title="UNICEF Donations", layout="centered")
st.title("UNICEF Donations Dashboard")

# --- INTRO TEXT ---
st.markdown("""
### 🇬🇧 About this Dashboard  
This dashboard provides an overview of donation data collected by UNICEF Slovakia.  
It allows you to explore trends in monthly donations, compare campaigns, and analyze donor behavior.  
You can also upload your own CSV file to explore donations from a specific time period.

### 🇸🇰 O tomto prehľade  
Tento prehľad zobrazuje údaje o daroch získaných UNICEF Slovensko.  
Umožňuje vám sledovať vývoj mesačných príspevkov, porovnať úspešnosť kampaní a analyzovať správanie darcov.  
Môžete nahrať aj vlastný CSV súbor, napríklad s dátami z konkrétneho mesiaca.

---
""")


# --- LOAD DATA ---
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file, sep=";")

    # Rename columns to English
    df.columns = [
        "Organization", "Campaign", "DonationDate", "FirstName", "LastName",
        "AmountEUR", "Frequency", "PaymentVS", "PaymentStatus", "Email",
        "PaymentGateway", "PaymentMethod", "IsAnonymous",
        "AltLinkName", "Source", "DonorType"
    ]

    # Convert DonationDate
    df["DonationDate"] = pd.to_datetime(df["DonationDate"], format="%d.%m.%Y %H:%M:%S")

    # Convert AmountEUR to numeric
    df["AmountEUR"] = pd.to_numeric(df["AmountEUR"], errors="coerce")

    # Map Slovak "IsAnonymous" values to boolean
    df["IsAnonymous"] = df["IsAnonymous"].map({"Áno": True, "Nie": False})

    return df


uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # All your data processing and charting code goes here...
    st.success("File successfully uploaded and processed.")
    
    # --------------------
    # DASHBOARD VISUALS
    if not df.empty:
        # --- Monthly Donations ---
        monthly_donations = df.set_index("DonationDate")["AmountEUR"].resample("ME").sum()
        monthly_donations.index = monthly_donations.index.strftime('%Y-%m')
        st.subheader("📅 Total Donation Amount by Month")
        st.bar_chart(monthly_donations)

        # --- Top Campaigns ---
        campaign_totals = df.groupby("Campaign")["AmountEUR"].sum().sort_values(ascending=False)
        top_5 = campaign_totals.head(5).sort_values()  # ascending=True for horizontal bar sort

        st.subheader("🏆 Top 5 Campaigns by Donation Amount")
        top_chart = alt.Chart(top_5.reset_index()).mark_bar(color=main_color).encode(
            x=alt.X("AmountEUR:Q", title="Total Donations (€)"),
            y=alt.Y("Campaign:N", sort="-x", title="Campaign"),
            tooltip=["Campaign", "AmountEUR"]
        ).properties(height=200)
        st.altair_chart(top_chart, use_container_width=True)

        # --- Bottom Campaigns ---
        bottom_5 = campaign_totals.tail(5).sort_values()  # ascending=True for horizontal bar sort

        st.subheader("📉 Bottom 5 Campaigns by Donation Amount")
        bottom_chart = alt.Chart(bottom_5.reset_index()).mark_bar(color=main_color).encode(
            x=alt.X("AmountEUR:Q", title="Total Donations (€)"),
            y=alt.Y("Campaign:N", sort="-x", title="Campaign"),
            tooltip=["Campaign", "AmountEUR"]
        ).properties(height=200)
        st.altair_chart(bottom_chart, use_container_width=True)

        # --- Frequency Pie Chart ---
        st.subheader("⏱️ Donation Frequency Distribution")
        freq_counts = df["Frequency"].value_counts().reset_index()
        freq_counts.columns = ["Frequency", "Count"]
        pie = alt.Chart(freq_counts).mark_arc(innerRadius=50).encode(
            theta="Count",
            color=alt.Color("Frequency", scale=alt.Scale(range=[main_color, "#ddd"])),
            tooltip=["Frequency", "Count"]
        ).properties(width=300, height=300)
        st.altair_chart(pie, use_container_width=True)

        # --- Donor Type Visuals ---
        col1, col2 = st.columns(2)

        with col1:
            donor_counts = df["DonorType"].value_counts()
            st.subheader("👥 Number of Donations by Donor Type")
            st.bar_chart(donor_counts)

        with col2:
            donation_sums = df.groupby("DonorType")["AmountEUR"].sum().sort_values(ascending=False)
            st.subheader("💶 Total Donation Amount by Donor Type")
            st.bar_chart(donation_sums)
            
        # --- RFM Analysis ---
        df = df[df['PaymentStatus'] == 'Úspešná']
        today = df['DonationDate'].max() + pd.Timedelta(days=1)

        rfm = df.groupby('Email').agg({
            'DonationDate': lambda x: (today - x.max()).days,
            'Email': 'count',
            'AmountEUR': 'sum'
        }).rename(columns={
            'DonationDate': 'Recency (days)',
            'Email': 'Frequency',
            'AmountEUR': 'Monetary (€)'
        }).reset_index()

        # Display in Streamlit
        st.header("📊 RFM Analysis (Recency, Frequency, Monetary)")

        st.write("""
        This table shows how recently each donor donated (Recency), how often they donated (Frequency),
        and how much they donated in total (Monetary).
        """)

        st.dataframe(rfm.sort_values(by='Monetary (€)', ascending=False), use_container_width=True)


    else:
        st.warning("No data loaded. Please upload a CSV file or ensure the data is correctly formatted.")

else:
    st.info("Please upload a CSV file to see the dashboard.")

