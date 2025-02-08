import pandas as pd

try:
    # Lees het bestand met emails
    df = pd.read_excel('dataset_email-extractor_final.xlsx')
    
    # Filter websites zonder email
    no_email_df = df[df['Email'].isna() | (df['Email'] == '')]
    
    # Sla op als CSV
    no_email_df.to_csv('websites_zonder_email.csv', index=False)
    
    print(f"Websites zonder email zijn opgeslagen in 'websites_zonder_email.csv'")
    print(f"Aantal websites zonder email: {len(no_email_df)}")

except Exception as e:
    print(f"Fout: {str(e)}") 