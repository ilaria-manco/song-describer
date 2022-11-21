import streamlit as st


def get_trimmed_audio_element(audio_url: str, max_duration: int = 120):
    html = """
    <audio controls style="width: 100%;">audio not supported</audio>
    <script src="https://cdn.jsdelivr.net/npm/audiobuffer-to-wav@1.0.0/index.js"></script>
    <script defer>
      const audio = document.querySelector('audio');
      const url = "{audio_url}";
    
      const sampleRate = 44100;
    
      async function getAudio() {{
        try {{
          const offlineCtx = new(window.OfflineAudioContext || window.webkitOfflineAudioContext)(2, sampleRate * 40, 44100);

          let r = await fetch(url);
          let buffer = await r.arrayBuffer();
          let decodedData = await offlineCtx.decodeAudioData(buffer)
          // console.log(decodedData.duration, decodedData.numberOfChannels)
          let frameCount = sampleRate * {max_duration};
          if (decodedData.length > frameCount) {{
            let twoMinutesBuffer = offlineCtx.createBuffer(decodedData.numberOfChannels, frameCount, offlineCtx.sampleRate);
            for (let channel = 0; channel < twoMinutesBuffer.numberOfChannels; channel++) {{
              twoMinutesBuffer.copyToChannel(decodedData.getChannelData(channel), channel);
            }}
            decodedData = twoMinutesBuffer;
          }}
          let wav = audioBufferToWav(decodedData);
          let blob = new Blob([new DataView(wav)], {{
            type: 'audio/wav'
          }});

          let objectUrl = URL.createObjectURL(blob);
          audio.src = objectUrl;
        }} catch (e) {{
          // console.error(e.message);
          const para = document.createElement('p');
          para.textContent = 'Your browser is not supported!';
          document.body.appendChild(para);
        }}
      }}

      getAudio();
    </script>
    """.format(audio_url=audio_url, max_duration=max_duration)
    return st.components.v1.html(html, height=75)
