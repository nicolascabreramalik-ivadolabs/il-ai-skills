import os
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

# 1. Setup & Security
load_dotenv()  # Loads your API key from .env
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def run_ab_analysis(data_path):
    # 2. Load the "Skill" and "Methodology"
    skill_instructions = load_file(".claude/skills/ab_test_specialist.md")
    methodology = load_file("docs/templates/AB_Analysis_Methodology.md")
    
    # 3. Load the actual data:
    df = pd.read_csv(data_path)
    data_summary = df.describe().to_string()
    raw_data_snippet = df.head(10).to_string()

    # 4. Construct the Prompt
    prompt = f"""
    Using the following methodology and instructions, analyze this dataset.
    
    <methodology>
    {methodology}
    </methodology>
    
    <instructions>
    {skill_instructions}
    </instructions>
    
    <data_summary>
    {data_summary}
    </data_summary>
    
    <data_snippet>
    {raw_data_snippet}
    </data_snippet>
    
    Please provide the final analysis as specified in the 'Deliverable Format'.
    """

    # 5. Execute API Call
    print("Sending analysis request to Claude...")
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2000,
        system="You are a specialized A/B Test Analyst. Stay strictly within the provided methodology.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # 6. Save Result to /output
    output_filename = f"output/analysis_{os.path.basename(data_path).replace('.csv', '.md')}"
    with open(output_filename, 'w') as f:
        f.write(response.content[0].text)
    
    print(f"Analysis complete. Results saved to {output_filename}")

if __name__ == "__main__":
    # Test it with a sample file once available
    sample_data = "docs/raw/sample_test_data.csv" 
    if os.path.exists(sample_data):
        run_ab_analysis(sample_data)
    else:
        print(f"Waiting for data... Please place a CSV at {sample_data}")