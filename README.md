# 📦 YouTube Channel Navigator

🚧 **Project Status: In Progress**

That's a compact agent for finding and comparing channels relevant to your query by using the YouTube Data API and OpenAI’s SDK to support both data retrieval and agentic conversation flow.

### How is it different from ChatGPT alone?

It extracts data directly from YouTube Data API.

### How is it different from the default YouTube search?

It does not only find trending video but gives you info about the channel it comes from.
For example, if your are looking for channels about yoga, the agent will tell you whether the video comes from a source with a focus on traditional practices or on alternative modern approaches.

Provides the user with links to the relevant channels and gives a short summary based on their descriptions.

## 🔧 Installation
```
git clone https://github.com/NeLyu/yt_channel_navigator.git
cd yt_channel_navigator
pip install -r requirements.txt
```

## 🧪 Usage
Basic example of how to run your project:
```
python src/main.py
```
Prompt example:
```
User: Give me channels about running
Extracting channels...
Selecting only relevant channels...
Summarizing...

Assistant: 1. Nick Bare
https://www.youtube.com/channel/@nickbarefitness
Treding video from the channel:
How To Run Faster For Longer
https://www.youtube.com/watch?v=uzRi7FS6iAY

2. Global Triathlon Network
https://www.youtube.com/channel/@gtn
Treding video from the channel:
Improve Your Running Speed | 3 Workouts To Make You Run Faster!
https://www.youtube.com/watch?v=RC1lrx1IhLw

3. Nico Felich
https://www.youtube.com/channel/@nico.felich
Treding video from the channel:
Running Routine for Beginners
https://www.youtube.com/watch?v=QltNOfH6Zhk

4. James Dunne
https://www.youtube.com/channel/@jamesdunne
Treding video from the channel:
RUNNING FASTER - The ONLY 3 Ways to Build Endurance
https://www.youtube.com/watch?v=28KR2wmGGh0

5. Ben Parkes
https://www.youtube.com/channel/@benparkes
Treding video from the channel:
How To Run Faster With Less Effort
https://www.youtube.com/watch?v=LMtW9uB2Z1o

The channels related to running each offer a unique perspective and content focus. Nick Bare combines fitness advice with insights from his military background and hybrid athlete lifestyle, appealing to those interested in a diverse range of athletic training, including marathons and bodybuilding. In contrast, the Global Triathlon Network focuses on triathlon training, providing expert guidance for a variety of skill levels, as well as practical tips for running faster. Meanwhile, channels like James Dunne and Nico Felich cater more to injury prevention and personal experiences in running, making them suitable for beginners and those seeking inspiration. Overall, for viewers looking to enhance their running technique and avoid injuries, channels like James Dunne and r4ucoaching offer specialized content that emphasizes strength training and injury prevention, while those aiming for a broader fitness journey may resonate more with Nick Bare and the Global Triathlon Network.

User: What are the last videos on Ben Parkes channel?What are last videos on Ben Parkes channel?
Assistant: Recently, the channel has been focusing on in-depth reviews of running shoes from various brands, highlighting both their strengths and weaknesses. Additionally, there are practical tips for runners, including how to pace runs, avoid common mistakes, and effectively prepare for marathons and half-marathons.

Check it out here https://www.youtube.com/@benparkes/videos
```

## ✅ Requirements
* Python 3.x
* google-api-python-client
* dotenv

You will also need 
* Google Data API key, check out [this page](https://developers.google.com/youtube/v3/getting-started?utm_source=chatgpt.com)
* OpenAI API key


### 📈 Roadmap / TODO
 
 1. Improve selection of recommended channels ✅
 2. Add an option of longer dialogues ✅
 3. Add more functionality for dialogues
 4. Launch at Streamlit


### 👤 Author

**Liubov Nesterenko**, [LinkedIn page](https://www.linkedin.com/in/liubov-nesterenko-851b4474/)