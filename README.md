# 📦 YouTube Channel Navigator

That's a compact agent for finding and comparing channels relevant to your query by using both YouTube Data API and OpenAI reasoning.

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
Type your query: Find me channels about watercolor painting
Output:
1. Aryan verma studios
https://www.youtube.com/channel/UCP4JX0XS64fmC_wnITdPuow
2. Yasmin Art Drawing
https://www.youtube.com/channel/UCk1HnZpqA3HDHkiAbMnGFaA
3. ART and LEARN
https://www.youtube.com/channel/UC6__E-Qg9kZIDa8yMn8UDig

In the realm of watercolor painting, **Aryan Verma Studios** stands out with a broad range of tutorials covering multiple mediums, catering to both beginners and advanced artists, while focusing on inspirational content. **Yasmin Art Drawing** emphasizes a more playful approach with creative DIY projects and BFF drawings, appealing particularly to younger audiences and casual art enthusiasts. In contrast, **ART and LEARN** targets families with its simple, accessible painting tutorials suitable for beginners, showcasing a variety of techniques, including watercolor. For viewers seeking a comprehensive yet exciting approach to watercolor and art, **Aryan Verma Studios** is ideal, while **Yasmin Art Drawing** is perfect for casual, fun art projects, and **ART and LEARN** is suited for those who want to engage children in artistic activities.
```

## ✅ Requirements
* Python 3.x
* google-api-python-client
* dotenv

You will also need 
* Google Data API key, check out [this page](https://developers.google.com/youtube/v3/docs)
* OpenAI API key


### 📈 Roadmap / TODO
 
 1. Improve selection of recommended channels
 2. Add an option of longer dialogues
 3. Launch at Streamlit


### 👤 Author

**Liubov Nesterenko**, [LinkedIn page](https://www.linkedin.com/in/liubov-nesterenko-851b4474/)

📄 License
This project is licensed under the MIT License.