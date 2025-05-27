import pandas as pd
def run(input_data):
    df = pd.read_csv("data.csv")
    record = df[df["Project_ID"] == input_data["project_id"]].iloc[0]
    return {"variance": record["Variance"]}