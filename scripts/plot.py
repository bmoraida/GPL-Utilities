import plotly.express as px
import pandas as pd

df = pd.read_csv(f"robot.csv")
fig = px.scatter_3d(
    df,
    x="x",
    y="y",
    z="z",
    color="Distance To Packoff",
    hover_name="location",
    color_continuous_scale="Bluered",
)

fig.update_layout(title=f"Robot Point Distance")
fig.show()
# fig.write_html(f"rab{rab_name}.html", auto_open=True)
