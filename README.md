# ChannelFetch

ChannelFetch is a compact agent for finding and comparing channels relevant to your query by using the YouTube Data API and OpenAI’s SDK to support both data retrieval and agentic conversation flow.

### How is it different from ChatGPT alone?

It extracts data directly from YouTube Data API.

### How is it different from the default YouTube search?

It does not only showing trending videos but gives you info about the channel it comes from.
For example, if you are looking for channels about yoga, the agent will tell you whether the video comes from a source with a focus on traditional practices or on alternative modern approaches.
It provides you with links to the relevant channels and gives a short summary based on their descriptions.

### 💬 What you can do with Channel Fetch:
- Get a YouTube channels selection with a summary. Try asking "Find channels about traveling".
- Get quick overviews of a channel's content from video titles, for example, "What is this channel about?"
- Run regular searches like "video tips for baking"
- Ask the model simple questions in chat format

## License

This project is licensed under the MIT License. If you use it in your own work, please give credit to the author  
by including the following attribution:
Copyright (c) 2025 Liubov Nesterenko

## Installation

Clone the repository and install the dependencies:

```
git clone https://github.com/NeLyu/channel_fetch.git
cd channel_fetch
pip install -r requirements.txt
```

### For the CLI version:
- Get a [Google Data API key](https://developers.google.com/youtube/v3/getting-started?utm_source=chatgpt.com)
- Get an OpenAI API key

### For the full version:
- Register a Google app for authentication
- Set up a Redis database

## 🚀 Usage

You can try ChannelFetch in two ways:

### 1. 💬 Web App: 
Run it instantly on Streamlit → [ChannelFetch on Streamlit](https://channel-fetch.streamlit.app/)

### 2. Command Line Interface (CLI):
Fastest way to run it locally ```python3 -m cli.cfetch_cli```


### 👤 Author

**Liubov Nesterenko** | nesterenko.liuba@gmail.com | [LinkedIn page](https://www.linkedin.com/in/liubov-nesterenko-851b4474/)