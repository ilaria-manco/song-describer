import streamlit as st

FAQS_TEXT = """
    #####  What is Song Describer?
    Song Describer is a web application built in [Streamlit](https://streamlit.io/), designed as a tool to crowdsource text descriptions (captions) of Creative Commons-licenced music. It is part of a research effort to collect and release the first public dataset of music captions. 
    
    ##### Who can contribute?
    Participation is open to anyone above the age of 18 with access to the internet. We particularly encourage you to participate if you’re comfortable reading and writing in English and are a music enthusiast.

    ##### How can I contribute?
    You will be asked to listen to some music and write a new description for it (Annotation) or evaluate an existing one (Evaluation). Each task takes only a few minutes. You can complete either task as many times as you'd like. And once you're done, tell a friend to tell a friend!

    #####  Why should I participate?
    Do you like music? Do you like science? Do you want to help us understand how people describe music and how machines can understand and describe music more like people? If the answer to any of these questions is yes, you’ve found a good reason to participate!

    ##### What information will you be collecting?
    We only collect the data you provide in your answers, alongside date and time information. We do NOT collect any personal data and have no way of identifying you. Please remember to never input any information which may be used to identify you in any of your text answers.

    ##### How will the data be used?
    All the data collected through Song Describer will be analysed, cleaned and processed as suitable, before being released as a public dataset under the [Creative Commons 4.0 CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/) licence. It will be deposited on the open-access repository [Zenodo](https://zenodo.org/) and will be freely available for anyone to download.

    ##### What is a music caption?
    A caption is a short piece of text that describes a piece of media, often a picture or video. When we talk about *music* captions, we refer to this kind of text describing the content of a music recording.

    ##### Why are we collecting music captions?
    Describing music is challenging, both for humans and machines. There is a wealth of research in developing machine listening systems that are able to understand and describe music. Such systems aim to enhance the listener experience, for example, by providing a way to search through vast catalogues and discover new music.
    
    Many of the current machine listening systems are able to learn correspondences between audio signals and categorical labels, but they lack the flexibility and expressivity to describe music with natural language, which humans routinely use to express their musical preference, communicate listening experiences, give music recommendations and more.
    
    Our goal is therefore to promote multimodal research which combines machine listening with natural language processing by providing open data to the research community.

    ##### Who are we?
    We are a team of researchers from the [Centre for Digital Music](https://c4dm.eecs.qmul.ac.uk/) (Queen Mary University of London) and the [Music Technology Group](https://www.upf.edu/web/mtg) (Pompeu Fabra Barcelona) with a shared interest for machine listening and music. The core members of our team are Ilaria Manco, Benno Weck, Philip Tovstogan, Dmitry Bogdanov and Minz Won.

    ##### Who can I contact if I have any questions?
    
    If you’d like to know more about the project or have any questions or feedback, please get in touch with Ilaria Manco: [i.manco@qmul.ac.uk](mailto:i.manco@qmul.ac.uk).

    If you have a complaint that you feel you cannot discuss with the researchers, contact the Queen Mary Research Ethics Facilitators by e-mail: [research-ethics@qmul.ac.uk](mailto:research-ethics@qmul.ac.uk). When contacting the Research Ethics Facilitators, please provide the following: The study title, description of the study and QMERC reference number (where possible), the researcher(s) involved, and details of the complaint you wish to make.
   """


def show():
    st.header(
        """
        ❓ FAQs
        """
    )

    st.write(FAQS_TEXT)


if __name__ == "__main__":
    show()
